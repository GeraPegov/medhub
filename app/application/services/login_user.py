from app.domain.interfaces.auth_service import IAuthService
from app.domain.interfaces.user_repository import IUserRepository


class UserAuthenticationService:

    """Сценарий входа"""

    def __init__(
            self,
            auth_service: IAuthService,
            user_repo: IUserRepository
    ):
        self.user_repo = user_repo
        self.auth_service = auth_service

    async def execute(self, email: str, password: str) -> str:
        """Возвращает JWT токен"""
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise ValueError('Неверный email или пароль')

        if not self.auth_service.verify_password(password, user.password_hash):
            raise ValueError('НЕверный email или пароль')

        token = self.auth_service.create_access_token(user.id)

        return token
