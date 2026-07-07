from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from .models import VehicleState


SCHEMA = """
CREATE TABLE IF NOT EXISTS samples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    rpm INTEGER,
    speed_mph REAL,
    coolant_f REAL,
    intake_air_f REAL,
    voltage REAL,
    throttle_percent REAL,
    engine_load_percent REAL,
    fuel_level_percent REAL,
    payload_json TEXT NOT NULL,
    sent_mqtt INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_samples_timestamp ON samples(timestamp);
CREATE INDEX IF NOT EXISTS idx_samples_sent_mqtt ON samples(sent_mqtt);

CREATE TABLE IF NOT EXISTS metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


class TelemetryStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.connection: sqlite3.Connection | None = None

    def connect(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self.connection.executescript(SCHEMA)
        self._migrate_samples_table()
        self.connection.commit()

    def close(self) -> None:
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def insert_sample(self, state: VehicleState, *, sent_mqtt: bool = False) -> int:
        if self.connection is None:
            raise RuntimeError("TelemetryStore is not connected")
        payload = json.dumps(state.to_dict(), separators=(",", ":"))
        cursor = self.connection.execute(
            """
            INSERT INTO samples(
                timestamp,
                rpm,
                speed_mph,
                coolant_f,
                intake_air_f,
                voltage,
                throttle_percent,
                engine_load_percent,
                fuel_level_percent,
                payload_json,
                sent_mqtt
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                state.timestamp.isoformat(),
                state.rpm,
                state.speed_mph,
                state.coolant_f,
                state.intake_air_f,
                state.voltage,
                state.throttle_percent,
                state.engine_load_percent,
                state.fuel_level_percent,
                payload,
                1 if sent_mqtt else 0,
            ),
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def latest_sample(self) -> dict[str, Any] | None:
        if self.connection is None:
            raise RuntimeError("TelemetryStore is not connected")
        row = self.connection.execute(
            "SELECT payload_json FROM samples ORDER BY id DESC LIMIT 1"
        ).fetchone()
        if row is None:
            return None
        return json.loads(row["payload_json"])

    def unsent_mqtt_count(self) -> int:
        if self.connection is None:
            raise RuntimeError("TelemetryStore is not connected")
        row = self.connection.execute("SELECT COUNT(*) AS count FROM samples WHERE sent_mqtt = 0").fetchone()
        return int(row["count"])

    def mark_sample_sent_mqtt(self, sample_id: int) -> None:
        if self.connection is None:
            raise RuntimeError("TelemetryStore is not connected")
        self.connection.execute("UPDATE samples SET sent_mqtt = 1 WHERE id = ?", (sample_id,))
        self.connection.commit()

    def _migrate_samples_table(self) -> None:
        """Add structured columns for repos created before the prototype schema.

        SQLite has limited ALTER TABLE support, so this keeps migrations simple and
        additive while the project is still in prototype stage.
        """
        assert self.connection is not None
        existing = {
            row["name"]
            for row in self.connection.execute("PRAGMA table_info(samples)").fetchall()
        }
        columns = {
            "rpm": "INTEGER",
            "speed_mph": "REAL",
            "coolant_f": "REAL",
            "intake_air_f": "REAL",
            "voltage": "REAL",
            "throttle_percent": "REAL",
            "engine_load_percent": "REAL",
            "fuel_level_percent": "REAL",
            "sent_mqtt": "INTEGER NOT NULL DEFAULT 0",
        }
        for column, column_type in columns.items():
            if column not in existing:
                self.connection.execute(f"ALTER TABLE samples ADD COLUMN {column} {column_type}")
