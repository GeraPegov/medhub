from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession


class ICommentRepository(ABC):

    @abstractmethod
    def __init__(self, session: AsyncSession):
        pass

    @abstractmethod
    async def show(self, article_id: int):
        pass

    @abstractmethod
    async def create(self, article_id: int, author_id: int, content: str):
        pass

    @abstractmethod
    async def delete(self, comment_id: int):
        pass
