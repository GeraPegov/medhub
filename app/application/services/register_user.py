from app.domain.entities.user import UserEntity
from app.domain.interfaces.auth_service import IAuthService
from app.domain.interfaces.user_repository import IUserRepository


class UserRegistrationService:
    """Сценарий регистрации"""
    def __init__(
            self,
            user_repo: IUserRepository,
            auth_service: IAuthService
    ):
        self.user_repo = user_repo
        self.auth_service = auth_service

    async def execute(self, email: str, password: str, username: str, nickname: str) -> UserEntity | None:
        if await self.user_repo.get_by_email(email):
            return None

        password_hash = self.auth_service.hash_password(password)
        user = await self.user_repo.create(email, password_hash, username, nickname)
        return user

