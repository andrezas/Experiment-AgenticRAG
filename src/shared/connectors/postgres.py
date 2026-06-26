from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from src.shared.utils.log import Logger


class PostgresStorage:
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine
        self._session_maker = async_sessionmaker(bind=self._engine, expire_on_commit=False)
        Logger.info("DB session maker initialized successfully.")

    @classmethod
    async def create(cls, credentials: dict) -> "PostgresStorage":
        Logger.info("Initializing DB connection.")
        try:
            engine = await cls._create_engine(credentials=credentials)
            return cls(engine)
        except Exception as e:
            Logger.error(f"DB connection failed: {e}")
            raise

    async def close(self) -> None:
        Logger.info("Closing DB connection pool.")
        await self._engine.dispose()

    @asynccontextmanager
    async def get_db_session(self) -> AsyncGenerator[AsyncSession]:
        async with self._session_maker() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    @staticmethod
    def _format_pg_credentials(values: dict) -> dict:
        return {"drivername": "postgresql+psycopg", **values}

    @staticmethod
    async def _create_engine(credentials: dict) -> AsyncEngine:
        url = URL.create(**PostgresStorage._format_pg_credentials(credentials))
        return create_async_engine(url, pool_pre_ping=True)
