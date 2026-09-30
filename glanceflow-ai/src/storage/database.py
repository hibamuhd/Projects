"""SQLite persistence. One short-lived connection per operation (safe with Streamlit reruns)."""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
  event_id TEXT PRIMARY KEY, ts TEXT NOT NULL, session_id TEXT NOT NULL, event_type TEXT NOT NULL,
  ref_id TEXT, properties TEXT NOT NULL DEFAULT '{}', is_seeded INTEGER NOT NULL DEFAULT 0);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_session ON events(session_id);
CREATE TABLE IF NOT EXISTS shortlist (
  item_id TEXT PRIMARY KEY, saved_at TEXT NOT NULL, fit_reason TEXT NOT NULL DEFAULT '', session_id TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS dismissals (
  item_id TEXT PRIMARY KEY, dismissed_at TEXT NOT NULL, session_id TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS feedback (
  feedback_id TEXT PRIMARY KEY, ts TEXT NOT NULL, session_id TEXT NOT NULL, item_id TEXT NOT NULL, reason TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS preferences (key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at TEXT NOT NULL);
"""


class PersistenceError(RuntimeError):
    pass


class Database:
    def __init__(self, path: Path | str):
        self.path = str(path)
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def connect(self):
        try:
            conn = sqlite3.connect(self.path, timeout=5)
            conn.row_factory = sqlite3.Row
            try:
                yield conn
                conn.commit()
            finally:
                conn.close()
        except sqlite3.Error as e:
            raise PersistenceError(str(e)) from e

    def init(self) -> None:
        with self.connect() as c:
            c.executescript(SCHEMA)

    def clear_user_data(self, keep_seeded_events: bool = False) -> None:
        with self.connect() as c:
            if keep_seeded_events:
                c.execute("DELETE FROM events WHERE is_seeded = 0")
            else:
                c.execute("DELETE FROM events")
            for t in ("shortlist", "dismissals", "feedback", "preferences"):
                c.execute(f"DELETE FROM {t}")
