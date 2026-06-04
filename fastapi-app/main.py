
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager
from redis.asyncio.connection import ConnectionPool

from app.presentation.api.router import api_router
from app.presentation.dependencies.scheduler import scheduler_service_context
from app.infrastructure.config import settings
import app.presentation.dependencies.cache as state

scheduler = AsyncIOScheduler() 

async def update_views_counter():
    async with scheduler_service_context() as service:
        await service.update_views_counter()
redis_pool = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    state.redis_pool = ConnectionPool.from_url(
        f'redis://{settings.HOST_REDIS}:{settings.PORT_REDIS}',
        decode_responses=True,
        encoding='utf-8',
        max_connections=10,
        socket_timeout=1.0,
        socket_connect_timeout=1.0,
        retry_on_timeout=False
    )
    scheduler.add_job(
        update_views_counter,
        trigger="interval",
        seconds=10  
    )
    scheduler.start()
    yield
    scheduler.shutdown()
    await redis_pool.aclose()

app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates('app/presentation/api/endpoints/templates')

app.mount("/static", StaticFiles(directory="app/presentation/api/endpoints/templates"), name="static")

app.include_router(api_router)
