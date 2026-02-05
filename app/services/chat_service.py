from __future__ import annotations

from app.agent.agent import Agent
from app.core.config import settings
from app.core.llm import FakeLLMClient, OllamaChatClient, OpenAIChatClient
from app.memory.long_term import SQLiteMemoryStore
from app.memory.service import MemoryService
from app.memory.short_term import ShortTermMemory
from app.rag.service import (
    FakeEmbeddingClient,
    OllamaEmbeddingClient,
    OpenAIEmbeddingClient,
    RagService,
)
from app.rag.vector_store import FaissVectorStore, InMemoryVectorStore
from app.tools.implementations import (
    ExternalApiMockTool,
    RetrieveMemoryTool,
    SaveMemoryTool,
    VectorSearchTool,
)
from app.tools.registry import ToolRegistry


_memory_service: MemoryService | None = None
_rag_service: RagService | None = None
_agent: Agent | None = None


def build_memory_service() -> MemoryService:
    short_term = ShortTermMemory(max_messages=settings.short_term_max_messages)
    long_term = SQLiteMemoryStore(settings.memory_db_url)
    return MemoryService(short_term=short_term, long_term=long_term)


def build_rag_service(use_fake: bool = False) -> RagService:
    if use_fake:
        store = InMemoryVectorStore()
        embeddings = FakeEmbeddingClient()
    elif settings.use_ollama:
        store = FaissVectorStore()
        embeddings = OllamaEmbeddingClient(
            host=settings.ollama_host,
            model=settings.ollama_embed_model,
        )
    else:
        store = FaissVectorStore()
        embeddings = OpenAIEmbeddingClient(
            api_key=settings.openai_api_key,
            model=settings.openai_embedding_model,
        )
    return RagService(vector_store=store, embedding_client=embeddings)


def build_tool_registry(memory_service: MemoryService, rag_service: RagService) -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(VectorSearchTool(rag_service))
    registry.register(SaveMemoryTool(memory_service))
    registry.register(RetrieveMemoryTool(memory_service))
    registry.register(ExternalApiMockTool())
    return registry


def build_agent(use_fake_llm: bool = False, use_fake_rag: bool = False) -> Agent:
    memory_service = build_memory_service()
    rag_service = build_rag_service(use_fake=use_fake_rag)
    tool_registry = build_tool_registry(memory_service, rag_service)
    llm = FakeLLMClient() if use_fake_llm else OpenAIChatClient(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
    )
    return Agent(
        llm=llm,
        tool_registry=tool_registry,
        memory_service=memory_service,
        rag_service=rag_service,
        max_steps=settings.agent_max_steps,
    )


def get_memory_service() -> MemoryService:
    global _memory_service
    if _memory_service is None:
        _memory_service = build_memory_service()
    return _memory_service


def get_rag_service() -> RagService:
    global _rag_service
    if _rag_service is None:
        _rag_service = build_rag_service(use_fake=settings.use_fake_rag)
    return _rag_service


def get_agent() -> Agent:
    global _agent
    if _agent is None:
        memory_service = get_memory_service()
        rag_service = get_rag_service()
        tool_registry = build_tool_registry(memory_service, rag_service)
        if settings.use_fake_llm:
            llm = FakeLLMClient()
        elif settings.use_ollama:
            llm = OllamaChatClient(
                host=settings.ollama_host,
                model=settings.ollama_chat_model,
            )
        else:
            llm = OpenAIChatClient(
                api_key=settings.openai_api_key,
                model=settings.openai_model,
            )
        _agent = Agent(
            llm=llm,
            tool_registry=tool_registry,
            memory_service=memory_service,
            rag_service=rag_service,
            max_steps=settings.agent_max_steps,
        )
    return _agent
