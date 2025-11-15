from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.comment_manager import CommentService
from app.domain.interfaces.commentRepositories import ICommentRepository
from app.infrastructure.database.connection import get_db
from app.infrastructure.database.repositories.comment_repository import (
    CommentRepository,
)


def get_comment_repository(
        session: AsyncSession = Depends(get_db)
) -> ICommentRepository:
    return CommentRepository(session)

def get_comment_manager(
        repository: ICommentRepository = Depends(get_comment_repository)
) -> CommentService:
    return CommentService(repository)
