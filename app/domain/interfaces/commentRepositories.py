from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.comment import CommentEntity


class ICommentRepository(ABC):

    @abstractmethod
    def __init__(self, session: AsyncSession):
        pass

    @abstractmethod
    async def show_by_article(self, article_id: int) -> list[CommentEntity] | None:
        pass

    @abstractmethod
    async def show_by_author(self, author_id: int) -> list[CommentEntity] | None:
        pass

    @abstractmethod
    async def create(self, article_id: int, author_id: int, content: str):
        pass

    @abstractmethod
    async def delete(self, comment_id: int):
        pass
