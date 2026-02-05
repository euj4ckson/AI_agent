from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path


class SQLiteMemoryStore:
    def __init__(self, db_url: str) -> None:
        self._db_path = self._parse_sqlite_path(db_url)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def add(self, user_id: str, content: str) -> None:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                "INSERT INTO memories (user_id, content, created_at) VALUES (?, ?, ?)",
                (user_id, content, datetime.now(timezone.utc).isoformat()),
            )
            conn.commit()

    def get(self, user_id: str, limit: int = 10) -> list[str]:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute(
                "SELECT content FROM memories WHERE user_id = ? "
                "ORDER BY id DESC LIMIT ?",
                (user_id, limit),
            )
            return [row[0] for row in cursor.fetchall()]

    def _ensure_schema(self) -> None:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    @staticmethod
    def _parse_sqlite_path(db_url: str) -> Path:
        if db_url.startswith("sqlite:///"):
            return Path(db_url.replace("sqlite:///", "", 1))
        if db_url.startswith("sqlite://"):
            return Path(db_url.replace("sqlite://", "", 1))
        return Path(db_url)
