import datetime as dt
import logging
from functools import wraps
from typing import Any

import aiohttp
from fastapi import APIRouter, Form, Query, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.domain.exceptions import (
    AdminApiUnavailableError,
    BadGatewayError,
    NotFoundRecordsError,
)
from app.infrastructure.config import settings

router = APIRouter()

ADMIN_API_URL = settings.ADMIN_API_URL
templates = Jinja2Templates("app/presentation/api/endpoints/templates/html")
logger = logging.getLogger(__name__)


def admin_api_error_response() -> JSONResponse:
    return JSONResponse(
        content={"detail": "Admin API недоступен"},
        status_code=502,
    )


async def delete_admin_api(path: str) -> None:
    status, _ = await request_admin_api("DELETE", path)
    if status == 204:
        return
    if status == 404:
        raise NotFoundRecordsError
    logger.error(
        "Admin API вернул неожиданный статус при удалении: path=%s status=%s",
        path,
        status,
    )
    raise BadGatewayError(status)


async def request_admin_api(
    method: str,
    path: str,
    **kwargs: Any,
) -> tuple[int, Any]:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method,
                f"{ADMIN_API_URL}{path}",
                **kwargs,
            ) as response:
                if response.status == 204:
                    return response.status, None
                if response.content_type == "application/json":
                    try:
                        return response.status, await response.json()
                    except ValueError as error:
                        logger.exception(
                            "Admin API вернул невалидный JSON: method=%s path=%s status=%s",
                            method,
                            path,
                            response.status,
                        )
                        raise BadGatewayError(response.status) from error
                return response.status, await response.text()
    except aiohttp.ClientError as error:
        logger.exception(
            "Ошибка запроса к Admin API: method=%s path=%s",
            method,
            path,
        )
        raise AdminApiUnavailableError from error


async def get_admin_data(method: str, path: str, params: dict[str, Any]) -> Any:
    status, data = await request_admin_api(method, path, params=params)
    if status != 200:
        logger.error(
            "Admin API вернул неожиданный статус: method=%s path=%s status=%s",
            method,
            path,
            status,
        )
        raise BadGatewayError(status)
    return data


def check_token(func):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        token = request.cookies.get("admin_access_token")
        if not token:
            return RedirectResponse("/admin/login", status_code=303)
        try:
            status, _ = await request_admin_api(
                "GET",
                "/admin/me",
                headers={"Authorization": f"Bearer {token}"},
            )
        except (AdminApiUnavailableError, BadGatewayError):
            return admin_api_error_response()
        if status == 401:
            return RedirectResponse("/admin/login", status_code=303)
        if status != 204:
            logger.error(
                "Admin API вернул неожиданный статус при проверке токена: status=%s",
                status,
            )
            return admin_api_error_response()
        return await func(request, *args, **kwargs)

    return wrapper


@router.get("/admin/login")
async def register_form(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="admin/admin_login.html",
    )


@router.post("/admin/login")
async def register_check(
    login: str = Form(...),
    password: str = Form(...),
):
    try:
        status, data = await request_admin_api(
            "POST",
            "/admin/login",
            json={"login": login, "password": password},
        )
        if status in (401, 403):
            logger.warning(
                "Авторизация администратора отклонена: login=%s status=%s",
                login,
                status,
            )
            return Response(content="invalid credentials", status_code=401)

        if status != 200:
            logger.error(
                "Admin API вернул неожиданный статус при авторизации: status=%s",
                status,
            )
            return admin_api_error_response()

        if not isinstance(data, dict):
            logger.error(
                "Admin API вернул невалидный ответ при авторизации: login=%s",
                login,
            )
            return admin_api_error_response()

        token = data.get("access_token")
        if not token:
            logger.error(
                "Admin API вернул успешный статус без access_token: login=%s",
                login,
            )
            return Response(content="internal server error", status_code=502)

        response = RedirectResponse("/admin", status_code=303)

        response.set_cookie(
            key="admin_access_token", value=token, httponly=True, samesite="lax"
        )
        logger.info("Успешная авторизация с логином = %s", login)
        return response
    except (AdminApiUnavailableError, BadGatewayError):
        return admin_api_error_response()


@router.get("/admin")
@check_token
async def admin(
    request: Request,
    selected_date: dt.date | None = Query(None, alias="date"),
):
    try:
        date = (selected_date or dt.datetime.now().date()).isoformat()
        statistics = await get_admin_data("GET", "/admin/statistics", {"date": date})
        return templates.TemplateResponse(
            request=request,
            name="admin/admin.html",
            context={
                "articles_today": statistics["articles_today"],
                "users_today": statistics["users_today"],
                "quantity_users": statistics["quantity_users"]["Value"]
                if statistics["quantity_users"]["Err"].strip() == ""
                else statistics["quantity_users"]["Err"],
                "quantity_articles": statistics["quantity_articles"]["Value"]
                if statistics["quantity_articles"]["Err"].strip() == ""
                else statistics["quantity_articles"]["Err"],
            },
        )
    except (AdminApiUnavailableError, BadGatewayError):
        return admin_api_error_response()

@router.get("/admin/users")
@check_token
async def users_menu(
    request: Request,
    user_id: int | None = Query(None, alias="id"),
    email: str | None = Query(None),
    username: str | None = Query(None),
):
    try:
        params = {
            key: value
            for key, value in {
                "user_id": user_id,
                "email": email,
                "username": username,
            }.items()
            if value not in (None, "")
        }
        users = await get_admin_data("GET", "/admin/users", params)
        return templates.TemplateResponse(
            request=request,
            name="admin/admin_users.html",
            context={"users": users},
        )
    except (AdminApiUnavailableError, BadGatewayError):
        return admin_api_error_response()


@router.post("/admin/users/{user_id}")
@check_token
async def user_delete(
    request: Request,
    user_id: int,
):
    try:
        await delete_admin_api(f"/admin/users/{user_id}")
        logger.info("Администратор удалил пользователя: user_id=%s", user_id)
        return RedirectResponse("/admin/users", status_code=303)
    except NotFoundRecordsError:
        logger.info("Пользователь для удаления не найден: user_id=%s", user_id)
        return JSONResponse(
            content={"detail": "Пользователь не найден"},
            status_code=404,
        )
    except (AdminApiUnavailableError, BadGatewayError):
        return admin_api_error_response()


@router.get("/admin/articles")
@check_token
async def articles_menu(
    request: Request,
    user_id: int | None = Query(None),
    title: str | None = Query(None),
    article_id: int | None = Query(None),
):
    try:
        params = {
            key: value
            for key, value in {
                "article_id": article_id,
                "title": title,
                "user_id": user_id,
            }.items()
            if value not in (None, "")
        }
        articles = await get_admin_data("GET", "/admin/articles", params)
        return templates.TemplateResponse(
            request=request,
            name="admin/admin_articles.html",
            context={"articles": articles},
        )
    except (AdminApiUnavailableError, BadGatewayError):
        return admin_api_error_response()


@router.post("/admin/articles/{article_id}")
@check_token
async def article_delete(
    request: Request,
    article_id: int,
):
    try:
        await delete_admin_api(f"/admin/articles/{article_id}")
        logger.info("Администратор удалил статью: article_id=%s", article_id)
        return RedirectResponse("/admin/articles", status_code=303)
    except NotFoundRecordsError:
        logger.info("Статья для удаления не найдена: article_id=%s", article_id)
        return JSONResponse(
            content={"detail": "Статья не найдена"},
            status_code=404,
        )
    except (AdminApiUnavailableError, BadGatewayError):
        return admin_api_error_response()


@router.get("/admin/comments")
@check_token
async def comments_menu(
    request: Request,
    user_id: int | None = Query(None),
    article_id: int | None = Query(None),
    public_date: dt.date | None = Query(None),
):
    try:
        params = {
            key: value
            for key, value in {
                "article_id": article_id,
                "public_date": public_date.isoformat() if public_date else None,
                "user_id": user_id,
            }.items()
            if value not in (None, "")
        }
        comments = await get_admin_data("GET", "/admin/comments", params)
        return templates.TemplateResponse(
            request=request,
            name="admin/admin_comments.html",
            context={"comments": comments},
        )
    except (AdminApiUnavailableError, BadGatewayError):
        return admin_api_error_response()


@router.post("/admin/comments/{comment_id}")
@check_token
async def comment_delete(
    request: Request,
    comment_id: int,
):
    try:
        await delete_admin_api(f"/admin/comments/{comment_id}")
        logger.info("Администратор удалил комментарий: comment_id=%s", comment_id)
        return RedirectResponse("/admin/comments", status_code=303)
    except NotFoundRecordsError:
        logger.info("Комментарий для удаления не найден: comment_id=%s", comment_id)
        return JSONResponse(
            content={"detail": "Комментарий не найден"},
            status_code=404,
        )
    except (AdminApiUnavailableError, BadGatewayError):
        return admin_api_error_response()
