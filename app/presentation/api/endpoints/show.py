from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from app.application.services.article_manager import ArticleService
from app.domain.logging import logger
from app.presentation.dependencies.articles_dependencies import get_article_manager

templates = Jinja2Templates('app/presentation/api/endpoints/templates')

router = APIRouter()

@router.get('/article/{article_id}')
async def show(
    request: Request,
    article_id: int,
    manager: ArticleService = Depends(get_article_manager)
):
    logger.info(f'article_id = {article_id}')
    article = await manager.show(article_id)

    return templates.TemplateResponse(
        'show.html',
        {'request': request,
         'article': article
        }
    )

# @router.post('/article/comment')
# async def comment(
#     article_id: int = Form(...),

# )
