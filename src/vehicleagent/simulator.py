from __future__ import annotations

import math
import time

from .adapter import OBDAdapter
from .models import VehicleState


class SimulatorAdapter(OBDAdapter):
    """Fake vehicle adapter for desk development."""

    def __init__(self) -> None:
        self._started_at = time.monotonic()
        self._connected = False

    def connect(self) -> None:
        self._connected = True
        self._started_at = time.monotonic()

    def disconnect(self) -> None:
        self._connected = False

    def read_state(self) -> VehicleState:
        if not self._connected:
            raise RuntimeError("SimulatorAdapter is not connected")

        elapsed = time.monotonic() - self._started_at
        speed = max(0.0, 35.0 + 25.0 * math.sin(elapsed / 18.0))
        rpm = int(750 + speed * 42 + 250 * math.sin(elapsed / 3.0))
        coolant = min(190.0, 70.0 + elapsed * 1.2)

        return VehicleState.now(
            rpm=rpm,
            speed_mph=round(speed, 1),
            coolant_f=round(coolant, 1),
            voltage=13.9,
            throttle_percent=round(18 + 10 * math.sin(elapsed / 4.0), 1),
            engine_load_percent=round(25 + 15 * math.sin(elapsed / 8.0), 1),
        )
