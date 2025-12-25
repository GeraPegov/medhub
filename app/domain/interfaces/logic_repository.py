from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession


class ILogicRepository(ABC):
    @abstractmethod
    def __init__(self, session: AsyncSession):
        pass

    @abstractmethod
    async def check_limited(self, user_id):
        pass
