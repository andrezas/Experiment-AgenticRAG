import logging
from typing import Any

from langchain_core.embeddings import Embeddings
from qdrant_client import models

from src.shared.connectors.qdrant import QdrantStorage

logger = logging.getLogger(__name__)


async def retrieve_chunks(
    query: str,
    collection_name: str,
    test_context_id: str,
    qdrant_storage: QdrantStorage,
    embeddings: Embeddings,
    k: int = 5,
    exclude_ids: list[str] | None = None,
) -> list[Any]:
    query_vector = embeddings.embed_query(query)

    must_conditions = [models.FieldCondition(key="test_context_id", match=models.MatchValue(value=test_context_id))]

    must_not_conditions = []
    if exclude_ids:
        must_not_conditions.append(models.HasIdCondition(has_id=exclude_ids))

    search_filter = models.Filter(must=must_conditions, must_not=must_not_conditions if must_not_conditions else None)

    search_result = await qdrant_storage.search_points(
        collection_name=collection_name, query_vector=query_vector, limit=k, query_filter=search_filter
    )

    return search_result
