from __future__ import annotations

from collections import deque
from typing import Deque


class ShortTermMemory:
    def __init__(self, max_messages: int = 20) -> None:
        self._max_messages = max_messages
        self._store: dict[str, Deque[dict[str, str]]] = {}

    def add(self, user_id: str, role: str, content: str) -> None:
        if user_id not in self._store:
            self._store[user_id] = deque(maxlen=self._max_messages)
        self._store[user_id].append({"role": role, "content": content})

    def get(self, user_id: str) -> list[dict[str, str]]:
        return list(self._store.get(user_id, []))
