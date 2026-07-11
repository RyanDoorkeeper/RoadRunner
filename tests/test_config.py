from pathlib import Path

from roadrunnerd.config import RoadRunnerConfig


def test_missing_config_uses_defaults(tmp_path: Path) -> None:
    config = RoadRunnerConfig.load(tmp_path / "missing.yaml")

    assert config.vehicle_name == "Pathfinder"
    assert config.mqtt.host == "localhost"
    assert config.hudiy.command == ["hudiy"]


def test_partial_config_keeps_default_vehicle_name(tmp_path: Path) -> None:
    config_path = tmp_path / "roadrunner.yaml"
    config_path.write_text(
        """
mqtt:
  host: homeassistant.local
""",
        encoding="utf-8",
    )

    config = RoadRunnerConfig.load(config_path)

    assert config.vehicle_name == "Pathfinder"
    assert config.mqtt.host == "homeassistant.local"
