from vehicleagent.simulator import SimulatorAdapter


def test_simulator_reads_state() -> None:
    adapter = SimulatorAdapter()
    adapter.connect()
    state = adapter.read_state()
    adapter.disconnect()

    assert state.rpm is not None
    assert state.speed_mph is not None
    assert state.coolant_f is not None
    assert state.voltage is not None
