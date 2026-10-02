import datetime as dt
import logging
from typing import Any

import aiohttp
from fastapi import APIRouter, Depends, Form, Query, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.application.services.cache_service import (
    CachedArticleService,
    CachedCommentService,
    CachedUserService,
)
from app.application.services.comment_service import CommentService
from app.domain.exceptions import (
    AdminApiUnavailableError,
    BadGatewayError,
    NotFoundCommentError,
    NotFoundRecordsError,
    NotFoundUserError,
    NotValidCsrfTokenError,
)
from app.infrastructure.config import settings
from app.presentation.api.endpoints.auth import check_csrf_token
from app.presentation.api.helpers import ensure_csrf_token, error_page
from app.presentation.dependencies.cache import (
    get_cached_article_service,
    get_cached_comment_service,
    get_cached_user_service,
)
from app.presentation.dependencies.comments import get_comment_service

router = APIRouter()

ADMIN_API_URL = settings.ADMIN_API_URL
templates = Jinja2Templates("app/presentation/api/endpoints/templates/html")
logger = logging.getLogger(__name__)


def admin_api_error_response() -> JSONResponse:
    return JSONResponse(
        content={"detail": "Admin API недоступен"},
        status_code=502,
    )


async def delete_admin_api(path: str, headers: dict[str, str]) -> None:
    status, _ = await request_admin_api(
        method="DELETE", path=path, headers_data=headers
    )
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
    headers_data: dict,
    **kwargs: Any,
) -> tuple[int, Any]:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method, f"{ADMIN_API_URL}{path}", **kwargs, headers=headers_data
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


async def get_admin_data(
    method: str, path: str, params: dict[str, Any], headers: dict
) -> Any:
    status, data = await request_admin_api(
        method, path, params=params, headers_data=headers
    )
    if status != 200:
        logger.error(
            "Admin API вернул неожиданный статус: method=%s path=%s status=%s",
            method,
            path,
            status,
        )
        raise BadGatewayError(status)
    return data


@router.get("/admin/login")
async def register_form(request: Request):
    ensure_csrf_token(request)
    return templates.TemplateResponse(
        request=request,
        name="admin/admin_login.html",
    )


@router.post("/admin/login")
async def register_check(
    request: Request,
    csrf_token: str = Form(...),
    login: str = Form(...),
    password: str = Form(...),
):
    try:
        await check_csrf_token(request, csrf_token)
        async with aiohttp.ClientSession() as session:
            async with session.request(
                "POST",
                f"{ADMIN_API_URL}/admin/login",
                json={"login": login, "password": password},
            ) as response:
                if response.status in (401, 403):
                    logger.warning(
                        "Авторизация администратора отклонена: login=%s status=%s",
                        login,
                        response.status,
                    )
                    return Response(content="invalid credentials", status_code=401)

                if response.status != 200:
                    logger.error(
                        "Admin API вернул неожиданный статус при авторизации: status=%s",
                        response.status,
                    )
                    return admin_api_error_response()

                if not isinstance(await response.json(), dict):
                    logger.error(
                        "Admin API вернул невалидный ответ при авторизации: login=%s",
                        login,
                    )
                    return admin_api_error_response()

                data = await response.json()
                token = data.get("access_token")
                if not token:
                    logger.error(
                        "Admin API вернул успешный статус без access_token: login=%s",
                        login,
                    )
                    return Response(content="internal server error", status_code=502)

        response = RedirectResponse("/admin", status_code=303)

        response.set_cookie(
            key="admin_access_token",
            value=token,
            httponly=True,
            samesite="lax",
            secure=True,
        )
        logger.info("Успешная авторизация с логином = %s", login)
        return response
    except NotValidCsrfTokenError:
        return error_page(request, "Невалидный CSRF-токен", 403)
    except (AdminApiUnavailableError, BadGatewayError):
        return admin_api_error_response()


@router.get("/admin")
async def admin(
    request: Request,
    date_first: dt.date | None = Query(None),
    date_last: dt.date | None = Query(None),
):
    try:
        token = request.cookies.get("admin_access_token")
        date_from = (date_first or dt.date.today()).isoformat()
        date_to = ((date_last or dt.date.today()) + dt.timedelta(days=1)).isoformat()
        statistics = await get_admin_data(
            "GET",
            "/admin/statistics",
            {"date_from": date_from, "date_to": date_to},
            {"Authorization": f"Bearer {token}"},
        )
        return templates.TemplateResponse(
            request=request,
            name="admin/admin_statistics.html",
            context={
                "popularity_authors": statistics["popularity_authors"]["Value"]
                if statistics["popularity_authors"]["Err"].strip() == ""
                else statistics["popularity_authors"]["Err"],
                "popularity_category": statistics["popularity_category"]["Value"]
                if statistics["popularity_category"]["Err"].strip() == ""
                else statistics["popularity_category"]["Err"],
                "quantity_users": statistics["quantity_users"]["Value"]
                if statistics["quantity_users"]["Err"].strip() == ""
                else statistics["quantity_users"]["Err"],
                "quantity_articles": statistics["quantity_articles"]["Value"]
                if statistics["quantity_articles"]["Err"].strip() == ""
                else statistics["quantity_articles"]["Err"],
            },
        )
    except (AdminApiUnavailableError, BadGatewayError):
        logger.error(f"Ошибка при данных, date from = {date_from}, date to = {date_to}")
        return admin_api_error_response()


@router.get("/admin/users")
async def users_menu(
    request: Request,
    user_id: int | None = Query(None, alias="id"),
    email: str | None = Query(None),
    username: str | None = Query(None),
):
    try:
        token = request.cookies.get("admin_access_token")
        params = {
            key: value
            for key, value in {
                "user_id": user_id,
                "email": email,
                "username": username,
            }.items()
            if value not in (None, "")
        }
        users = await get_admin_data(
            "GET", "/admin/users", params, {"Authorization": f"Bearer {token}"}
        )
        return templates.TemplateResponse(
            request=request,
            name="admin/admin_users.html",
            context={"users": users},
        )
    except (AdminApiUnavailableError, BadGatewayError):
        return admin_api_error_response()


@router.post("/admin/users/{user_id}")
async def user_delete(
    request: Request,
    user_id: int,
    csrf_token: str = Form(...),
    cached_user_service: CachedUserService = Depends(get_cached_user_service),
):
    try:
        await check_csrf_token(request, csrf_token)
        user = await cached_user_service.get_user(user_id)
        token = request.cookies.get("admin_access_token")
        await delete_admin_api(
            f"/admin/users/{user_id}", {"Authorization": f"Bearer {token}"}
        )
        await cached_user_service.invalidate_user(user)
        logger.info("Администратор удалил пользователя: user_id=%s", user_id)
        return RedirectResponse("/admin/users", status_code=303)
    except NotValidCsrfTokenError:
        return error_page(request, "Невалидный CSRF-токен", 403)
    except (NotFoundRecordsError, NotFoundUserError):
        logger.info("Пользователь для удаления не найден: user_id=%s", user_id)
        return JSONResponse(
            content={"detail": "Пользователь не найден"},
            status_code=404,
        )
    except (AdminApiUnavailableError, BadGatewayError):
        return admin_api_error_response()


@router.get("/admin/articles")
async def articles_menu(
    request: Request,
    user_id: int | None = Query(None),
    title: str | None = Query(None),
    article_id: int | None = Query(None),
    public_date: dt.date | None = Query(None),
):
    try:
        ensure_csrf_token(request)
        token = request.cookies.get("admin_access_token")
        params = {
            key: value
            for key, value in {
                "article_id": article_id,
                "title": title,
                "user_id": user_id,
                "public_date": public_date.isoformat() if public_date else None,
            }.items()
            if value not in (None, "")
        }
        articles = await get_admin_data(
            "GET", "/admin/articles", params, {"Authorization": f"Bearer {token}"}
        )
        return templates.TemplateResponse(
            request=request,
            name="admin/admin_articles.html",
            context={"articles": articles},
        )
    except (AdminApiUnavailableError, BadGatewayError):
        return admin_api_error_response()


@router.post("/admin/articles/{article_id}")
async def article_delete(
    request: Request,
    article_id: int,
    csrf_token: str = Form(...),
    cached_article_service: CachedArticleService = Depends(get_cached_article_service),
):
    try:
        await check_csrf_token(request, csrf_token)
        token = request.cookies.get("admin_access_token")
        await delete_admin_api(
            f"/admin/articles/{article_id}", {"Authorization": f"Bearer {token}"}
        )
        await cached_article_service.invalidate_article(article_id)
        logger.info("Администратор удалил статью: article_id=%s", article_id)
        return RedirectResponse("/admin/articles", status_code=303)
    except NotValidCsrfTokenError:
        return error_page(request, "Невалидный CSRF-токен", 403)
    except NotFoundRecordsError:
        logger.info("Статья для удаления не найдена: article_id=%s", article_id)
        return JSONResponse(
            content={"detail": "Статья не найдена"},
            status_code=404,
        )
    except (AdminApiUnavailableError, BadGatewayError):
        return admin_api_error_response()


@router.get("/admin/comments")
async def comments_menu(
    request: Request,
    user_id: int | None = Query(None),
    article_id: int | None = Query(None),
    public_date: dt.date | None = Query(None),
):
    try:
        ensure_csrf_token(request)
        token = request.cookies.get("admin_access_token")
        params = {
            key: value
            for key, value in {
                "article_id": article_id,
                "public_date": public_date.isoformat() if public_date else None,
                "user_id": user_id,
            }.items()
            if value not in (None, "")
        }
        comments = await get_admin_data(
            "GET", "/admin/comments", params, {"Authorization": f"Bearer {token}"}
        )
        return templates.TemplateResponse(
            request=request,
            name="admin/admin_comments.html",
            context={"comments": comments},
        )
    except (AdminApiUnavailableError, BadGatewayError):
        return admin_api_error_response()


@router.post("/admin/comments/{comment_id}")
async def comment_delete(
    request: Request,
    comment_id: int,
    csrf_token: str = Form(...),
    comment_service: CommentService = Depends(get_comment_service),
    cached_comment_service: CachedCommentService = Depends(get_cached_comment_service),
):
    try:
        await check_csrf_token(request, csrf_token)
        article_id = await comment_service.get_article_id(comment_id)
        token = request.cookies.get("admin_access_token")
        await delete_admin_api(
            f"/admin/comments/{comment_id}", {"Authorization": f"Bearer {token}"}
        )
        await cached_comment_service.invalidate_comments(article_id)
        logger.info("Администратор удалил комментарий: comment_id=%s", comment_id)
        return RedirectResponse("/admin/comments", status_code=303)
    except NotValidCsrfTokenError:
        return error_page(request, "Невалидный CSRF-токен", 403)
    except (NotFoundCommentError, NotFoundRecordsError):
        logger.info("Комментарий для удаления не найден: comment_id=%s", comment_id)
        return JSONResponse(
            content={"detail": "Комментарий не найден"},
            status_code=404,
        )
    except (AdminApiUnavailableError, BadGatewayError):
        return admin_api_error_response()
