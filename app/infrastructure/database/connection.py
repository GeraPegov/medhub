from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.infrastructure.config import settings

SQL_DB_URL = settings.MY_DB_URL

async_engine = create_async_engine(SQL_DB_URL, echo=False, connect_args={"server_settings": {"client_encoding": "utf8"}})

AsyncSessionLocal = async_sessionmaker(

    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
