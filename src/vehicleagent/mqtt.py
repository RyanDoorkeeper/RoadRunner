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
        self._connected = False
        if self.username:
            self.client.username_pw_set(self.username, self.password)

    def connect(self) -> None:
        if self._connected:
            return
        _LOGGER.info("Connecting to MQTT broker %s:%s", self.host, self.port)
        self.client.will_set(f"{self.base_topic}/availability", "offline", retain=True)
        self.client.connect(self.host, self.port, keepalive=30)
        self.client.loop_start()
        self._connected = True
        self.publish_message(f"{self.base_topic}/availability", "online", retain=True)
        if self.publish_discovery:
            publish_sensor_configs(
                self.client,
                base_topic=self.base_topic,
                vehicle_name=self.vehicle_name,
            )

    def disconnect(self) -> None:
        if not self._connected:
            return
        try:
            self.publish_message(f"{self.base_topic}/availability", "offline", retain=True)
        finally:
            self.client.loop_stop()
            self.client.disconnect()
            self._connected = False

    def publish_state(self, state: VehicleState) -> None:
        payload = json.dumps(state.to_dict(), separators=(",", ":"))
        self.publish_message(f"{self.base_topic}/state", payload)

    def publish_message(self, topic: str, payload: str, *, retain: bool = False) -> None:
        if not self._connected:
            self.connect()
        result = self.client.publish(topic, payload, retain=retain)
        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            self._connected = False
            raise RuntimeError(f"MQTT publish failed with result code {result.rc}")
        result.wait_for_publish(timeout=5.0)
        if not result.is_published():
            self._connected = False
            raise TimeoutError("Timed out waiting for MQTT state publish")
