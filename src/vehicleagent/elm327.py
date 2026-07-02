from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass

from .adapter import OBDAdapter
from .models import VehicleState

_LOGGER = logging.getLogger(__name__)
_HEX_RE = re.compile(r"^[0-9A-Fa-f ]+$")


class ELM327Error(RuntimeError):
    pass


@dataclass(slots=True)
class ELM327SerialAdapter(OBDAdapter):
    port: str
    baudrate: int = 38400
    timeout: float = 1.0
    fast: bool = True

    def __post_init__(self) -> None:
        self._serial = None

    def connect(self) -> None:
        try:
            import serial  # type: ignore[import-not-found]
        except ImportError as exc:
            raise ELM327Error("pyserial is required: python -m pip install pyserial") from exc

        _LOGGER.info("Opening ELM327 adapter on %s", self.port)
        self._serial = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
        time.sleep(1.5)
        self._flush()
        for command in ("ATZ", "ATE0", "ATL0", "ATS0", "ATH0", "ATSP0"):
            self._command(command)
        if self.fast:
            self._command("ATAT1")

    def disconnect(self) -> None:
        if self._serial is not None:
            self._serial.close()
            self._serial = None

    def read_state(self) -> VehicleState:
        rpm = self._read_rpm()
        speed = self._read_speed_mph()
        coolant = self._read_coolant_f()
        throttle = self._read_throttle_percent()
        load = self._read_engine_load_percent()
        voltage = self._read_voltage()
        return VehicleState.now(
            rpm=rpm,
            speed_mph=speed,
            coolant_f=coolant,
            voltage=voltage,
            throttle_percent=throttle,
            engine_load_percent=load,
        )

    def _flush(self) -> None:
        assert self._serial is not None
        self._serial.reset_input_buffer()
        self._serial.reset_output_buffer()

    def _command(self, command: str) -> str:
        if self._serial is None:
            raise ELM327Error("Adapter is not connected")
        self._serial.write((command + "\r").encode("ascii"))
        self._serial.flush()
        chunks: list[bytes] = []
        deadline = time.monotonic() + self.timeout + 1.0
        while time.monotonic() < deadline:
            chunk = self._serial.read_until(b">")
            if chunk:
                chunks.append(chunk)
                if b">" in chunk:
                    break
        raw = b"".join(chunks).decode("ascii", errors="ignore")
        cleaned = raw.replace(command, "").replace(">", "")
        lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
        response = " ".join(lines)
        if "NO DATA" in response.upper():
            return ""
        if "ERROR" in response.upper() or "UNABLE" in response.upper():
            _LOGGER.debug("ELM327 command %s returned %s", command, response)
            return ""
        return response

    def _pid(self, pid: str) -> list[int]:
        response = self._command(f"01{pid}")
        if not response:
            return []
        text = response.replace(" ", "")
        idx = text.find("41" + pid.upper())
        if idx == -1:
            return []
        data = text[idx + 4 :]
        if len(data) < 2 or not _HEX_RE.match(data):
            return []
        return [int(data[i : i + 2], 16) for i in range(0, len(data) - 1, 2)]

    def _read_rpm(self) -> int | None:
        data = self._pid("0C")
        if len(data) < 2:
            return None
        return int(((data[0] * 256) + data[1]) / 4)

    def _read_speed_mph(self) -> float | None:
        data = self._pid("0D")
        if not data:
            return None
        kmh = data[0]
        return round(kmh * 0.621371, 1)

    def _read_coolant_f(self) -> float | None:
        data = self._pid("05")
        if not data:
            return None
        celsius = data[0] - 40
        return round(celsius * 9 / 5 + 32, 1)

    def _read_throttle_percent(self) -> float | None:
        data = self._pid("11")
        if not data:
            return None
        return round(data[0] * 100 / 255, 1)

    def _read_engine_load_percent(self) -> float | None:
        data = self._pid("04")
        if not data:
            return None
        return round(data[0] * 100 / 255, 1)

    def _read_voltage(self) -> float | None:
        response = self._command("ATRV")
        if not response:
            return None
        match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*V", response, re.IGNORECASE)
        if not match:
            return None
        return float(match.group(1))
