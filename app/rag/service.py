from __future__ import annotations

from typing import Iterable, Protocol

import httpx
from openai import OpenAI

from app.rag.vector_store import VectorStore


class EmbeddingClient(Protocol):
    def embed(self, texts: Iterable[str]) -> list[list[float]]:
        ...


class OpenAIEmbeddingClient:
    def __init__(self, api_key: str, model: str) -> None:
        self._client = OpenAI(api_key=api_key)
        self._model = model

    def embed(self, texts: Iterable[str]) -> list[list[float]]:
        response = self._client.embeddings.create(model=self._model, input=list(texts))
        return [item.embedding for item in response.data]


class OllamaEmbeddingClient:
    def __init__(self, host: str, model: str, timeout: float = 120.0) -> None:
        self._client = httpx.Client(base_url=host, timeout=timeout)
        self._model = model

    def embed(self, texts: Iterable[str]) -> list[list[float]]:
        embeddings: list[list[float]] = []
        for text in texts:
            response = self._client.post(
                "/api/embeddings", json={"model": self._model, "prompt": text}
            )
            response.raise_for_status()
            data = response.json()
            embeddings.append(data.get("embedding", []))
        return embeddings


class FakeEmbeddingClient:
    def embed(self, texts: Iterable[str]) -> list[list[float]]:
        embeddings: list[list[float]] = []
        for text in texts:
            base = sum(ord(ch) for ch in text) or 1
            embeddings.append([(base % 101) / 100.0, (base % 97) / 100.0, 0.5])
        return embeddings


class RagService:
    def __init__(self, vector_store: VectorStore, embedding_client: EmbeddingClient) -> None:
        self._store = vector_store
        self._embeddings = embedding_client

    def add_documents(self, documents: list[str]) -> None:
        vectors = self._embeddings.embed(documents)
        self._store.add(documents=documents, embeddings=vectors)

    def search(self, query: str, k: int = 3) -> list[str]:
        if self._store.count() == 0:
            return []
        vector = self._embeddings.embed([query])[0]
        return self._store.similarity_search(vector, k=k)
