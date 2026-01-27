from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.presentation.api.router import api_router
from app.presentation.dependencies.cache import lifespan

app = FastAPI(lifespan=lifespan)

templates = Jinja2Templates('app/presentation/api/endpoints/templates')

app.mount("/static", StaticFiles(directory="app/presentation/api/endpoints/templates"), name="static")

app.include_router(api_router)
