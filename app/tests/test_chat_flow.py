from __future__ import annotations


def test_chat_flow_persists_memory(agent, memory_service) -> None:
    result = agent.chat(user_id="u1", message="Teste de chat")
    assert "Resposta" in result.reply

    memories = memory_service.get_long_term("u1", limit=10)
    assert len(memories) >= 2
