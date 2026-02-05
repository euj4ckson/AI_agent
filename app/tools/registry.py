from __future__ import annotations

from typing import Any

from app.tools.base import Tool


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.spec.name] = tool

    def run(self, name: str, arguments: dict[str, Any]) -> str:
        tool = self._tools.get(name)
        if not tool:
            return f"Tool '{name}' não encontrada."
        return tool.run(arguments)

    def as_openai_tools(self) -> list[dict[str, Any]]:
        return [tool.openai_schema() for tool in self._tools.values()]
