import secrets

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
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
from app.presentation.dependencies.current_user import get_current_user

templates = Jinja2Templates("app/presentation/api/endpoints/templates/html")

router = APIRouter()


def ensure_csrf_token(request: Request) -> None:
    if "csrf_token" not in request.session:
        request.session["csrf_token"] = secrets.token_urlsafe(32)


@router.get("/user/profile/{unique_username}")
async def profile(
    request: Request,
    unique_username: str,
    cached_user_service: CachedUserService = Depends(get_cached_user_service),
    current_user: UserEntity | None = Depends(get_current_user),
):
    ensure_csrf_token(request)
    profile_user = await cached_user_service.get_user(unique_username)
    return templates.TemplateResponse(
        request=request,
        name="profile.html",
        context={"user": profile_user, "auth": current_user},
    )


@router.get("/user/profile/{unique_username}/articles")
async def articles(
    request: Request,
    unique_username: str,
    cached_user_service: CachedUserService = Depends(get_cached_user_service),
    article_service: ArticleService = Depends(get_article_service),
    current_user: UserEntity | None = Depends(get_current_user),
):
    ensure_csrf_token(request)
    profile_user = await cached_user_service.get_user(unique_username)
    articles = await article_service.list_user_articles(profile_user.user_id)
    return templates.TemplateResponse(
        request=request,
        name="profile.html",
        context={
            "auth": current_user,
            "user": profile_user,
            "articles": articles,
        },
    )


@router.get("/user/profile/{unique_username}/comments")
async def comments(
    request: Request,
    unique_username: str,
    cached_user_service: CachedUserService = Depends(get_cached_user_service),
    comment_service: CommentService = Depends(get_comment_service),
    current_user: UserEntity | None = Depends(get_current_user),
):
    ensure_csrf_token(request)
    profile_user = await cached_user_service.get_user(unique_username)
    comments = await comment_service.show_by_author(profile_user.user_id)

    return templates.TemplateResponse(
        request=request,
        name="profile.html",
        context={
            "auth": current_user,
            "user": profile_user,
            "comments": comments,
            "article": None,
        },
    )


@router.post("/user/profile/{unique_username}/subscribe")
async def subscribe(
    unique_username: str,
    user_service: UserService = Depends(get_user_service),
    current_user: UserEntity = Depends(get_current_user),
    cached_user_service: CachedUserService = Depends(get_cached_user_service),
):
    user = await user_service.subscribe(
        subscriber_id=current_user.user_id,
        author_unique_username=unique_username,
    )
    await cached_user_service.update_user(user)
    return RedirectResponse(url=f"/user/profile/{unique_username}", status_code=303)


@router.post("/user/profile/{unique_username}/unsubscribe")
async def unsubscribe(
    unique_username: str,
    user_service: UserService = Depends(get_user_service),
    current_user: UserEntity = Depends(get_current_user),
    cached_user_service: CachedUserService = Depends(get_cached_user_service),
):
    user = await user_service.unsubscribe(
        subscriber_id=current_user.user_id,
        author_unique_username=unique_username,
    )
    await cached_user_service.update_user(user)
    return RedirectResponse(url=f"/user/profile/{unique_username}", status_code=303)


@router.get("/user/profile/{unique_username}/subscriptions")
async def subscriptions(
    request: Request,
    unique_username: str,
    current_user: UserEntity | None = Depends(get_current_user),
    cached_user_service: CachedUserService = Depends(get_cached_user_service),
):
    ensure_csrf_token(request)
    profile_user = await cached_user_service.get_user(unique_username)

    return templates.TemplateResponse(
        request=request,
        name="profile.html",
        context={
            "auth": current_user,
            "user": profile_user,
            "article": None,
            "subscriptions": profile_user.subscriptions,
        },
    )


@router.get("/user/profile/{unique_username}/liked")
async def liked(
    request: Request,
    current_user: UserEntity = Depends(get_current_user),
    article_service: ArticleService = Depends(get_article_service),
):
    ensure_csrf_token(request)
    articles = await article_service.liked_articles_by_user(current_user.user_id)
    return templates.TemplateResponse(
        request=request,
        name="profile.html",
        context={
            "auth": current_user,
            "user": current_user,
            "articles": articles,
        },
    )


@router.get("/user/profile/{unique_username}/delete")
async def delete_profile(
    current_user: UserEntity = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    await user_service.delete_profile(current_user.user_id)

    return RedirectResponse(url="/", status_code=303)
