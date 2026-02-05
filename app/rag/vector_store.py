from __future__ import annotations

import math
from typing import Iterable, Protocol

import faiss
import numpy as np


class VectorStore(Protocol):
    def add(self, documents: list[str], embeddings: list[list[float]]) -> None:
        ...

    def similarity_search(self, embedding: list[float], k: int) -> list[str]:
        ...

    def count(self) -> int:
        ...


class FaissVectorStore:
    def __init__(self) -> None:
        self._docs: list[str] = []
        self._index: faiss.Index | None = None

    def add(self, documents: list[str], embeddings: list[list[float]]) -> None:
        if not documents:
            return
        vectors = np.array(embeddings, dtype="float32")
        vectors = self._normalize(vectors)
        if self._index is None:
            self._index = faiss.IndexFlatIP(vectors.shape[1])
        self._index.add(vectors)
        self._docs.extend(documents)

    def similarity_search(self, embedding: list[float], k: int) -> list[str]:
        if self._index is None:
            return []
        query = self._normalize(np.array([embedding], dtype="float32"))
        scores, indices = self._index.search(query, k)
        results = []
        for idx in indices[0]:
            if 0 <= idx < len(self._docs):
                results.append(self._docs[idx])
        return results

    def count(self) -> int:
        return len(self._docs)

    @staticmethod
    def _normalize(vectors: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return vectors / norms


class InMemoryVectorStore:
    def __init__(self) -> None:
        self._docs: list[str] = []
        self._embeddings: list[list[float]] = []

    def add(self, documents: list[str], embeddings: list[list[float]]) -> None:
        self._docs.extend(documents)
        self._embeddings.extend(embeddings)

    def similarity_search(self, embedding: list[float], k: int) -> list[str]:
        scored = [
            (self._cosine(embedding, emb), doc)
            for emb, doc in zip(self._embeddings, self._docs)
        ]
        scored.sort(key=lambda item: item[0], reverse=True)
        return [doc for _, doc in scored[:k]]

    def count(self) -> int:
        return len(self._docs)

    @staticmethod
    def _cosine(a: Iterable[float], b: Iterable[float]) -> float:
        a_list = list(a)
        b_list = list(b)
        dot = sum(x * y for x, y in zip(a_list, b_list))
        norm_a = math.sqrt(sum(x * x for x in a_list)) or 1.0
        norm_b = math.sqrt(sum(y * y for y in b_list)) or 1.0
        return dot / (norm_a * norm_b)
