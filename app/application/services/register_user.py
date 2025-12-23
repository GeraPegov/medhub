from app.application.dto.articleAuth_dto import UserDTO
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

    async def execute(self, user_data: UserDTO) -> UserEntity | None:
        if await self.user_repo.get_by_email(user_data.email):
            return None
        password_hash = self.auth_service.hash_password(user_data.password)
        mapping = {
            'unique_username': user_data.username,
            'password_hash': password_hash,
            'email': user_data.email,
            'nickname': user_data.nickname
        }
        user = await self.user_repo.create(mapping)
        return user

