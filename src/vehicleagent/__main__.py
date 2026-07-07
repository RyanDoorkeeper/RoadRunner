from __future__ import annotations

import argparse
import json
import logging
import time
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

    adapter.connect()
    store.connect()
    if mqtt is not None:
        mqtt.connect()

    sample_count = 0
    try:
        while True:
            state = adapter.read_state()
            sent_mqtt = False
            if mqtt is not None:
                try:
                    mqtt.publish_state(state)
                    sent_mqtt = True
                except Exception:  # noqa: BLE001 - keep local logging alive even if MQTT fails
                    _LOGGER.exception("Failed to publish MQTT state; sample will remain unsent")
            sample_id = store.insert_sample(state, sent_mqtt=sent_mqtt)
            _log_sample(sample_id, state, args.print_json)

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


def _log_sample(sample_id: int, state: VehicleState, print_json: bool) -> None:
    data = state.compact_dict()
    if print_json:
        print(json.dumps({"sample_id": sample_id, **data}, separators=(",", ":")), flush=True)
        return
    _LOGGER.info("sample_id=%s state=%s", sample_id, data)


if __name__ == "__main__":
    raise SystemExit(main())
