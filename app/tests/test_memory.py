from __future__ import annotations

from app.memory.long_term import SQLiteMemoryStore


def test_memory_persistence(tmp_path) -> None:
    db_url = f"sqlite:///{tmp_path}/memory.db"
    store = SQLiteMemoryStore(db_url)
    store.add("u1", "lembrar disso")
    memories = store.get("u1", limit=1)
    assert memories == ["lembrar disso"]
