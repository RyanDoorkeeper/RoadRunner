from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
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

CREATE TABLE IF NOT EXISTS outbound_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    target TEXT NOT NULL,
    topic TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    sample_id INTEGER,
    created_at TEXT NOT NULL,
    next_attempt_at TEXT,
    attempt_count INTEGER NOT NULL DEFAULT 0,
    last_error TEXT,
    sent_at TEXT,
    FOREIGN KEY(sample_id) REFERENCES samples(id)
);

CREATE INDEX IF NOT EXISTS idx_outbound_queue_pending
    ON outbound_queue(target, sent_at, next_attempt_at, id);

CREATE TABLE IF NOT EXISTS metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


@dataclass(frozen=True, slots=True)
class OutboundMessage:
    id: int
    target: str
    topic: str
    payload_json: str
    sample_id: int | None
    attempt_count: int


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

    def enqueue_mqtt_state(self, sample_id: int, state: VehicleState, *, topic: str) -> int:
        if self.connection is None:
            raise RuntimeError("TelemetryStore is not connected")
        payload = json.dumps(state.to_dict(), separators=(",", ":"))
        cursor = self.connection.execute(
            """
            INSERT INTO outbound_queue(
                target,
                topic,
                payload_json,
                sample_id,
                created_at
            ) VALUES (?, ?, ?, ?, ?)
            """,
            ("mqtt", topic, payload, sample_id, _utc_now()),
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def pending_outbound_messages(self, *, target: str, limit: int = 10) -> list[OutboundMessage]:
        if self.connection is None:
            raise RuntimeError("TelemetryStore is not connected")
        rows = self.connection.execute(
            """
            SELECT id, target, topic, payload_json, sample_id, attempt_count
            FROM outbound_queue
            WHERE target = ?
              AND sent_at IS NULL
              AND (next_attempt_at IS NULL OR next_attempt_at <= ?)
            ORDER BY id
            LIMIT ?
            """,
            (target, _utc_now(), limit),
        ).fetchall()
        return [
            OutboundMessage(
                id=int(row["id"]),
                target=str(row["target"]),
                topic=str(row["topic"]),
                payload_json=str(row["payload_json"]),
                sample_id=int(row["sample_id"]) if row["sample_id"] is not None else None,
                attempt_count=int(row["attempt_count"]),
            )
            for row in rows
        ]

    def pending_outbound_count(self, *, target: str) -> int:
        if self.connection is None:
            raise RuntimeError("TelemetryStore is not connected")
        row = self.connection.execute(
            "SELECT COUNT(*) AS count FROM outbound_queue WHERE target = ? AND sent_at IS NULL",
            (target,),
        ).fetchone()
        return int(row["count"])

    def mark_outbound_sent(self, message_id: int) -> None:
        if self.connection is None:
            raise RuntimeError("TelemetryStore is not connected")
        row = self.connection.execute(
            "SELECT target, sample_id FROM outbound_queue WHERE id = ?",
            (message_id,),
        ).fetchone()
        if row is None:
            raise ValueError(f"Outbound message does not exist: {message_id}")

        self.connection.execute(
            "UPDATE outbound_queue SET sent_at = ?, last_error = NULL WHERE id = ?",
            (_utc_now(), message_id),
        )
        if row["target"] == "mqtt" and row["sample_id"] is not None:
            self.connection.execute(
                "UPDATE samples SET sent_mqtt = 1 WHERE id = ?",
                (int(row["sample_id"]),),
            )
        self.connection.commit()

    def mark_outbound_failed(
        self,
        message_id: int,
        *,
        error: str,
        next_attempt_at: datetime,
    ) -> None:
        if self.connection is None:
            raise RuntimeError("TelemetryStore is not connected")
        self.connection.execute(
            """
            UPDATE outbound_queue
            SET attempt_count = attempt_count + 1,
                last_error = ?,
                next_attempt_at = ?
            WHERE id = ?
            """,
            (error, next_attempt_at.astimezone(UTC).isoformat(), message_id),
        )
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


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()
