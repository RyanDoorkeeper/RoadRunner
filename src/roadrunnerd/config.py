from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass(slots=True)
class MQTTConfig:
    host: str = "localhost"
    port: int = 1883
    username: str | None = None
    password: str | None = None
    base_topic: str = "car/pathfinder"


@dataclass(slots=True)
class HuDiYConfig:
    command: list[str] = field(default_factory=lambda: ["hudiy"])
    autostart: bool = False


@dataclass(slots=True)
class RoadRunnerConfig:
    vehicle_name: str = "Pathfinder"
    mqtt: MQTTConfig = field(default_factory=MQTTConfig)
    hudiy: HuDiYConfig = field(default_factory=HuDiYConfig)

    @classmethod
    def load(cls, path: Path) -> "RoadRunnerConfig":
        if not path.exists():
            return cls()

        with path.open("r", encoding="utf-8") as handle:
            raw: dict[str, Any] = yaml.safe_load(handle) or {}

        mqtt_raw = raw.get("mqtt", {}) or {}
        hudiy_raw = raw.get("hudiy", {}) or {}

        return cls(
            vehicle_name=raw.get("vehicle_name", cls.vehicle_name),
            mqtt=MQTTConfig(**mqtt_raw),
            hudiy=HuDiYConfig(**hudiy_raw),
        )
