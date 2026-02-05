from __future__ import annotations

import json
from typing import Any

from app.memory.service import MemoryService
from app.rag.service import RagService
from app.tools.base import Tool, ToolSpec


class VectorSearchTool(Tool):
    def __init__(self, rag_service: RagService) -> None:
        self._rag = rag_service
        self.spec = ToolSpec(
            name="vector_search",
            description="Busca semântica na base vetorial.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "k": {"type": "integer", "default": 3},
                },
                "required": ["query"],
            },
        )

    def run(self, arguments: dict[str, Any]) -> str:
        query = arguments.get("query", "")
        k = int(arguments.get("k", 3))
        results = self._rag.search(query, k=k)
        return "\n".join(results) or "Nenhum resultado."


class SaveMemoryTool(Tool):
    def __init__(self, memory_service: MemoryService) -> None:
        self._memory = memory_service
        self.spec = ToolSpec(
            name="save_memory",
            description="Salva memória de longo prazo para um usuário.",
            parameters={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["user_id", "content"],
            },
        )

    def run(self, arguments: dict[str, Any]) -> str:
        user_id = arguments.get("user_id", "")
        content = arguments.get("content", "")
        if not user_id or not content:
            return "Parâmetros inválidos."
        self._memory.add_long_term(user_id, content)
        return "Memória salva."


class RetrieveMemoryTool(Tool):
    def __init__(self, memory_service: MemoryService) -> None:
        self._memory = memory_service
        self.spec = ToolSpec(
            name="retrieve_memory",
            description="Recupera memórias de longo prazo de um usuário.",
            parameters={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "limit": {"type": "integer", "default": 5},
                },
                "required": ["user_id"],
            },
        )

    def run(self, arguments: dict[str, Any]) -> str:
        user_id = arguments.get("user_id", "")
        limit = int(arguments.get("limit", 5))
        memories = self._memory.get_long_term(user_id, limit=limit)
        return "\n".join(memories) or "Nenhuma memória."


class ExternalApiMockTool(Tool):
    def __init__(self) -> None:
        self.spec = ToolSpec(
            name="external_api_mock",
            description="Simula chamada de API externa.",
            parameters={
                "type": "object",
                "properties": {"resource": {"type": "string"}},
                "required": ["resource"],
            },
        )

    def run(self, arguments: dict[str, Any]) -> str:
        resource = arguments.get("resource", "default")
        payload = {"resource": resource, "status": "ok", "data": {"value": 42}}
        return json.dumps(payload, ensure_ascii=False)
