from __future__ import annotations

import argparse
import json
import logging
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

from .adapter import OBDAdapter
from .elm327 import ELM327SerialAdapter
from .models import VehicleState
from .mqtt import MQTTPublisher
from .simulator import SimulatorAdapter
from .store import TelemetryStore

_LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="RoadRunner vehicle telemetry service")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--simulator", action="store_true", help="Use fake vehicle data")
    source.add_argument("--elm327-port", help="Serial/RFCOMM port for an ELM327 adapter")
    parser.add_argument("--elm327-baud", type=int, default=38400)
    parser.add_argument("--elm327-timeout", type=float, default=1.0)
    parser.add_argument("--elm327-protocol", default="0", help="ELM327 protocol; 0 means automatic")
    parser.add_argument("--mqtt-host", help="MQTT broker host. Omit to disable MQTT for local testing")
    parser.add_argument("--mqtt-port", type=int, default=1883)
    parser.add_argument("--base-topic", default="car/pathfinder")
    parser.add_argument("--db", type=Path, default=Path("data/roadrunner.sqlite3"))
    parser.add_argument("--interval", type=float, default=1.0)
    parser.add_argument("--once", action="store_true", help="Read one sample and exit")
    parser.add_argument("--samples", type=int, help="Read this many samples and exit")
    parser.add_argument("--print-json", action="store_true", help="Print compact JSON samples to stdout")
    parser.add_argument("--verbose", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    adapter = _build_adapter(args)
    mqtt = _build_mqtt(args)
    store = TelemetryStore(args.db)

    store.connect()
    _connect_adapter(adapter)
    _connect_mqtt(mqtt)

    sample_count = 0
    try:
        while True:
            _read_store_and_queue(adapter, store, mqtt, print_json=args.print_json)
            _publish_pending_mqtt(store, mqtt)

            sample_count += 1
            if args.once or (args.samples is not None and sample_count >= args.samples):
                break
            time.sleep(args.interval)
    except KeyboardInterrupt:
        _LOGGER.info("VehicleAgent stopped by user")
    finally:
        store.close()
        if mqtt is not None:
            mqtt.disconnect()
        adapter.disconnect()

    return 0


def _build_adapter(args: argparse.Namespace) -> OBDAdapter:
    if args.simulator:
        return SimulatorAdapter()
    return ELM327SerialAdapter(
        port=args.elm327_port,
        baudrate=args.elm327_baud,
        timeout=args.elm327_timeout,
        protocol=args.elm327_protocol,
    )


def _build_mqtt(args: argparse.Namespace) -> MQTTPublisher | None:
    if not args.mqtt_host:
        return None
    return MQTTPublisher(host=args.mqtt_host, port=args.mqtt_port, base_topic=args.base_topic)


def _connect_adapter(adapter: OBDAdapter) -> None:
    while True:
        try:
            adapter.connect()
            return
        except Exception:  # noqa: BLE001 - hardware adapters can fail in several ways
            _LOGGER.exception("Failed to connect OBD adapter; retrying in 5 seconds")
            time.sleep(5)


def _connect_mqtt(mqtt: MQTTPublisher | None) -> None:
    if mqtt is None:
        return
    try:
        mqtt.connect()
    except Exception:  # noqa: BLE001 - MQTT should not stop local logging
        _LOGGER.exception("Failed to connect MQTT; samples will be queued locally")


def _read_store_and_queue(
    adapter: OBDAdapter,
    store: TelemetryStore,
    mqtt: MQTTPublisher | None,
    *,
    print_json: bool,
) -> int:
    state = _read_state_with_reconnect(adapter)
    sample_id = store.insert_sample(state, sent_mqtt=False)
    if mqtt is not None:
        store.enqueue_mqtt_state(sample_id, state, topic=f"{mqtt.base_topic}/state")
    _log_sample(sample_id, state, print_json)
    return sample_id


def _read_state_with_reconnect(adapter: OBDAdapter) -> VehicleState:
    while True:
        try:
            return adapter.read_state()
        except Exception:  # noqa: BLE001 - keep the service alive across adapter loss
            _LOGGER.exception("Failed to read OBD state; reconnecting in 5 seconds")
            try:
                adapter.disconnect()
            except Exception:  # noqa: BLE001 - best-effort cleanup before reconnect
                _LOGGER.debug("Adapter disconnect after read failure also failed", exc_info=True)
            time.sleep(5)
            _connect_adapter(adapter)


def _publish_pending_mqtt(
    store: TelemetryStore,
    mqtt: MQTTPublisher | None,
    *,
    limit: int = 10,
) -> None:
    if mqtt is None:
        return

    for message in store.pending_outbound_messages(target="mqtt", limit=limit):
        try:
            mqtt.publish_message(message.topic, message.payload_json)
        except Exception as exc:  # noqa: BLE001 - retry later; never block local logging
            delay = _retry_delay_seconds(message.attempt_count + 1)
            next_attempt_at = datetime.now(UTC) + timedelta(seconds=delay)
            store.mark_outbound_failed(
                message.id,
                error=str(exc),
                next_attempt_at=next_attempt_at,
            )
            _LOGGER.warning(
                "Failed to publish queued MQTT message %s; retrying in %s seconds",
                message.id,
                delay,
            )
            return
        store.mark_outbound_sent(message.id)


def _retry_delay_seconds(attempt_count: int) -> int:
    return min(300, 2 ** min(attempt_count, 8))


def _log_sample(sample_id: int, state: VehicleState, print_json: bool) -> None:
    data = state.compact_dict()
    if print_json:
        print(json.dumps({"sample_id": sample_id, **data}, separators=(",", ":")), flush=True)
        return
    _LOGGER.info("sample_id=%s state=%s", sample_id, data)


if __name__ == "__main__":
    raise SystemExit(main())
