from __future__ import annotations

from app.rag.service import RagService


class DocumentService:
    def __init__(self, rag_service: RagService) -> None:
        self._rag = rag_service

    def add_documents(self, documents: list[str]) -> None:
        self._rag.add_documents(documents)
