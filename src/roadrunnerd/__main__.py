from __future__ import annotations

import argparse
import logging
import signal
import time
from pathlib import Path

from .config import RoadRunnerConfig
from .service import RoadRunnerService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="RoadRunner background daemon")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/roadrunner.yaml"),
        help="Path to RoadRunner YAML config",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    config = RoadRunnerConfig.load(args.config)
    service = RoadRunnerService(config)

    running = True

    def stop(_signum: int, _frame: object) -> None:
        nonlocal running
        running = False
        service.stop()

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    service.start()
    while running:
        time.sleep(1)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
