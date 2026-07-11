from pathlib import Path

from vehicleagent.__main__ import _publish_pending_mqtt, _read_store_and_queue
from vehicleagent.store import TelemetryStore
from vehicleagent.models import VehicleState


class FakeAdapter:
    def __init__(self) -> None:
        self.state = VehicleState.now(rpm=1234)

    def read_state(self) -> VehicleState:
        return self.state


class RecordingMQTT:
    base_topic = "car/pathfinder"

    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.published: list[tuple[str, str]] = []

    def publish_message(self, topic: str, payload: str, *, retain: bool = False) -> None:
        if self.fail:
            raise RuntimeError("broker offline")
        self.published.append((topic, payload))


def test_sample_is_stored_and_queued_before_mqtt_publish(tmp_path: Path) -> None:
    store = TelemetryStore(tmp_path / "telemetry.sqlite3")
    store.connect()

    sample_id = _read_store_and_queue(
        FakeAdapter(),
        store,
        RecordingMQTT(),
        print_json=False,
    )

    latest = store.latest_sample()
    unsent_count = store.unsent_mqtt_count()
    pending_count = store.pending_outbound_count(target="mqtt")
    store.close()

    assert sample_id == 1
    assert latest is not None
    assert latest["rpm"] == 1234
    assert unsent_count == 1
    assert pending_count == 1


def test_failed_mqtt_publish_leaves_sample_and_queue_pending(tmp_path: Path) -> None:
    store = TelemetryStore(tmp_path / "telemetry.sqlite3")
    store.connect()
    mqtt = RecordingMQTT(fail=True)

    _read_store_and_queue(FakeAdapter(), store, mqtt, print_json=False)
    _publish_pending_mqtt(store, mqtt)

    unsent_count = store.unsent_mqtt_count()
    pending_count = store.pending_outbound_count(target="mqtt")
    store.close()

    assert unsent_count == 1
    assert pending_count == 1


def test_successful_mqtt_publish_marks_sample_and_queue_sent(tmp_path: Path) -> None:
    store = TelemetryStore(tmp_path / "telemetry.sqlite3")
    store.connect()
    mqtt = RecordingMQTT()

    _read_store_and_queue(FakeAdapter(), store, mqtt, print_json=False)
    _publish_pending_mqtt(store, mqtt)

    unsent_count = store.unsent_mqtt_count()
    pending_count = store.pending_outbound_count(target="mqtt")
    store.close()

    assert len(mqtt.published) == 1
    assert unsent_count == 0
    assert pending_count == 0
