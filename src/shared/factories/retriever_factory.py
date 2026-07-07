import logging
from typing import List, Any, Optional
from qdrant_client import models
from langchain_core.embeddings import Embeddings
from src.shared.connectors.qdrant import QdrantStorage

logger = logging.getLogger(__name__)

async def retrieve_chunks(
    query: str,
    collection_name: str,
    test_context_id: str,
    qdrant_storage: QdrantStorage,
    embeddings: Embeddings,
    k: int = 5,
    exclude_ids: Optional[List[str]] = None
) -> List[Any]:
    """
    Abstrai a geração de embedding, aplicação do filtro de contexto 
    e chamada assíncrona ao Qdrant.
    """
    query_vector = embeddings.embed_query(query)
    
    search_filter = models.Filter(
        must=[
            models.FieldCondition(
                key="test_context_id",
                match=models.MatchValue(value=test_context_id)
            )
        ]
    )

    must_not_conditions = []
    if exclude_ids:
        must_not_conditions.append(
            models.HasIdCondition(has_id=exclude_ids)
        )

    search_filter = models.Filter(
        must=search_filter,
        must_not=must_not_conditions
    )

    search_result = await qdrant_storage.client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        query_filter=search_filter,
        limit=k
    )
    
    return search_result