from abc import ABC, abstractmethod

from app.domain.entities.user import UserEntity


class IUserRepository(ABC):

    @abstractmethod
    async def get_by_id(self, user_id: int) -> UserEntity | None:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> UserEntity | None:
        pass

    @abstractmethod
    async def create(self, email: str, password_hash: str, username: str) -> UserEntity:
        pass
