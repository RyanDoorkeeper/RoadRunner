from __future__ import annotations

import json
import logging
from dataclasses import dataclass

import paho.mqtt.client as mqtt

from .models import VehicleState

_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class MQTTPublisher:
    host: str = "localhost"
    port: int = 1883
    base_topic: str = "car/pathfinder"
    username: str | None = None
    password: str | None = None

    def __post_init__(self) -> None:
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        if self.username:
            self.client.username_pw_set(self.username, self.password)

    def connect(self) -> None:
        _LOGGER.info("Connecting to MQTT broker %s:%s", self.host, self.port)
        self.client.connect(self.host, self.port, keepalive=30)
        self.client.loop_start()

    def disconnect(self) -> None:
        self.client.loop_stop()
        self.client.disconnect()

    def publish_state(self, state: VehicleState) -> None:
        topic = f"{self.base_topic}/state"
        payload = json.dumps(state.to_dict(), separators=(",", ":"))
        self.client.publish(topic, payload, retain=False)
