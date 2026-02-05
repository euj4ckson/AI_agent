from __future__ import annotations


def test_agent_initialization(agent) -> None:
    result = agent.chat(user_id="u1", message="Oi agente")
    assert result.reply
    assert result.steps >= 1
