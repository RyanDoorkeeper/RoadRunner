from pathlib import Path

from vehicleagent.models import VehicleState
from vehicleagent.store import TelemetryStore


def test_store_inserts_and_reads_latest_sample(tmp_path: Path) -> None:
    db_path = tmp_path / "telemetry.sqlite3"
    store = TelemetryStore(db_path)
    store.connect()

    state = VehicleState.now(rpm=1234, speed_mph=45.6, coolant_f=188.0, voltage=13.9)
    sample_id = store.insert_sample(state)
    latest = store.latest_sample()

    store.close()

    assert sample_id == 1
    assert latest is not None
    assert latest["rpm"] == 1234
    assert latest["speed_mph"] == 45.6
    assert latest["coolant_f"] == 188.0
    assert latest["voltage"] == 13.9


def test_store_tracks_unsent_mqtt_count(tmp_path: Path) -> None:
    db_path = tmp_path / "telemetry.sqlite3"
    store = TelemetryStore(db_path)
    store.connect()

    first_id = store.insert_sample(VehicleState.now(rpm=1000), sent_mqtt=False)
    store.insert_sample(VehicleState.now(rpm=1100), sent_mqtt=True)

    assert store.unsent_mqtt_count() == 1
    store.mark_sample_sent_mqtt(first_id)
    assert store.unsent_mqtt_count() == 0

    store.close()


def test_store_tracks_pending_outbound_messages(tmp_path: Path) -> None:
    db_path = tmp_path / "telemetry.sqlite3"
    store = TelemetryStore(db_path)
    store.connect()

    sample_id = store.insert_sample(VehicleState.now(rpm=1000), sent_mqtt=False)
    message_id = store.enqueue_mqtt_state(
        sample_id,
        VehicleState.now(rpm=1000),
        topic="car/pathfinder/state",
    )
    pending = store.pending_outbound_messages(target="mqtt")

    assert len(pending) == 1
    assert pending[0].id == message_id
    assert pending[0].topic == "car/pathfinder/state"
    assert store.pending_outbound_count(target="mqtt") == 1

    store.mark_outbound_sent(message_id)

    assert store.pending_outbound_count(target="mqtt") == 0
    assert store.unsent_mqtt_count() == 0

    store.close()
