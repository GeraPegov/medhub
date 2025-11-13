from app.domain.entities.user import User
from app.domain.interfaces.auth_service import IAuthService
from app.domain.interfaces.user_repository import IUserRepository
from app.domain.logging import logger


class UserRegistrationService:
    """Сценарий регистрации"""
    def __init__(
            self,
            user_repo: IUserRepository,
            auth_service: IAuthService
    ):
        self.user_repo = user_repo
        self.auth_service = auth_service

    async def execute(self, email: str, password: str, username: str) -> User:
        if await self.user_repo.get_by_email(email):
            raise ValueError('Email уже зарегестрирован')

        password_hash = self.auth_service.hash_password(password)
        logger.info(f'password hash : {password_hash}')
        user = await self.user_repo.create(email, password_hash, username)
        logger.info(f'user in use_cases : {user}')
        return user

