from fastapi import APIRouter, Depends, Form
from fastapi.responses import RedirectResponse

from app.application.services.comment_service import CommentService
from app.domain.entities.user import UserEntity
from app.presentation.dependencies.comments import get_comment_service
from app.presentation.dependencies.current_user import get_current_user

router = APIRouter()


@router.post("/comments/{article_id}/create")
async def create(
    article_id: int,
    content: str = Form(...),
    comment_service: CommentService = Depends(get_comment_service),
    current_user: UserEntity = Depends(get_current_user),
):
    await comment_service.create(
        article_id=article_id,
        content=content,
        user_id=current_user.user_id,
    )

    response = RedirectResponse(url=f"/article/{article_id}", status_code=303)

    return response


@router.post("/comments/{comment_id}/delete")
async def delete(
    comment_id: int,
    comment_service: CommentService = Depends(get_comment_service),
    current_user: UserEntity = Depends(get_current_user),
):
    article_id = await comment_service.delete(
        comment_id=comment_id,
        user_id=current_user.user_id,
    )

    response = RedirectResponse(url=f"/article/{article_id}", status_code=303)
    return response
