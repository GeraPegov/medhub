
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.domain.interfaces.user_repository import IUserRepository
from app.domain.logging import logger
from app.infrastructure.database.models.user import UserModel


class UserRepositopry(IUserRepository):
    """Реализация репозитория пользователей"""
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> User | None:
        user = await self.session.execute(
            select(UserModel)
            .where(UserModel.id==user_id)
        )
        user_model = user.scalar_one_or_none()
        if not user_model:
            return None
        return await self._to_entity(user_model)

    async def get_by_email(self, email: str) -> User | None:
        logger.info('start repository for user_repository')
        user = await self.session.execute(
            select(UserModel)
            .where(UserModel.email==email)
        )
        user_model = user.scalar_one_or_none()
        if not user_model:
            return None
        return await self._to_entity(user_model)

    async def create(self, email: str, password_hash: str, username: str) -> User:
        logger.info('start create repositories')
        user_model = UserModel(
            email=email,
            password_hash=password_hash,
            username=username
        )

        self.session.add(user_model)
        await self.session.commit()
        await self.session.refresh(user_model)
        logger.info(f'start user_model in repository {user_model}')
        return await self._to_entity(user_model)

    async def _to_entity(self, model: User) -> User:
        """Преобразование SQLAlchemy модели в доменную сущность"""
        return User(
            id=model.id,
            email=model.email,
            username=model.username,
            password_hash=model.password_hash,
        )
