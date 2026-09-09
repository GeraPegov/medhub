import logging
import secrets

from fastapi import Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates("app/presentation/api/endpoints/templates/html")
logger = logging.getLogger(__name__)


def ensure_csrf_token(request: Request) -> None:
    if "csrf_token" not in request.session:
        request.session["csrf_token"] = secrets.token_urlsafe(32)


def error_page(request: Request, message: str, status_code: int):
    if status_code >= 500:
        log = logger.error
    elif status_code in {401, 403, 429}:
        log = logger.warning
    else:
        log = logger.info
    log(
        "Возвращена страница ошибки: status=%s path=%s message=%s",
        status_code,
        request.url.path,
        message,
    )
    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={"error": message, "status_code": status_code},
        status_code=status_code,
    )
