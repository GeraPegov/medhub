from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from app.application.services.article_service import ArticleService
from app.domain.entities.user import UserEntity
from app.presentation.dependencies.articles_dependencies import get_article_manager
from app.presentation.dependencies.current_user import get_current_user

templates = Jinja2Templates('app/presentation/api/endpoints/templates/html')

router = APIRouter()

@router.get('/user/articles')
async def only_user_articles(
    request: Request,
    user: UserEntity = Depends(get_current_user),
    manager: ArticleService = Depends(get_article_manager)
):
    list_articles = await manager.list_user_articles(user.id)

    return templates.TemplateResponse(
        'user_articles.html',
        {'request': request, 'articles': list_articles}
    )

@router.get('/user/profile')
async def profile(
    request: Request,
    user: UserEntity = Depends(get_current_user)
):
    pass
