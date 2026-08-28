import secrets
from typing import Literal

from fastapi import APIRouter, Depends, Form, Header, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.application.dto.article_create_dto import ArticleCreateDTO
from app.application.services.article_service import ArticleService
from app.application.services.cache_service import CachedArticleService
from app.application.services.comment_service import CommentService
from app.domain.entities.user import UserEntity
from app.domain.exceptions import (
    NotFoundArticleError,
    NotValidCsrfTokenError,
    ReactionAlreadyExistsError,
)
from app.presentation.api.endpoints.auth import check_csrf_token
from app.presentation.dependencies.articles_dependencies import get_article_service
from app.presentation.dependencies.cache import get_cached_article_service
from app.presentation.dependencies.comments import get_comment_service
from app.presentation.dependencies.current_user import get_current_user
from app.presentation.dependencies.parse_article import parse_article_form

templates = Jinja2Templates("app/presentation/api/endpoints/templates/html")

router = APIRouter()


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


@router.get("/article/{article_id:int}")
async def show_article(
    request: Request,
    article_id: int,
    cached_article_service: CachedArticleService = Depends(get_cached_article_service),
    comment_service: CommentService = Depends(get_comment_service),
    current_user: UserEntity | None = Depends(get_current_user),
):
    ensure_csrf_token(request)

    try:
        article = await cached_article_service.get_article(article_id)
    except NotFoundArticleError:
        return error_page(request, "Статья не найдена", 404)

    await cached_article_service.increment_view_counter(article_id)
    comments = await comment_service.list_by_article_id(article_id)

    return templates.TemplateResponse(
        request=request,
        name="only_article.html",
        context={
            "article": article,
            "comments": comments,
            "auth": current_user,
        },
    )


@router.post("/article/delete/{article_id}")
async def delete_article(
    request: Request,
    article_id: int,
    csrf_token: str = Form(...),
    current_user: UserEntity | None = Depends(get_current_user),
    article_service: ArticleService = Depends(get_article_service),
    cached_article_service: CachedArticleService = Depends(get_cached_article_service),
):
    if current_user is None:
        return RedirectResponse(url="/auth", status_code=303)

    try:
        await check_csrf_token(request, csrf_token)
        await article_service.delete_article(article_id, current_user.user_id)
        await cached_article_service.delete_article(article_id)
        return RedirectResponse(
            status_code=303, url=f"/user/profile/{current_user.unique_username}"
        )
    except NotFoundArticleError:
        return error_page(request, "Статья не найдена", 404)
    except NotValidCsrfTokenError:
        return error_page(request, "Невалидный CSRF-токен", 403)


@router.get("/article/change/{article_id}")
async def preliminary_change(
    request: Request,
    article_id: int,
    article_service: ArticleService = Depends(get_article_service),
    current_user: UserEntity | None = Depends(get_current_user),
):
    if current_user is None:
        return RedirectResponse(url="/auth", status_code=303)

    ensure_csrf_token(request)
    try:
        article = await article_service.get_by_id(article_id)
        if article.user_id != current_user.user_id:
            return error_page(request, "Недостаточно прав для изменения статьи", 403)

        return templates.TemplateResponse(
            request=request,
            name="change_article.html",
            context={"article": article, "auth": current_user},
        )
    except NotFoundArticleError:
        return error_page(request, "Статья не найдена", 404)


@router.post("/article/change/{article_id}/access")
async def final_change(
    request: Request,
    article_id: int,
    csrf_token: str = Form(...),
    dto: ArticleCreateDTO = Depends(parse_article_form),
    article_service: ArticleService = Depends(get_article_service),
    current_user: UserEntity | None = Depends(get_current_user),
    cached_article_service: CachedArticleService = Depends(get_cached_article_service),
):
    if current_user is None:
        return RedirectResponse(url="/auth", status_code=303)

    try:
        await check_csrf_token(request, csrf_token)
        article = await article_service.change_article(
            dto,
            article_id,
            current_user.user_id,
        )
        await cached_article_service.update_article(article)

        return RedirectResponse(
            url=f"/article/{article.article_id}",
            status_code=303,
        )

    except NotValidCsrfTokenError:
        return error_page(request, "Невалидный CSRF-токен", 403)
    except NotFoundArticleError:
        return error_page(request, "Статья не найдена", 404)


@router.post("/article/{reaction}/{article_id:int}")
async def add_reaction(
    request: Request,
    article_id: int,
    reaction: Literal["like", "dislike"],
    csrf_token: str = Header(..., alias="X-CSRF-Token"),
    current_user: UserEntity | None = Depends(get_current_user),
    cached_article_service: CachedArticleService = Depends(get_cached_article_service),
):
    if current_user is None:
        return JSONResponse(
            {"error": "Для реакции необходимо войти"},
            status_code=401,
        )

    try:
        await check_csrf_token(request, csrf_token)
        return await cached_article_service.add_reaction(
            article_id=article_id,
            user_id=current_user.user_id,
            reaction=reaction,
        )
    except NotValidCsrfTokenError:
        return JSONResponse(
            {"error": "Невалидный CSRF-токен"},
            status_code=403,
        )
    except NotFoundArticleError:
        return JSONResponse(
            {"error": "Статья не найдена"},
            status_code=404,
        )
    except ReactionAlreadyExistsError:
        return JSONResponse(
            {"error": "Вы уже поставили реакцию на эту статью"},
            status_code=409,
        )


@router.get("/articles/search")
async def search(
    request: Request,
    current_user: UserEntity | None = Depends(get_current_user),
):
    return templates.TemplateResponse(
        request=request,
        name="search.html",
        context={"auth": current_user},
    )


@router.get("/articles/search/title", response_class=HTMLResponse)
async def get_title(
    request: Request,
    query: str = Query(..., min_length=2),
    article_service: ArticleService = Depends(get_article_service),
    current_user: UserEntity | None = Depends(get_current_user),
):
    articles = await article_service.search_by_title(query)

    return templates.TemplateResponse(
        request=request,
        name="search.html",
        context={"articles": articles, "title": query, "auth": current_user},
    )


@router.get("/articles/search/category/{category}", response_class=HTMLResponse)
async def get_category(
    request: Request,
    category: str,
    article_service: ArticleService = Depends(get_article_service),
    current_user: UserEntity | None = Depends(get_current_user),
):
    articles = await article_service.search_by_category(category)

    return templates.TemplateResponse(
        request=request,
        name="search.html",
        context={"articles": articles, "auth": current_user},
    )


@router.get("/article/submit", response_class=HTMLResponse)
async def add(
    request: Request,
    current_user: UserEntity | None = Depends(get_current_user),
):
    if current_user is None:
        return RedirectResponse(url="/auth", status_code=303)

    ensure_csrf_token(request)
    return templates.TemplateResponse(
        request=request,
        name="submit_article.html",
        context={"auth": current_user},
    )


@router.post("/article/submit/add")
async def create_article(
    request: Request,
    csrf_token: str = Form(...),
    dto: ArticleCreateDTO = Depends(parse_article_form),
    article_service: ArticleService = Depends(get_article_service),
    current_user: UserEntity | None = Depends(get_current_user),
):
    if current_user is None:
        return RedirectResponse(url="/auth", status_code=303)

    try:
        await check_csrf_token(request, csrf_token)
        article = await article_service.submit_article(dto, current_user.user_id)
        if article is None:
            return error_page(
                request,
                "Достигнут дневной лимит публикаций",
                429,
            )
        return RedirectResponse(
            url=f"/user/profile/{current_user.unique_username}", status_code=303
        )
    except NotValidCsrfTokenError:
        return error_page(request, "Невалидный CSRF-токен", 403)
