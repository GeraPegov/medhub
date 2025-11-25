from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.presentation.api.router import api_router

app = FastAPI()

templates = Jinja2Templates('app/presentation/api/endpoints/templates')

app.mount("/static", StaticFiles(directory="app/presentation/api/endpoints/templates"), name="static")
# @app.exception_handler(HTTPException)
# async def handle_http_exception(request: Request, exc: HTTPException):
#     return templates.TemplateResponse(
#         "error.html",
#         {"request": request, "error": exc.detail},
#         status_code=exc.status_code
#     )

app.include_router(api_router)
