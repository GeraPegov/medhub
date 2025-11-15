
from fastapi import APIRouter, Depends, Form
from fastapi.templating import Jinja2Templates

from app.application.services.comment_manager import CommentService
from app.domain.entities.user import UserEntity
from app.domain.logging import logger
from app.presentation.dependencies.auth import get_current_user
from app.presentation.dependencies.comments import get_comment_manager

templates = Jinja2Templates('app/presentation/api/endpoints/templates')

router = APIRouter()

@router.post('/articles/{article_id}/comments')
async def create(
    article_id: int,
    content: str = Form(...),
    comment_manager: CommentService = Depends(get_comment_manager),
    user: UserEntity = Depends(get_current_user)
):
    logger.info(f'start comment endpoint, article_id = {article_id}, content={content}, user={user.id}')
    create_comment = await comment_manager.create(
        article_id=article_id,
        content=content,
        author_id=user.id
    )
    return 'okay'
