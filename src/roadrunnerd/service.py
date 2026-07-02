from __future__ import annotations

import logging
import subprocess
from dataclasses import dataclass, field
from subprocess import Popen

from .config import RoadRunnerConfig

_LOGGER = logging.getLogger(__name__)


@dataclass
class RoadRunnerService:
    config: RoadRunnerConfig
    hudiy_process: Popen[bytes] | None = field(default=None, init=False)

    def start(self) -> None:
        _LOGGER.info("Starting RoadRunner for %s", self.config.vehicle_name)
        if self.config.hudiy.autostart:
            self.launch_hudiy()

    def stop(self) -> None:
        _LOGGER.info("Stopping RoadRunner")
        self.stop_hudiy()

    def launch_hudiy(self) -> None:
        if self.hudiy_process and self.hudiy_process.poll() is None:
            _LOGGER.info("HuDiY is already running")
            return

        _LOGGER.info("Launching HuDiY: %s", " ".join(self.config.hudiy.command))
        try:
            self.hudiy_process = subprocess.Popen(self.config.hudiy.command)
        except FileNotFoundError:
            _LOGGER.error("HuDiY command not found: %s", self.config.hudiy.command[0])
            self.hudiy_process = None

    def stop_hudiy(self) -> None:
        if not self.hudiy_process or self.hudiy_process.poll() is not None:
            return

        _LOGGER.info("Stopping HuDiY")
        self.hudiy_process.terminate()
        try:
            self.hudiy_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            _LOGGER.warning("HuDiY did not stop cleanly; killing")
            self.hudiy_process.kill()
            self.hudiy_process.wait(timeout=5)
