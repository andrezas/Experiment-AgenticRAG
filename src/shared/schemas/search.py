from pydantic import BaseModel
from typing import List

class SearchParams(BaseModel):
    query: str
    top_k: int = 5
    similarity_threshold: float = 0.7

class ChunkResponse(BaseModel):
    content: str
    score: float
    metadata: dict