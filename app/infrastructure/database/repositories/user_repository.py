
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import UserEntity
from app.domain.interfaces.user_repository import IUserRepository
from app.domain.logging import logger
from app.infrastructure.database.models.client import Client


class UserRepository(IUserRepository):
    """Реализация репозитория пользователей"""
    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_by_id(self, user_id: int) -> UserEntity | None:
        user = await self.session.execute(
            select(Client)
            .where(Client.id==user_id)
        )
        user_model = user.scalar_one_or_none()
        if not user_model:
            return None
        return await self._to_entity(user_model)


    async def get_by_email(self, email: str) -> UserEntity | None:
        user = await self.session.execute(
            select(Client)
            .where(Client.email==email)
        )
        user_model = user.scalar_one_or_none()
        if not user_model:
            return None
        return await self._to_entity(user_model)

    async def create(self, email: str, password_hash: str, username: str, nickname: str) -> UserEntity:
        logger.info('start create')
        user_model = Client(
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


    async def _to_entity(self, model: Client) -> UserEntity:
        """Преобразование SQLAlchemy модели в доменную сущность"""
        return UserEntity(
            id=model.id,
            email=model.email,
            username=model.unique_username,
            password_hash=model.password_hash,
            nickname=model.nickname
        )
