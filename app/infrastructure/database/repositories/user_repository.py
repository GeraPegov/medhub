
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import UserEntity
from app.domain.interfaces.user_repository import IUserRepository
from app.infrastructure.database.models.user import User


class UserRepository(IUserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_by_id(self, user_id: int) -> UserEntity | None:
        user_db = await self.session.execute(
            select(User)
            .where(User.id==user_id)
        )
        user = user_db.scalar_one_or_none()

        return await self._to_entity(user) if user else None


    async def get_by_email(self, email: str) -> UserEntity | None:
        user_db = await self.session.execute(
            select(User)
            .where(User.email==email)
        )
        user = user_db.scalar_one_or_none()

        return await self._to_entity(user) if user else None


    async def get_by_username(self, unique_username: str) -> UserEntity | None:
        user_db = await self.session.execute(
            select(User)
            .where(User.unique_username==unique_username)
        )
        user = user_db.scalar_one_or_none()
        return await self._to_entity(user) if user else None


    async def create(self, email: str, password_hash: str, username: str, nickname: str) -> UserEntity:
        user = User(
            email=email,
            password_hash=password_hash,
            nickname=nickname,
            unique_username=username
        )

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        return await self._to_entity(user)


    async def subscribe(self, subscribe_id, author_unique_username) -> UserEntity | None:
        result = await self.session.execute(
            select(User)
            .where(User.id==subscribe_id)
        )

        user = result.scalar_one_or_none()

        if not user:
            return None

        if author_unique_username not in user.subscriptions:
            user.subscriptions.append(author_unique_username)
            await self.session.commit()
            await self.session.refresh(user)
            return await self._to_entity(user)
        return None


    async def unsubscribe(self, subscribe_id, author_unique_username) -> UserEntity | None:
        result = await self.session.execute(
            select(User)
            .where(User.id==subscribe_id)
        )

        user = result.scalar_one_or_none()

        if not user:
            return None

        if author_unique_username in user.subscriptions:
            user.subscriptions.remove(author_unique_username)
            await self.session.commit()
            await self.session.refresh(user)
            return await self._to_entity(user)

        return None


    async def _to_entity(self, model: User) -> UserEntity:

        return UserEntity(
            user_id=model.id,
            email=model.email,
            unique_username=model.unique_username,
            nickname=model.nickname,
            password_hash=model.password_hash,
            subscriptions=model.subscriptions
        )
