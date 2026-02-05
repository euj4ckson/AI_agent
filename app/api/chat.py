from __future__ import annotations

from fastapi import APIRouter

from app.models.schemas import ChatRequest, ChatResponse
from app.services.chat_service import get_agent

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    agent = get_agent()
    result = agent.chat(user_id=request.user_id, message=request.message)
    return ChatResponse(reply=result.reply, steps=result.steps)
