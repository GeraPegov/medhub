from fastapi import APIRouter, Depends, Request, Response
from fastapi.templating import Jinja2Templates

from app.application.services.article_service import ArticleService
from app.domain.entities.user import UserEntity
from app.presentation.dependencies.articles_dependencies import get_article_service
from app.presentation.dependencies.current_user import get_current_user

router = APIRouter()

templates = Jinja2Templates("app/presentation/api/endpoints/templates/html")


@router.get('/')
async def home(
    request: Request,
    auth: UserEntity = Depends(get_current_user),
    article_service: ArticleService = Depends(get_article_service)
) -> Response:
    articles = await article_service.show_all_articles()

    return templates.TemplateResponse(
        name='home.html', context={
            'auth': auth,
            'request': request,
            'articles': articles
            })
