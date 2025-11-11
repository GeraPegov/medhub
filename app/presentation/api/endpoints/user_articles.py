from fastapi import APIRouter, Depends, Form, Request
from fastapi.templating import Jinja2Templates

from app.application.services.article_manager import ArticleManager
from app.domain.entities.user import User
from app.domain.logging import logger
from app.presentation.dependencies.auth import get_current_user
from app.presentation.dependencies.depends_submit_article import get_article_manager

templates = Jinja2Templates('app/presentation/api/endpoints/templates')

router = APIRouter()

@router.get('/articles/user')
async def user_articles(
    request: Request,
    user: User = Depends(get_current_user),
    manager: ArticleManager = Depends(get_article_manager)
):
    list_articles = await manager.list_user_articles(user.id)

    return templates.TemplateResponse(
        'user_articles.html',
        {'request': request, 'articles': list_articles}
    )

@router.post('/articles/user/delete')
async def delete_article(
    request: Request,
    manager: ArticleManager = Depends(get_article_manager),
    user: ArticleManager = Depends(get_article_manager),
    article_id: str = Form(...)
):
    logger.info(f'id {article_id}, {type(article_id)}')
    if not user:
        return 'Авторизуйтесь'
    title = await manager.delete_article(int(article_id))
    return {'access': title}
