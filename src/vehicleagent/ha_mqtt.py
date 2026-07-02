from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import paho.mqtt.client as mqtt


@dataclass(frozen=True, slots=True)
class SensorSpec:
    key: str
    label: str
    unit: str | None = None
    icon: str | None = None


SENSORS: tuple[SensorSpec, ...] = (
    SensorSpec("rpm", "RPM", icon="mdi:gauge"),
    SensorSpec("speed_mph", "Speed", unit="mph"),
    SensorSpec("coolant_f", "Coolant Temperature", unit="°F"),
    SensorSpec("voltage", "Voltage", unit="V"),
    SensorSpec("throttle_percent", "Throttle", unit="%"),
    SensorSpec("engine_load_percent", "Engine Load", unit="%"),
)


def publish_sensor_configs(
    client: mqtt.Client,
    *,
    prefix: str = "homeassistant",
    base_topic: str = "car/pathfinder",
    vehicle_name: str = "Pathfinder",
    unique_prefix: str = "roadrunner_pathfinder",
) -> None:
    state_topic = f"{base_topic}/state"
    device: dict[str, Any] = {
        "identifiers": [unique_prefix],
        "name": vehicle_name,
        "manufacturer": "RoadRunner",
        "model": "Vehicle Companion",
    }

    for sensor in SENSORS:
        object_id = f"{unique_prefix}_{sensor.key}"
        topic = f"{prefix}/sensor/{object_id}/config"
        payload: dict[str, Any] = {
            "name": f"{vehicle_name} {sensor.label}",
            "unique_id": object_id,
            "state_topic": state_topic,
            "value_template": f"{{{{ value_json.{sensor.key} }}}}",
            "availability_topic": f"{base_topic}/availability",
            "device": device,
        }
        if sensor.unit:
            payload["unit_of_measurement"] = sensor.unit
        if sensor.icon:
            payload["icon"] = sensor.icon
        client.publish(topic, json.dumps(payload, separators=(",", ":")), retain=True)
