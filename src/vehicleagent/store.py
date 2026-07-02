from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .models import VehicleState


SCHEMA = """
CREATE TABLE IF NOT EXISTS samples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    payload_json TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_samples_timestamp ON samples(timestamp);
"""


class TelemetryStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.connection: sqlite3.Connection | None = None

    def connect(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.connection.executescript(SCHEMA)
        self.connection.commit()

    def close(self) -> None:
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def insert_sample(self, state: VehicleState) -> None:
        if self.connection is None:
            raise RuntimeError("TelemetryStore is not connected")
        payload = json.dumps(state.to_dict(), separators=(",", ":"))
        self.connection.execute(
            "INSERT INTO samples(timestamp, payload_json) VALUES(?, ?)",
            (state.timestamp.isoformat(), payload),
        )
        self.connection.commit()
