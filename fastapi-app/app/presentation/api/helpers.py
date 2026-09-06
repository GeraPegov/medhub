import secrets

from fastapi import Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates("app/presentation/api/endpoints/templates/html")


def ensure_csrf_token(request: Request) -> None:
    if "csrf_token" not in request.session:
        request.session["csrf_token"] = secrets.token_urlsafe(32)


def error_page(request: Request, message: str, status_code: int):
    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={"error": message, "status_code": status_code},
        status_code=status_code,
    )
