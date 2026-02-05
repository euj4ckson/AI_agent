from __future__ import annotations

from fastapi import APIRouter

from app.models.schemas import DocumentRequest
from app.services.chat_service import get_rag_service
from app.services.document_service import DocumentService

router = APIRouter()


@router.post("/documents")
def add_documents(request: DocumentRequest) -> dict[str, int | str]:
    rag_service = get_rag_service()
    service = DocumentService(rag_service)
    service.add_documents(request.documents)
    return {"status": "ok", "count": len(request.documents)}
