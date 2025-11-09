from abc import ABC, abstractmethod

from app.domain.entities.user import User


class IUserRepository(ABC):

    @abstractmethod
    async def get_by_id(self, user_id: int) -> User | None:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        pass

    @abstractmethod
    async def create(self, email: str, password_hash: str, username: str) -> User:
        pass
