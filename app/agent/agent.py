from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from app.agent.prompts import REASONING_PROMPT, SYSTEM_PROMPT, TOOLS_PROMPT
from app.core.config import settings
from app.core.llm import LLMClient, LLMResponse
from app.core.logging import get_logger
from app.memory.service import MemoryService
from app.rag.service import RagService
from app.tools.registry import ToolRegistry


@dataclass
class AgentResult:
    reply: str
    steps: int


class Agent:
    def __init__(
        self,
        llm: LLMClient,
        tool_registry: ToolRegistry,
        memory_service: MemoryService,
        rag_service: RagService,
        max_steps: int = 5,
    ) -> None:
        self._llm = llm
        self._tool_registry = tool_registry
        self._memory = memory_service
        self._rag = rag_service
        self._max_steps = max_steps
        self._logger = get_logger(self.__class__.__name__)

    def chat(self, user_id: str, message: str) -> AgentResult:
        self._logger.info("Nova mensagem: user_id=%s", user_id)

        self._memory.add_short_term(user_id, role="user", content=message)
        long_term = self._memory.get_long_term(user_id, limit=5)
        short_term = self._memory.get_short_term(user_id)
        if settings.rag_enabled:
            try:
                rag_context = self._rag.search(message, k=3)
            except Exception as exc:
                self._logger.warning("RAG indisponível: %s", exc)
                rag_context = []
        else:
            rag_context = []

        system_context = self._build_system_context(long_term, rag_context)
        history = short_term[:-1] if short_term else []
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": REASONING_PROMPT},
            {"role": "system", "content": TOOLS_PROMPT},
            {"role": "system", "content": system_context},
        ]
        messages.extend(history)
        messages.append({"role": "user", "content": message})

        tools = self._tool_registry.as_openai_tools()
        steps = 0
        while steps < self._max_steps:
            steps += 1
            self._logger.info("Passo do agente: %s", steps)
            response = self._llm.chat(messages=messages, tools=tools)
            if response.tool_calls:
                self._logger.info("Chamadas de tool: %s", len(response.tool_calls))
                tool_message = self._format_tool_message(response)
                messages.append(tool_message)
                for call in response.tool_calls:
                    result = self._tool_registry.run(call.name, call.arguments)
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": call.id,
                            "content": result,
                        }
                    )
                continue
            final_text = response.content or "Sem resposta no momento."
            self._memory.add_short_term(user_id, role="assistant", content=final_text)
            self._memory.add_long_term(user_id, content=message)
            self._memory.add_long_term(user_id, content=final_text)
            return AgentResult(reply=final_text, steps=steps)

        fallback = "Desculpe, não consegui concluir a resposta a tempo."
        self._logger.warning("Limite de passos atingido.")
        return AgentResult(reply=fallback, steps=steps)

    def _build_system_context(
        self,
        long_term: list[str],
        rag_context: list[str],
    ) -> str:
        memory_block = "\n".join(f"- {item}" for item in long_term) or "Sem memórias."
        rag_block = "\n".join(f"- {doc}" for doc in rag_context) or "Sem contexto RAG."

        return (
            "Contexto de memória longa:\n"
            f"{memory_block}\n\n"
            "Contexto RAG:\n"
            f"{rag_block}"
        )

    def _format_tool_message(self, response: LLMResponse) -> dict[str, Any]:
        tool_calls = [
            {
                "id": call.id,
                "type": "function",
                "function": {
                    "name": call.name,
                    "arguments": json.dumps(call.arguments, ensure_ascii=False),
                },
            }
            for call in response.tool_calls
        ]
        return {"role": "assistant", "content": None, "tool_calls": tool_calls}
