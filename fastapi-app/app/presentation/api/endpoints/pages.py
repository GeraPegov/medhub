from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.application.services.article_service import ArticleService
from app.domain.entities.user import UserEntity
from app.presentation.dependencies.articles_dependencies import get_article_service
from app.presentation.dependencies.current_user import get_current_user

templates = Jinja2Templates("app/presentation/api/endpoints/templates/html")
router = APIRouter()


@router.get("/")
async def home(
    request: Request,
    current_user: UserEntity | None = Depends(get_current_user),
    article_service: ArticleService = Depends(get_article_service),
) -> Response:
    articles = await article_service.show_all_articles()

    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={"auth": current_user, "articles": articles},
    )


@router.get("/exit")
async def exit():
    response = RedirectResponse(url="/", status_code=303)

    response.delete_cookie(key="access_token")

    return response
