import asyncio

from app.domain.logging import logger
from app.infrastructure.database.connection import (
    create_database_if_not_exists,
    prod_engine,
)


async def init_production_db():
    logger.info('initializing production database')

    await create_database_if_not_exists('medhub')

    # await create_tables(prod_engine)

    await prod_engine.dispose()

async def init_test_db():
    logger.info('initializing test database')

    await create_database_if_not_exists('testmedhub')

async def main():
    await init_production_db()
    await init_test_db()

if __name__ == "__main__":
    asyncio.run(main())
