from __future__ import annotations


def test_tool_usage(agent, memory_service) -> None:
    memory_service.add_long_term("u1", "memoria importante")
    message = 'USE_TOOL:retrieve_memory {"user_id":"u1","limit":1}'
    result = agent.chat(user_id="u1", message=message)
    assert "Tool executada" in result.reply
