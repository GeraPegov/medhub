from venv import logger

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from app.application.services.article_service import ArticleService
from app.application.services.comment_manager import CommentService
from app.application.services.user_service import UserService
from app.domain.entities.user import UserEntity
from app.infrastructure.database.repositories.cache_repository import CachedUser
from app.presentation.dependencies.articles_dependencies import get_article_manager
from app.presentation.dependencies.auth import get_user_service
from app.presentation.dependencies.cache import get_cache_user
from app.presentation.dependencies.comments import get_comment_manager
from app.presentation.dependencies.current_user import get_current_user

templates = Jinja2Templates('app/presentation/api/endpoints/templates/html')

router = APIRouter()


@router.get('/user/profile')
async def mine_profile(
    request: Request,
    user: UserEntity = Depends(get_current_user)
):
    logger.info(f' user {user}')
    return templates.TemplateResponse(
        'profile.html',
        {
        'request': request,
        'user': user
        }
    )


@router.get('/user/profile/{username}')
async def profile_another_user_by_username(
    request: Request,
    username: str,
    user_manager: UserService = Depends(get_user_service),
    auth: UserEntity = Depends(get_current_user)
):
    entity_user = await user_manager.get_by_username(username)
    logger.info(f'user username {entity_user.unique_username} ')
    logger.info(f'user username {auth.subscriptions} ')

    return templates.TemplateResponse(
        'profile.html',
        {
        'request': request,
        'user': entity_user,
        'auth': auth
        }
    )

@router.get('/user/profile/{unique_username}/articles')
async def articles(
    request: Request,
    unique_username: str,
    cache_manager: CachedUser = Depends(get_cache_user),
    article_service: ArticleService = Depends(get_article_manager),
    auth: UserEntity = Depends(get_current_user)
):
    user = await cache_manager.get_user(unique_username)
    logger.info(f'user if {user}')
    entity_articles = await article_service.list_user_articles(user.id)

    return templates.TemplateResponse(
        'profile.html',
        {
        'auth': auth,
        'request': request,
        'user': user,
        'articles': entity_articles
        }
    )

@router.get('/user/profile/{unique_username}/comments')
async def comments(
    request: Request,
    unique_username: str,
    cache_manager: CachedUser = Depends(get_cache_user),
    comment_manager: CommentService = Depends(get_comment_manager),
    auth: UserEntity = Depends(get_current_user)
):
    user = await cache_manager.get_user(unique_username)
    comments = await comment_manager.show_by_author(user.id)

    return templates.TemplateResponse(
        'profile.html',
        {
        'auth': auth,
        'request': request,
        'user': user,
        'comments': comments,
        'article': None
        }
    )

@router.post('/user/profile/{unique_username}/subscribe')
async def subscribe(
    unique_username: str,
    user_service: UserService = Depends(get_user_service),
    auth: UserEntity = Depends(get_current_user)
):
    await user_service.subscribe(
        subscriber_id=auth.id,
        author_unique_username=unique_username)


@router.get('/user/profile/{unique_username}/subscriptions')
async def subscriptions(
    request: Request,
    unique_username: str,
    user_service: UserService = Depends(get_user_service),
    auth: UserEntity = Depends(get_current_user),
    cache_manager: CachedUser = Depends(get_cache_user)
):
    user = await cache_manager.get_user(unique_username)
    subscriptions = await user_service.subscriptions(unique_username)
    logger.info(f'subscriberi {subscriptions}')

    return templates.TemplateResponse(
        'profile.html',
        {
        'auth': auth,
        'request': request,
        'user': user,
        'article': None,
        'subscriptions': subscriptions
        }
    )
