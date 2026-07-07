from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass
from typing import Iterable

from .adapter import OBDAdapter
from .models import VehicleState

_LOGGER = logging.getLogger(__name__)
_HEX_RE = re.compile(r"^[0-9A-Fa-f]+$")
_FLOAT_RE = re.compile(r"([0-9]+(?:\.[0-9]+)?)")


class ELM327Error(RuntimeError):
    pass


@dataclass(slots=True)
class ELM327SerialAdapter(OBDAdapter):
    """Small, dependency-light ELM327 serial/RFCOMM adapter.

    This is intentionally conservative. Cheap clone adapters vary a lot, so this
    adapter favors simple commands and readable logs over maximum polling speed.
    """

    port: str
    baudrate: int = 38400
    timeout: float = 1.0
    fast: bool = True
    protocol: str = "0"

    def __post_init__(self) -> None:
        self._serial = None
        self.supported_pids_01: set[int] = set()

    def connect(self) -> None:
        try:
            import serial  # type: ignore[import-not-found]
        except ImportError as exc:
            raise ELM327Error("pyserial is required: python -m pip install pyserial") from exc

        _LOGGER.info("Opening ELM327 adapter on %s at %s baud", self.port, self.baudrate)
        self._serial = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
        time.sleep(1.5)
        self._flush()
        self._initialize()
        self.supported_pids_01 = self._read_supported_pids_01()
        if self.supported_pids_01:
            _LOGGER.info("Adapter reported %d supported mode 01 PIDs", len(self.supported_pids_01))

    def disconnect(self) -> None:
        if self._serial is not None:
            self._serial.close()
            self._serial = None

    def read_state(self) -> VehicleState:
        return VehicleState.now(
            rpm=self._read_pid_if_supported(0x0C, self._read_rpm),
            speed_mph=self._read_pid_if_supported(0x0D, self._read_speed_mph),
            coolant_f=self._read_pid_if_supported(0x05, self._read_coolant_f),
            intake_air_f=self._read_pid_if_supported(0x0F, self._read_intake_air_f),
            voltage=self._read_voltage(),
            throttle_percent=self._read_pid_if_supported(0x11, self._read_throttle_percent),
            engine_load_percent=self._read_pid_if_supported(0x04, self._read_engine_load_percent),
            fuel_level_percent=self._read_pid_if_supported(0x2F, self._read_fuel_level_percent),
        )

    def adapter_info(self) -> dict[str, str | int | bool | None]:
        return {
            "port": self.port,
            "baudrate": self.baudrate,
            "protocol": self.protocol,
            "fast": self.fast,
        }

    def _initialize(self) -> None:
        commands = [
            "ATZ",  # reset
            "ATE0",  # echo off
            "ATL0",  # linefeeds off
            "ATS0",  # spaces off
            "ATH0",  # headers off
            "ATSP" + self.protocol,  # automatic protocol by default
        ]
        for command in commands:
            response = self._command(command, delay=0.2)
            _LOGGER.debug("%s -> %s", command, response)
        if self.fast:
            # Adaptive timing is widely supported and helps avoid long waits on many adapters.
            self._command("ATAT1", delay=0.1)

    def _flush(self) -> None:
        assert self._serial is not None
        self._serial.reset_input_buffer()
        self._serial.reset_output_buffer()

    def _command(self, command: str, delay: float = 0.0) -> str:
        if self._serial is None:
            raise ELM327Error("Adapter is not connected")
        self._serial.write((command + "\r").encode("ascii"))
        self._serial.flush()
        if delay:
            time.sleep(delay)
        chunks: list[bytes] = []
        deadline = time.monotonic() + self.timeout + 1.0
        while time.monotonic() < deadline:
            chunk = self._serial.read_until(b">")
            if chunk:
                chunks.append(chunk)
                if b">" in chunk:
                    break
        raw = b"".join(chunks).decode("ascii", errors="ignore")
        cleaned = raw.replace(command, "").replace(command.lower(), "").replace(">", "")
        lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
        response = " ".join(lines).strip()
        upper = response.upper()
        if any(marker in upper for marker in ("NO DATA", "STOPPED", "SEARCHING...")):
            return ""
        if any(marker in upper for marker in ("ERROR", "UNABLE", "?")):
            _LOGGER.debug("ELM327 command %s returned %s", command, response)
            return ""
        return response

    def _pid(self, pid: str) -> list[int]:
        response = self._command(f"01{pid}")
        if not response:
            return []
        text = response.replace(" ", "").replace("\r", "").replace("\n", "")
        idx = text.find("41" + pid.upper())
        if idx == -1:
            _LOGGER.debug("PID %s response did not contain expected marker: %s", pid, response)
            return []
        data = text[idx + 4 :]
        if len(data) < 2 or not _HEX_RE.match(data):
            return []
        return [int(data[i : i + 2], 16) for i in range(0, len(data) - 1, 2)]

    def _read_supported_pids_01(self) -> set[int]:
        data = self._pid("00")
        if len(data) < 4:
            return set()
        return set(_decode_supported_pids(data[:4], base=0x00))

    def _read_pid_if_supported(self, pid: int, reader):  # noqa: ANN001, ANN202
        # If supported PID discovery fails, still try the PID. Cheap ELM clones sometimes
        # answer useful PIDs even when PID 00 support is flaky.
        if self.supported_pids_01 and pid not in self.supported_pids_01:
            return None
        return reader()

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
        return _temp_pid_to_f(self._pid("05"))

    def _read_intake_air_f(self) -> float | None:
        return _temp_pid_to_f(self._pid("0F"))

    def _read_throttle_percent(self) -> float | None:
        return _percent_pid(self._pid("11"))

    def _read_engine_load_percent(self) -> float | None:
        return _percent_pid(self._pid("04"))

    def _read_fuel_level_percent(self) -> float | None:
        return _percent_pid(self._pid("2F"))

    def _read_voltage(self) -> float | None:
        response = self._command("ATRV")
        if not response:
            return None
        match = _FLOAT_RE.search(response)
        if not match:
            return None
        return float(match.group(1))


def _decode_supported_pids(data: Iterable[int], base: int) -> list[int]:
    bytes_list = list(data)
    supported: list[int] = []
    for byte_index, value in enumerate(bytes_list):
        for bit in range(8):
            if value & (1 << (7 - bit)):
                supported.append(base + byte_index * 8 + bit + 1)
    return supported


def _temp_pid_to_f(data: list[int]) -> float | None:
    if not data:
        return None
    celsius = data[0] - 40
    return round(celsius * 9 / 5 + 32, 1)


def _percent_pid(data: list[int]) -> float | None:
    if not data:
        return None
    return round(data[0] * 100 / 255, 1)
