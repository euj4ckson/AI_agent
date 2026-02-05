from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Protocol

import httpx
from openai import OpenAI


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class LLMResponse:
    content: str | None
    tool_calls: list[ToolCall]


class LLMClient(Protocol):
    def chat(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> LLMResponse:
        ...


class OpenAIChatClient:
    def __init__(self, api_key: str, model: str) -> None:
        self._client = OpenAI(api_key=api_key)
        self._model = model

    def chat(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> LLMResponse:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            tools=tools if tools else None,
            tool_choice="auto" if tools else None,
        )
        message = response.choices[0].message
        tool_calls: list[ToolCall] = []
        for call in message.tool_calls or []:
            tool_calls.append(
                ToolCall(
                    id=call.id,
                    name=call.function.name,
                    arguments=json.loads(call.function.arguments or "{}"),
                )
            )
        return LLMResponse(content=message.content, tool_calls=tool_calls)


class OllamaChatClient:
    def __init__(self, host: str, model: str, timeout: float = 120.0) -> None:
        self._client = httpx.Client(base_url=host, timeout=timeout)
        self._model = model

    def chat(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> LLMResponse:
        payload = {"model": self._model, "messages": messages, "stream": False}
        response = self._client.post("/api/chat", json=payload)
        response.raise_for_status()
        data = response.json()
        content = data.get("message", {}).get("content", "")
        return LLMResponse(content=content, tool_calls=[])


class FakeLLMClient:
    """LLM fake para testes. Use 'USE_TOOL:<tool> {json}' para forçar."""

    def chat(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> LLMResponse:
        last_user = next(
            (msg["content"] for msg in reversed(messages) if msg["role"] == "user"),
            "",
        )
        if any(msg["role"] == "tool" for msg in messages):
            return LLMResponse(content="Tool executada com sucesso.", tool_calls=[])
        if last_user and "USE_TOOL:" in last_user:
            payload = last_user.split("USE_TOOL:", 1)[1].strip()
            parts = payload.split(maxsplit=1)
            tool_name = parts[0]
            arguments: dict[str, Any] = {}
            if len(parts) == 2:
                try:
                    arguments = json.loads(parts[1])
                except json.JSONDecodeError:
                    arguments = {}
            return LLMResponse(
                content=None,
                tool_calls=[ToolCall(id="tool_1", name=tool_name, arguments=arguments)],
            )
        lower = last_user.lower()
        if any(token in lower for token in ("olá", "ola", "oi")):
            reply = "Olá! Posso ajudar com dúvidas, RAG, memória e automações."
        elif "rag" in lower:
            reply = (
                "Posso buscar contexto na base vetorial e montar uma resposta com base nos documentos."
            )
        elif "memória" in lower or "memoria" in lower:
            reply = "Posso salvar e recuperar memórias por usuário e chat."
        elif "tool" in lower or "ferramenta" in lower:
            reply = "Consigo usar ferramentas externas para buscar dados ou executar ações."
        else:
            reply = (
                "Entendi sua solicitação. Posso resumir, responder e sugerir próximos passos."
            )
        return LLMResponse(content=reply, tool_calls=[])
