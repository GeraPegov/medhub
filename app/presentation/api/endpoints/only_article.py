from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.application.dto.articleCreate_dto import ArticleCreateDTO
from app.application.services.article_service import ArticleService
from app.application.services.cache_service import CachedServiceArticle
from app.application.services.comment_service import CommentService
from app.domain.entities.user import UserEntity
from app.presentation.dependencies.articles_dependencies import get_article_manager
from app.presentation.dependencies.cache import get_cache_article
from app.presentation.dependencies.comments import get_comment_service
from app.presentation.dependencies.current_user import get_current_user
from app.presentation.dependencies.parse_article import parse_article_form

templates = Jinja2Templates('app/presentation/api/endpoints/templates/html')

router = APIRouter()

@router.get('/article/{article_id}')
async def show_article(
    request: Request,
    article_id: int,
    cache_service: CachedServiceArticle = Depends(get_cache_article),
    comment_service: CommentService = Depends(get_comment_service),
    auth: UserEntity = Depends(get_current_user)
):
    if auth:
        article = await cache_service.get_cache_article(article_id, auth.user_id)
    else:
        article = await cache_service.get_cache_article(article_id)

    comments = await comment_service.show_by_article(article_id)
    print(article)
    return templates.TemplateResponse(
        'only_article.html',
        {'request': request,
         'article': article,
         'comments': comments,
         'auth': auth
        }
    )


@router.post('/article/delete/{article_id}')
async def delete_article(
    article_id: int,
    auth: UserEntity = Depends(get_current_user),
    article_service: ArticleService = Depends(get_article_manager),
):
    await article_service.delete_article(article_id)

    return RedirectResponse(
        status_code=303,
        url=f'/user/profile/{auth.unique_username}'
    )


@router.get('/article/change/{article_id}')
async def change_article(
    request: Request,
    article_id: int,
    articles_service: ArticleService = Depends(get_article_manager),
):
    articles = await articles_service.get_by_id(article_id)

    return templates.TemplateResponse(
        'change_article.html',
        {
        'request': request,
        'article': articles
        }
    )


@router.post('/article/change/{article_id}/access')
async def create_article_access(
    request: Request,
    article_id: int,
    dto: ArticleCreateDTO = Depends(parse_article_form),
    article_service: ArticleService = Depends(get_article_manager),
    auth: UserEntity = Depends(get_current_user)
):
    article = await article_service.change_article(dto, article_id)

    return templates.TemplateResponse(
        'only_article.html',
        {
        'auth': auth,
        'request': request,
        'article': article
        }
    )


@router.post('/article/{reaction}/{article_id}')
async def like(
    request: Request,
    article_id: int,
    reaction: str,
    auth: UserEntity = Depends(get_current_user),
    article_service: ArticleService = Depends(get_article_manager),
    comment_service: CommentService = Depends(get_comment_service)
):
    like = await article_service.set_reaction(
        article_id,
        auth.user_id,
        reaction
    )
    comments = await comment_service.show_by_article(article_id)
    return templates.TemplateResponse(
        'only_article.html',
        {'request': request,
         'article': like,
         'comments': comments,
         'auth': auth
        }
    )
