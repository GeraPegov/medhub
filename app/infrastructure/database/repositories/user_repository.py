
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import UserEntity
from app.domain.interfaces.user_repository import IUserRepository
from app.domain.logging import logger
from app.infrastructure.database.models.user import User


class UserRepository(IUserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_by_id(self, user_id: int) -> UserEntity | None:
        user = await self.session.execute(
            select(User)
            .where(User.id==user_id)
        )
        user_model = user.scalar_one_or_none()
        if not user_model:
            return None
        return await self._to_entity(user_model)


    async def get_by_email(self, email: str) -> UserEntity | None:
        user = await self.session.execute(
            select(User)
            .where(User.email==email)
        )
        user_model = user.scalar_one_or_none()
        if not user_model:
            return None
        return await self._to_entity(user_model)

    async def get_by_username(self, unique_username: str) -> UserEntity | None:
        try:
            user = await self.session.execute(
                select(User)
                .where(User.unique_username==unique_username)
            )
            user_model = user.scalar_one_or_none()
            if not user_model:
                return None
            return await self._to_entity(user_model)
        except Exception:
            await self.session.rollback()
            raise

    async def create(self, email: str, password_hash: str, username: str, nickname: str) -> UserEntity:
        user_model = User(
            email=email,
            password_hash=password_hash,
            nickname=nickname,
            unique_username=username
        )
        logger.info('create user_model')
        self.session.add(user_model)
        await self.session.commit()
        await self.session.refresh(user_model)
        logger.info('save new db model')
        return await self._to_entity(user_model)

    async def subscribe(self, subscribe_id, author_unique_username):
        result = await self.session.execute(
            select(User)
            .where(User.id==subscribe_id)
        )

        user = result.scalar_one()

        user.subscriptions.append(author_unique_username)

        await self.session.commit()
        await self.session.refresh(user)

        return 'okay'

    async def subscriptions(self, unique_username):
        result = await self.session.execute(
            select(User.subscriptions)
            .where(User.unique_username==unique_username)
        )

        subscriptions = result.scalar_one()

        return subscriptions


    async def _to_entity(self, model: User) -> UserEntity:
        """Преобразование SQLAlchemy модели в доменную сущность"""
        return UserEntity(
            id=model.id,
            email=model.email,
            unique_username=model.unique_username,
            nickname=model.nickname,
            password_hash=model.password_hash,
            subscriptions=model.subscriptions
        )
