from __future__ import annotations

from app.memory.long_term import SQLiteMemoryStore
from app.memory.short_term import ShortTermMemory


class MemoryService:
    def __init__(self, short_term: ShortTermMemory, long_term: SQLiteMemoryStore) -> None:
        self._short_term = short_term
        self._long_term = long_term

    def add_short_term(self, user_id: str, role: str, content: str) -> None:
        self._short_term.add(user_id, role=role, content=content)

    def get_short_term(self, user_id: str) -> list[dict[str, str]]:
        return self._short_term.get(user_id)

    def add_long_term(self, user_id: str, content: str) -> None:
        self._long_term.add(user_id, content)

    def get_long_term(self, user_id: str, limit: int = 10) -> list[str]:
        return self._long_term.get(user_id, limit=limit)
