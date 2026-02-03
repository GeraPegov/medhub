from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import UserEntity


class IUserRepository(ABC):
    @abstractmethod
    def __init__(self, session: AsyncSession):
        pass

    @abstractmethod
    async def get_by_id(self, user_id: int) -> UserEntity | None:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> UserEntity | None:
        pass

    @abstractmethod
    async def create(self, user_data: dict) -> UserEntity:
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> UserEntity | None:
        pass

    @abstractmethod
    async def subscribe(self, subscriber_id, author_unique_username) -> bool:
        pass

    @abstractmethod
    async def unsubscribe(self, subscriber_id, author_unique_username) -> bool:
        pass

    @abstractmethod
    async def delete_profile(self, user_id):
        pass
