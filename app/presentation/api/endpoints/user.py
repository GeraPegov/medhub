from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.application.services.article_service import ArticleService
from app.application.services.comment_manager import CommentService
from app.domain.entities.user import UserEntity
from app.infrastructure.database.repositories.cache_repository import CachedUser
from app.presentation.dependencies.articles_dependencies import get_article_manager
from app.presentation.dependencies.cache import get_cache_user
from app.presentation.dependencies.comments import get_comment_manager
from app.presentation.dependencies.current_user import get_current_user

templates = Jinja2Templates('app/presentation/api/endpoints/templates/html')

router = APIRouter()

@router.get('/user/articles')
async def only_user_articles(
    request: Request,
    user: UserEntity = Depends(get_current_user),
    manager: ArticleService = Depends(get_article_manager)
):
    if not user:
        return RedirectResponse(url='/login')

    list_articles = await manager.list_user_articles(user.id)

    return templates.TemplateResponse(
        'user_articles.html',
        {'request': request, 'articles': list_articles}
    )

@router.get('/user/profile')
async def mine_profile(
    request: Request,
    user: UserEntity = Depends(get_current_user)
):
    return templates.TemplateResponse(
        'profile.html',
        {
        'request': request,
        'user': user
        }
    )

@router.get('/user/profile/{client_id}')
async def profile_another_user(
    request: Request,
    client_id: int,
    user_manager: CachedUser = Depends(get_cache_user)
):
    entity_user = await user_manager.get_user(client_id)

    return templates.TemplateResponse(
        'profile.html',
        {
        'request': request,
        'user': entity_user
        }
    )

@router.get('/user/profile/{client_id}/articles')
async def articles(
    request: Request,
    client_id: int,
    user_manager: CachedUser = Depends(get_cache_user),
    article_service: ArticleService = Depends(get_article_manager),
    auth: UserEntity = Depends(get_current_user)
):
    user = await user_manager.get_user(client_id)
    entity_articles = await article_service.list_user_articles(client_id)

    return templates.TemplateResponse(
        'profile.html',
        {
        'auth': auth,
        'request': request,
        'user': user,
        'articles': entity_articles
        }
    )

@router.get('/user/profile/{client_id}/comments')
async def comments(
    request: Request,
    client_id: int,
    user_manager: CachedUser = Depends(get_cache_user),
    comment_manager: CommentService = Depends(get_comment_manager)
):
    user = await user_manager.get_user(client_id)
    comments = await comment_manager.show_by_author(client_id)

    return templates.TemplateResponse(
        'profile.html',
        {
        'request': request,
        'user': user,
        'comments': comments
        }
    )
