import logging
import uuid

from langchain_core.embeddings import Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import models

from src.shared.connectors.qdrant import QdrantStorage
from src.shared.utils.log import Logger

Logger.configure()
logger = logging.getLogger(__name__)


async def index_context_to_qdrant(
    context_text: str,
    collection_name: str,
    metadata: dict,
    test_context_id: str,
    qdrant_storage: QdrantStorage,
    embeddings: Embeddings,
):
    """Divide o context_text em chunks e indexa na coleção informada do Qdrant."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=100,
        length_function=len,
    )

    chunks = text_splitter.split_text(context_text)
    if not chunks:
        logger.warning(f"Nenhum chunk gerado para a coleção {collection_name}")
        return

    if not await qdrant_storage.collection_exists(collection_name):
        sample_embedding = embeddings.embed_query("teste")
        vector_size = len(sample_embedding)

        await qdrant_storage.create_collection(collection_name=collection_name, vector_size=vector_size)

    vectors = embeddings.embed_documents(chunks)

    points = []
    for chunk, vector in zip(chunks, vectors):
        # vector = embeddings.embed_query(chunk)
        payload = {"test_context_id": test_context_id, "page_content": chunk, "metadata": metadata}

        points.append(models.PointStruct(id=str(uuid.uuid4()), vector=vector, payload=payload))

    if points:
        await qdrant_storage.upsert_points(collection_name=collection_name, points=points)
