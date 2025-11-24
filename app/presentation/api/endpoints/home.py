from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from app.application.services.article_service import ArticleService
from app.domain.entities.user import UserEntity
from app.domain.logging import logger
from app.presentation.dependencies.articles_dependencies import get_article_manager
from app.presentation.dependencies.current_user import get_current_user

router = APIRouter()

templates = Jinja2Templates("app/presentation/api/endpoints/templates")


@router.get('/')
async def full(
    request: Request,
    user: UserEntity = Depends(get_current_user),
    manager: ArticleService = Depends(get_article_manager)
):
    login = False
    if not user:
        login = True
    articles = await manager.show_all_articles()
    logger.info(f'endpoint HOME articles = {articles}')
    return templates.TemplateResponse(
        name='home.html', context={
            'login': login,
            'request': request,
            'articles': articles
            })
