from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates

from app.presentation.api.router import api_router

app = FastAPI()

templates = Jinja2Templates('app/presentation/api/endpoints/templates')


@app.exception_handler(HTTPException)
async def handle_http_exception(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "error": exc.detail},
        status_code=exc.status_code
    )

app.include_router(api_router)
