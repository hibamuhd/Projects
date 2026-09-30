from __future__ import annotations

import json
import uuid
from collections import Counter
from datetime import datetime, timezone

from src.storage.database import Database


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


class EventRepo:
    def __init__(self, db: Database):
        self.db = db

    def add(self, session_id: str, event_type: str, ref_id: str | None = None,
            properties: dict | None = None, is_seeded: bool = False, ts: str | None = None) -> str:
        eid = uuid.uuid4().hex
        with self.db.connect() as c:
            c.execute("INSERT INTO events VALUES (?,?,?,?,?,?,?)",
                      (eid, ts or now_iso(), session_id, event_type, ref_id,
                       json.dumps(properties or {}, default=str), int(is_seeded)))
        return eid

    def all(self, include_seeded: bool = True) -> list[dict]:
        q = "SELECT * FROM events" + ("" if include_seeded else " WHERE is_seeded = 0") + " ORDER BY ts"
        with self.db.connect() as c:
            rows = [dict(r) for r in c.execute(q)]
        for r in rows:
            r["properties"] = json.loads(r["properties"] or "{}")
        return rows

    def item_was_viewed(self, session_id: str, item_id: str) -> bool:
        with self.db.connect() as c:
            r = c.execute("SELECT 1 FROM events WHERE session_id=? AND event_type='recommendation_viewed' AND ref_id=? LIMIT 1",
                          (session_id, item_id)).fetchone()
        return r is not None


class ShortlistRepo:
    def __init__(self, db: Database):
        self.db = db

    def add(self, item_id: str, session_id: str, fit_reason: str = "") -> bool:
        """Returns True if newly inserted, False if it was already present."""
        with self.db.connect() as c:
            cur = c.execute("INSERT OR IGNORE INTO shortlist VALUES (?,?,?,?)", (item_id, now_iso(), fit_reason, session_id))
            return cur.rowcount == 1

    def remove(self, item_id: str) -> bool:
        with self.db.connect() as c:
            return c.execute("DELETE FROM shortlist WHERE item_id=?", (item_id,)).rowcount == 1

    def contains(self, item_id: str) -> bool:
        with self.db.connect() as c:
            return c.execute("SELECT 1 FROM shortlist WHERE item_id=?", (item_id,)).fetchone() is not None

    def all(self) -> list[dict]:
        with self.db.connect() as c:
            return [dict(r) for r in c.execute("SELECT * FROM shortlist ORDER BY saved_at")]


class DismissalRepo:
    def __init__(self, db: Database):
        self.db = db

    def add(self, item_id: str, session_id: str) -> bool:
        with self.db.connect() as c:
            return c.execute("INSERT OR IGNORE INTO dismissals VALUES (?,?,?)", (item_id, now_iso(), session_id)).rowcount == 1

    def contains(self, item_id: str) -> bool:
        with self.db.connect() as c:
            return c.execute("SELECT 1 FROM dismissals WHERE item_id=?", (item_id,)).fetchone() is not None

    def ids(self) -> set[str]:
        with self.db.connect() as c:
            return {r["item_id"] for r in c.execute("SELECT item_id FROM dismissals")}


class FeedbackRepo:
    def __init__(self, db: Database):
        self.db = db

    def add(self, session_id: str, item_id: str, reason: str) -> str:
        fid = uuid.uuid4().hex
        with self.db.connect() as c:
            c.execute("INSERT INTO feedback VALUES (?,?,?,?,?)", (fid, now_iso(), session_id, item_id, reason))
        return fid

    def all(self) -> list[dict]:
        with self.db.connect() as c:
            return [dict(r) for r in c.execute("SELECT * FROM feedback ORDER BY ts")]


class PreferenceRepo:
    def __init__(self, db: Database):
        self.db = db

    def set(self, key: str, value) -> None:
        with self.db.connect() as c:
            c.execute("INSERT INTO preferences VALUES (?,?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at",
                      (key, json.dumps(value), now_iso()))

    def all(self) -> dict:
        with self.db.connect() as c:
            return {r["key"]: json.loads(r["value"]) for r in c.execute("SELECT * FROM preferences")}

    def clear(self) -> None:
        with self.db.connect() as c:
            c.execute("DELETE FROM preferences")


def interaction_profile(db: Database, catalogue_by_id: dict) -> dict:
    """Evidence-only personalization signals: categories the user saved / dismissed."""
    saved, dismissed = Counter(), Counter()
    for r in ShortlistRepo(db).all():
        it = catalogue_by_id.get(r["item_id"])
        if it:
            saved[it.category] += 1
    for iid in DismissalRepo(db).ids():
        it = catalogue_by_id.get(iid)
        if it:
            dismissed[it.category] += 1
    return {"saved_categories": saved, "dismissed_categories": dismissed}
