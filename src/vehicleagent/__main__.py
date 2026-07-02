from __future__ import annotations

import argparse
import logging
import time

from .elm327 import ELM327SerialAdapter
from .mqtt import MQTTPublisher
from .simulator import SimulatorAdapter


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="RoadRunner vehicle telemetry service")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--simulator", action="store_true", help="Use fake vehicle data")
    source.add_argument("--elm327-port", help="Serial/RFCOMM port for an ELM327 adapter")
    parser.add_argument("--elm327-baud", type=int, default=38400)
    parser.add_argument("--mqtt-host", default="localhost")
    parser.add_argument("--mqtt-port", type=int, default=1883)
    parser.add_argument("--base-topic", default="car/pathfinder")
    parser.add_argument("--interval", type=float, default=1.0)
    parser.add_argument("--verbose", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    if args.simulator:
        adapter = SimulatorAdapter()
    else:
        adapter = ELM327SerialAdapter(port=args.elm327_port, baudrate=args.elm327_baud)

    mqtt = MQTTPublisher(host=args.mqtt_host, port=args.mqtt_port, base_topic=args.base_topic)

    adapter.connect()
    mqtt.connect()

    try:
        while True:
            state = adapter.read_state()
            mqtt.publish_state(state)
            logging.info("Published state: %s", state.to_dict())
            time.sleep(args.interval)
    except KeyboardInterrupt:
        pass
    finally:
        mqtt.disconnect()
        adapter.disconnect()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
