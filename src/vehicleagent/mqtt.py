from __future__ import annotations

import json
import logging
from dataclasses import dataclass

import paho.mqtt.client as mqtt

from .ha_mqtt import publish_sensor_configs
from .models import VehicleState

_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class MQTTPublisher:
    host: str = "localhost"
    port: int = 1883
    base_topic: str = "car/pathfinder"
    username: str | None = None
    password: str | None = None
    vehicle_name: str = "Pathfinder"
    publish_discovery: bool = True

    def __post_init__(self) -> None:
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        if self.username:
            self.client.username_pw_set(self.username, self.password)

    def connect(self) -> None:
        _LOGGER.info("Connecting to MQTT broker %s:%s", self.host, self.port)
        self.client.will_set(f"{self.base_topic}/availability", "offline", retain=True)
        self.client.connect(self.host, self.port, keepalive=30)
        self.client.loop_start()
        self.client.publish(f"{self.base_topic}/availability", "online", retain=True)
        if self.publish_discovery:
            publish_sensor_configs(
                self.client,
                base_topic=self.base_topic,
                vehicle_name=self.vehicle_name,
            )

    def disconnect(self) -> None:
        self.client.publish(f"{self.base_topic}/availability", "offline", retain=True)
        self.client.loop_stop()
        self.client.disconnect()

    def publish_state(self, state: VehicleState) -> None:
        topic = f"{self.base_topic}/state"
        payload = json.dumps(state.to_dict(), separators=(",", ":"))
        self.client.publish(topic, payload, retain=False)
