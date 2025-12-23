from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.comment_service import CommentService
from app.domain.interfaces.commentRepositories import ICommentRepository
from app.domain.interfaces.user_repository import IUserRepository
from app.infrastructure.database.connection import get_db
from app.infrastructure.database.repositories.comment_repository import (
    CommentRepository,
)
from app.presentation.dependencies.auth import get_user_repository


def get_comment_repository(
        session: AsyncSession = Depends(get_db)
) -> ICommentRepository:
    return CommentRepository(session)

def get_comment_service(
        comment_repository: ICommentRepository = Depends(get_comment_repository),
        user_repository: IUserRepository = Depends(get_user_repository)
) -> CommentService:
    return CommentService(comment_repository, user_repository)
