from __future__ import annotations

import pytest

from app.agent.agent import Agent
from app.core.llm import FakeLLMClient
from app.memory.long_term import SQLiteMemoryStore
from app.memory.service import MemoryService
from app.memory.short_term import ShortTermMemory
from app.rag.service import FakeEmbeddingClient, RagService
from app.rag.vector_store import InMemoryVectorStore
from app.tools.implementations import (
    ExternalApiMockTool,
    RetrieveMemoryTool,
    SaveMemoryTool,
    VectorSearchTool,
)
from app.tools.registry import ToolRegistry


@pytest.fixture()
def memory_service(tmp_path) -> MemoryService:
    db_url = f"sqlite:///{tmp_path}/memory.db"
    short_term = ShortTermMemory(max_messages=10)
    long_term = SQLiteMemoryStore(db_url)
    return MemoryService(short_term=short_term, long_term=long_term)


@pytest.fixture()
def rag_service() -> RagService:
    store = InMemoryVectorStore()
    embeddings = FakeEmbeddingClient()
    return RagService(vector_store=store, embedding_client=embeddings)


@pytest.fixture()
def tool_registry(memory_service: MemoryService, rag_service: RagService) -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(VectorSearchTool(rag_service))
    registry.register(SaveMemoryTool(memory_service))
    registry.register(RetrieveMemoryTool(memory_service))
    registry.register(ExternalApiMockTool())
    return registry


@pytest.fixture()
def agent(memory_service: MemoryService, rag_service: RagService, tool_registry: ToolRegistry) -> Agent:
    return Agent(
        llm=FakeLLMClient(),
        tool_registry=tool_registry,
        memory_service=memory_service,
        rag_service=rag_service,
        max_steps=3,
    )
