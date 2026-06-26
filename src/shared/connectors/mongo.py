from beanie import Document as MongoDocument
from beanie import init_beanie
from pymongo import AsyncMongoClient

from src.shared.utils.log import Logger


class MongoStorage:
    def __init__(self, uri: str, models: list[type[MongoDocument]]):
        try:
            Logger.info("Creating MongoDB storage class")
            self._client: AsyncMongoClient | None = None
            self._models = models
            self._uri = uri
            self._db_name = "db_name"
            Logger.info("MongoDB storage class created successfully.")
        except Exception as e:
            Logger.error(f"Failed to initialize MongoDB: {e}")
            raise

    async def connect(self):
        try:
            Logger.info("Initializing MongoDB connection")
            self._client = AsyncMongoClient(self._uri)

            await init_beanie(database=self._client[self._db_name], document_models=self._models)
            Logger.info("MongoDB initialized successfully.")
        except Exception as e:
            Logger.error(f"Failed to initialize MongoDB: {e}")
            raise

    @property
    def client(self):
        return self._client

    async def close(self) -> None:
        try:
            Logger.info("Closing MongoDB client.")
            if self._client:
                await self._client.close()
            Logger.info("MongoDB client closed successfully.")
        except Exception as e:
            Logger.error(f"Failed to close MongoDB client: {e}")
            raise
