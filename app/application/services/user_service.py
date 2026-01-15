

from app.domain.entities.user import UserEntity
from app.domain.interfaces.user_repository import IUserRepository


class UserService:
    def __init__(self, repository: IUserRepository):
        self.repository = repository

    async def get_by_id(self, user_id: int) -> UserEntity | None:
        return await self.repository.get_by_id(user_id)

    async def get_by_email(self, email: str) -> UserEntity | None:
        return await self.repository.get_by_email(email)

    async def create(self, email: str, password_hash: str, username: str, nickname: str) -> UserEntity:
        mapping = {
            'password_hash': password_hash,
            'username': username,
            'email': email,
            'nickname': nickname
        }
        return await self.repository.create(mapping)

    async def get_by_username(self, username: str) -> UserEntity | None:
        return await self.repository.get_by_username(username)

    async def subscribe(self, subscriber_id, author_unique_username):
        return await self.repository.subscribe(subscriber_id, author_unique_username)

    async def unsubscribe(self, subscriber_id, author_unique_username):
        return await self.repository.unsubscribe(subscriber_id, author_unique_username)

    async def delete_profile(self, user_id):
        return await self.repository.delete_profile(user_id)