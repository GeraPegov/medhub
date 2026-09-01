import secrets

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.application.services.article_service import ArticleService
from app.application.services.cache_service import CachedUserService
from app.application.services.comment_service import CommentService
from app.application.services.user_service import UserService
from app.domain.entities.user import UserEntity
from app.presentation.dependencies.articles_dependencies import get_article_service
from app.presentation.dependencies.auth import get_user_service
from app.presentation.dependencies.cache import get_cached_user_service
from app.presentation.dependencies.comments import get_comment_service
from app.presentation.dependencies.current_user import get_auth_service, get_current_user
from app.domain.exceptions import NotFoundUserError

templates = Jinja2Templates("app/presentation/api/endpoints/templates/html")

router = APIRouter()


@router.get("/user/profile/{unique_username}")
async def profile(
    request: Request,
    unique_username: str,
    cache_service: CachedUserService = Depends(get_cached_user_service),
    auth: UserEntity = Depends(get_current_user),
):
    try:
        if "csrf_token" not in request.session:
            request.session['csrf_token'] = secrets.token_urlsafe(32)
        user = await cache_service.get_user(unique_username)
        print(auth.subscriptions)
        return templates.TemplateResponse(
            request=request,
            name="profile.html",
            context={"user": user, "auth": auth},
        )
    except NotFoundUserError:
        return JSONResponse(
            content="Не нашли пользователя",
            status_code=404
        )


@router.get("/user/profile/{unique_username}/articles")
async def articles(
    request: Request,
    unique_username: str,
    cache_service: CachedUserService = Depends(get_cached_user_service),
    article_service: ArticleService = Depends(get_article_service),
    auth: UserEntity = Depends(get_current_user),
):
    try:
        user = await cache_service.get_user(unique_username)
        articles = await article_service.list_user_articles(user.user_id)
        return templates.TemplateResponse(
            request=request,
            name="profile.html",
            context={"auth": auth, "user": user, "articles": articles},
        )
    except NotFoundUserError:
        return JSONResponse(
            content="Не нашли пользователя",
            status_code=404
        )


@router.get("/user/profile/{unique_username}/comments")
async def comments(
    request: Request,
    unique_username: str,
    cache_service: CachedUserService = Depends(get_cached_user_service),
    comment_service: CommentService = Depends(get_comment_service),
    auth: UserEntity = Depends(get_current_user),
):
    try:
        user = await cache_service.get_user(unique_username)
        comments = await comment_service.show_by_author(user.user_id)

        return templates.TemplateResponse(
            request=request,
            name="profile.html",
            context={"auth": auth, "user": user, "comments": comments, "article": None},
        )
    except NotFoundUserError:
        return JSONResponse(
            content="Не нашли пользователя",
            status_code=404
        )


@router.post("/user/profile/{unique_username}/subscribe")
async def subscribe(
    unique_username: str,
    user_service: UserService = Depends(get_user_service),
    auth: UserEntity = Depends(get_current_user),
    cache_service: CachedUserService = Depends(get_cached_user_service),
):
    try:
        if auth.user_id is None:
            return RedirectResponse("/auth", status_code=303)
        user = await user_service.subscribe(
            subscriber_id=auth.user_id, username_to_follow=unique_username
        )
        if user is not None:
            await cache_service.update_user(user)
        return RedirectResponse(url=f"/user/profile/{unique_username}", status_code=303)
    except NotFoundUserError:
        return RedirectResponse("/auth", status_code=303)


@router.post("/user/profile/{unique_username}/unsubscribe")
async def unsubscribe(
    unique_username: str,
    user_service: UserService = Depends(get_user_service),
    auth: UserEntity = Depends(get_current_user),
    cache_service: CachedUserService = Depends(get_cached_user_service),
):
    try:
        user = await user_service.unsubscribe(
            subscriber_id=auth.user_id, author_unique_username=unique_username
        )
        if user is not None:
            await cache_service.update_user(user)
        return RedirectResponse(url=f"/user/profile/{unique_username}", status_code=303)
    except NotFoundUserError:
        return RedirectResponse("/auth", status_code=303)


@router.get("/user/profile/{unique_username}/subscriptions")
async def subscriptions(
    request: Request,
    unique_username: str,
    auth: UserEntity = Depends(get_current_user),
    cache_service: CachedUserService = Depends(get_cached_user_service),
):
    try:
        user = await cache_service.get_user(unique_username)

        return templates.TemplateResponse(
            request=request,
            name="profile.html",
            context={
                "auth": auth,
                "user": user,
                "article": None,
                "subscriptions": user.subscriptions,
            },
        )
    except NotFoundUserError:
        return JSONResponse("Пользователь не найден", status_code=404)


@router.get("/user/profile/{unique_username}/liked")
async def liked(
    request: Request,
    unique_username: str,
    auth: UserEntity = Depends(get_current_user),
    article_service: ArticleService = Depends(get_article_service),
    user_service: UserService = Depends(get_user_service)
):
    try:
        user = await user_service.get_by_username(unique_username)
        if user:
            articles = await article_service.liked_articles_by_user(user.user_id)
        return templates.TemplateResponse(
            request=request,
            name="profile.html",
            context={"auth": auth, "user": user, "articles": articles},
        )
    except NotFoundUserError:
        return JSONResponse("Пользователь не найден", status_code=404)


@router.get("/user/profile/{unique_username}/delete")
async def delete_profile(
    auth: UserEntity = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    try:
        await user_service.delete_profile(auth.user_id)
        return RedirectResponse(url="/", status_code=303)
    except NotFoundUserError:
        return JSONResponse("Пользователь не найден", status_code=404)
