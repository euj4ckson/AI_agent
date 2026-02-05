from __future__ import annotations


def test_rag_retrieval(rag_service) -> None:
    rag_service.add_documents(["Documento A sobre IA", "Documento B sobre finanças"])
    results = rag_service.search("IA", k=1)
    assert results
