from qdrant_client import AsyncQdrantClient, models

from src.shared.utils.log import Logger


class QdrantStorage:
    def __init__(self, host: str, port: int):
        try:
            Logger.info(f"Initializing Qdrant client for host {host} on port {port}")
            self._client = AsyncQdrantClient(host=host, port=port)
            Logger.info("Qdrant client initialized.")
        except Exception as e:
            Logger.error(f"Failed to initialize Qdrant client: {e}")
            raise

    async def close(self) -> None:
        try:
            Logger.info("Closing Qdrant client.")
            await self._client.close()
            Logger.info("Qdrant client closed successfully.")
        except Exception as e:
            Logger.error(f"Failed to close Qdrant client: {e}")

    async def list_collections(self) -> list[str]:
        try:
            Logger.info("Listing all collections.")
            collections_response = await self._client.get_collections()
            names = [col.name for col in collections_response.collections]
            Logger.info(f"Found {len(names)} collections.")

            return names
        except Exception as e:
            Logger.error(f"Failed to list collections: {e}")
            raise

    async def collection_exists(self, collection_name: str) -> bool:
        try:
            Logger.info(f"Checking if collection '{collection_name}' exists.")
            await self._client.get_collection(collection_name=collection_name)
            Logger.info(f"Collection '{collection_name}' found.")
            return True
        except Exception:
            Logger.info(f"Collection '{collection_name}' does not exist.")
            return False

    async def create_collection(
        self, collection_name: str, vector_size: int, distance: models.Distance = models.Distance.COSINE
    ) -> None:
        try:
            Logger.info(f"Creating collection '{collection_name}'")
            await self._client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(size=vector_size, distance=distance),
            )
            Logger.info(f"Collection '{collection_name}' created successfully.")
        except Exception as e:
            Logger.warning(f"Failed to create collection '{collection_name}': {e}")
            raise

    async def delete_collection(self, collection_name: str) -> None:
        try:
            Logger.info(f"Deleting collection '{collection_name}'")
            result = await self._client.delete_collection(collection_name=collection_name)
            if not result:
                Logger.error("Delete operation couldn't be executed due to an unexpected error.")
                return

            Logger.info(f"Collection '{collection_name}' deleted successfully.")
        except Exception as e:
            Logger.error(f"Failed to delete collection '{collection_name}': {e}")
            raise

    async def upsert_points(self, collection_name: str, points: list[models.PointStruct]) -> None:
        try:
            Logger.info(f"Upserting {len(points)} points to collection '{collection_name}'")
            await self._client.upsert(collection_name=collection_name, points=points, wait=True)
            Logger.info(f"Successfully upserted {len(points)} points.")
        except Exception as e:
            Logger.error(f"Failed to upsert points to collection '{collection_name}': {e}")
            raise

    async def retrieve_points(self, collection_name: str, point_ids: list[str | int]) -> list[models.Record]:
        try:
            Logger.info(f"Retrieving {len(point_ids)} points from collection '{collection_name}'")
            records = await self._client.retrieve(collection_name=collection_name, ids=point_ids, with_payload=True)
            Logger.info(f"Successfully retrieved {len(records)} points.")

            return records
        except Exception as e:
            Logger.error(f"Failed to retrieve points from collection '{collection_name}': {e}")
            raise

    async def search_points(
        self, collection_name: str, query_vector: list[float], limit: int
    ) -> list[models.ScoredPoint]:
        try:
            Logger.info(f"Searching for {limit} nearest points in collection '{collection_name}'")
            hits = await self._client.query_points(
                collection_name=collection_name, query=query_vector, limit=limit, with_payload=True
            )

            Logger.info(f"Search completed, returning {len(hits.points)} hits.")

            return hits.points
        except Exception as e:
            Logger.error(f"Failed to search in collection '{collection_name}': {e}")
            raise

    async def delete_points(self, collection_name: str, point_ids: list[str | int]) -> None:
        try:
            Logger.info(f"Deleting {len(point_ids)} points from collection '{collection_name}'")
            await self._client.delete(collection_name=collection_name, points_selector=point_ids)
            Logger.info(f"Successfully deleted {len(point_ids)} points.")
        except Exception as e:
            Logger.error(f"Failed to delete points from collection '{collection_name}': {e}")
            raise

    async def search_groups(
        self,
        collection_name: str,
        query_vector: list[float],
        *,
        group_by: str,
        limit: int,
        score_threshold: float,
    ) -> list[models.PointGroup]:
        try:
            Logger.info(f"Searching for {limit} groups in the collection '{collection_name}'")

            groups_search_result = await self._client.search_groups(
                collection_name=collection_name,
                query_vector=query_vector,
                group_by=group_by,
                limit=limit,
                score_threshold=score_threshold,
                with_payload=True,
            )

            groups = groups_search_result.groups

            Logger.info(f"Search completed, returning {len(groups)} groups.")
            return groups

        except Exception as e:
            Logger.error(f"Failed to search for groups in collection '{collection_name}': {e}")

            raise
