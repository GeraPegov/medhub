from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.application.services.article_service import ArticleService
from app.domain.entities.user import UserEntity
from app.domain.logging import logger
from app.presentation.dependencies.articles_dependencies import get_article_manager
from app.presentation.dependencies.current_user import get_current_user

templates = Jinja2Templates('app/presentation/api/endpoints/templates')

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

@router.post('/user/delete')
async def delete_article(
    request: Request,
    manager: ArticleService = Depends(get_article_manager),
    user: UserEntity = Depends(get_current_user),
    article_id: str = Form(...)
):
    logger.info(f'id {article_id}, {type(article_id)}')
    if not user:
        return 'Авторизуйтесь'
    title = await manager.delete_article(int(article_id))
    response = RedirectResponse(
        url='/user/articles'
    )
    return response

@router.get('/user/profile')
async def profile(
    request: Request,
    user: UserEntity = Depends(get_current_user)
):
    pass
