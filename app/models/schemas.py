from __future__ import annotations

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)


class ChatResponse(BaseModel):
    reply: str
    steps: int


class DocumentRequest(BaseModel):
    documents: list[str] = Field(..., min_length=1)


class MemoryResponse(BaseModel):
    user_id: str
    memories: list[str]
