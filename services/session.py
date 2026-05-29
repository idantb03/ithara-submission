import json
from datetime import datetime

import aiosqlite

from models.session import BookingSession


class SessionStore:
    def __init__(self, db_path: str = "sessions.db") -> None:
        self.db_path = db_path

    async def init(self) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    phone TEXT NOT NULL,
                    step TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            await db.commit()

    async def save(self, session: BookingSession) -> None:
        payload = json.dumps(session.model_dump(mode="json"))
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO sessions (session_id, phone, step, payload, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    phone = excluded.phone,
                    step = excluded.step,
                    payload = excluded.payload,
                    updated_at = excluded.updated_at
                """,
                (session.session_id, session.phone, session.step, payload, datetime.now().isoformat()),
            )
            await db.commit()

    async def get(self, session_id: str) -> BookingSession | None:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT payload FROM sessions WHERE session_id = ?", (session_id,))
            row = await cursor.fetchone()
            if not row:
                return None
            return BookingSession(**json.loads(row[0]))
