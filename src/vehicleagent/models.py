from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any


@dataclass(slots=True)
class VehicleState:
    timestamp: datetime
    rpm: int | None = None
    speed_mph: float | None = None
    coolant_f: float | None = None
    intake_air_f: float | None = None
    voltage: float | None = None
    throttle_percent: float | None = None
    engine_load_percent: float | None = None
    fuel_level_percent: float | None = None

    @classmethod
    def now(cls, **kwargs: Any) -> "VehicleState":
        return cls(timestamp=datetime.now(UTC), **kwargs)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data

    def compact_dict(self) -> dict[str, Any]:
        """Return only populated values for cleaner terminal output and MQTT payloads."""
        return {key: value for key, value in self.to_dict().items() if value is not None}
