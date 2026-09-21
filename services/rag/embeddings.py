import hashlib
from abc import ABC, abstractmethod


class EmbeddingModel(ABC):
    @abstractmethod
    async def embed(self, text: str) -> list[float]: ...


class HashEmbedding(EmbeddingModel):
    """Deterministic bag-of-words hashing embedding. Test/dev only, not semantic."""

    def __init__(self, dim: int = 64) -> None:
        self.dim = dim

    async def embed(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        for token in text.lower().split():
            h = int(hashlib.md5(token.encode()).hexdigest(), 16)
            vec[h % self.dim] += 1.0
        return vec
