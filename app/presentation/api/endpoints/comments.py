
from fastapi import APIRouter, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.application.services.comment_manager import CommentService
from app.domain.entities.user import UserEntity
from app.domain.logging import logger
from app.presentation.dependencies.comments import get_comment_manager
from app.presentation.dependencies.current_user import get_current_user

templates = Jinja2Templates('app/presentation/api/endpoints/templates')

router = APIRouter()

@router.post('/comments/{article_id}/create')
async def create(
    article_id: int,
    content: str = Form(...),
    comment_manager: CommentService = Depends(get_comment_manager),
    user: UserEntity = Depends(get_current_user)
):
    logger.info(f'start comment endpoint, article_id = {article_id}, content={content}, user={user.id}')
    await comment_manager.create(
        article_id=article_id,
        content=content,
        author_id=user.id
    )
    response = RedirectResponse(
        url=f'/article/{article_id}',
        status_code=303
    )

    return response

@router.post('/comments/{comment_id}/delete')
async def delete(
    comment_id: int,
    comment_manager: CommentService = Depends(get_comment_manager),
    user: UserEntity = Depends(get_current_user),
):
    result = await comment_manager.delete(
        comment_id=comment_id,
        author_id=user.id
    )
    response = RedirectResponse(
        url=f'/article/{result}',
        status_code=303
    )
    return response
