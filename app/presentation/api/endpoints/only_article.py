from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from app.application.services.article_service import ArticleService
from app.application.services.comment_manager import CommentService
from app.domain.entities.user import UserEntity
from app.presentation.dependencies.articles_dependencies import get_article_manager
from app.presentation.dependencies.auth import get_current_user
from app.presentation.dependencies.comments import get_comment_manager

templates = Jinja2Templates('app/presentation/api/endpoints/templates')

router = APIRouter()

@router.get('/article/{article_id}')
async def show_article(
    request: Request,
    article_id: int,
    article_manager: ArticleService = Depends(get_article_manager),
    comment_manager: CommentService = Depends(get_comment_manager),
    user: UserEntity = Depends(get_current_user)
):
    article = await article_manager.only_article(article_id)
    comments = await comment_manager.show_comment(article_id)

    return templates.TemplateResponse(
        'only_article.html',
        {'request': request,
         'article': article,
         'comments': comments,
         'user': user
        }
    )
