
from fastapi import APIRouter, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.application.services.comment_service import CommentService
from app.domain.entities.user import UserEntity
from app.presentation.dependencies.comments import get_comment_service
from app.presentation.dependencies.current_user import get_current_user

templates = Jinja2Templates('app/presentation/api/endpoints/templates')

router = APIRouter()

@router.post('/comments/{article_id}/create')
async def create(
    article_id: int,
    content: str = Form(...),
    comment_manager: CommentService = Depends(get_comment_service),
    user: UserEntity = Depends(get_current_user)
):
    await comment_manager.create(
        article_id=article_id,
        content=content,
        author_id=user.user_id
    )

    response = RedirectResponse(
        url=f'/article/{article_id}',
        status_code=303
    )

    return response

@router.post('/comments/{comment_id}/delete')
async def delete(
    comment_id: int,
    comment_manager: CommentService = Depends(get_comment_service),
    auth: UserEntity = Depends(get_current_user),
):
    result = await comment_manager.delete(
        comment_id=comment_id,
        author_id=auth.user_id
    )

    response = RedirectResponse(
        url=f'/article/{result}',
        status_code=303
    )
    return response
