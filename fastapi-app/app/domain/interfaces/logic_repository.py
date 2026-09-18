from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession


class ILogicRepository(ABC):
    @abstractmethod
    def __init__(self, session: AsyncSession):
        pass

    @abstractmethod
    async def can_publish_article_today(self, user_id) -> None:
        pass

    @abstractmethod
    async def can_publish_comment_today(self, user_id, article_id) -> None:
        pass
