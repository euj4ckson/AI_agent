from __future__ import annotations

from fastapi import APIRouter

from app.models.schemas import MemoryResponse
from app.services.chat_service import get_memory_service

router = APIRouter()


@router.get("/memory/{user_id}", response_model=MemoryResponse)
def get_memory(user_id: str) -> MemoryResponse:
    memory_service = get_memory_service()
    memories = memory_service.get_long_term(user_id, limit=20)
    return MemoryResponse(user_id=user_id, memories=memories)
