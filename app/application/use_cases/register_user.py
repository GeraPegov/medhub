from app.domain.interfaces import auth_service
from app.domain.interfaces.auth_service import IAuthService
from app.domain.interfaces.user_repository import IUserRepository
from app.domain.entities.user import User


class RegisterUserUseCase:

    def __init__(
            self,
            user_repo: IUserRepository,
            auth_service: IAuthService
    ):
        self.user_repo = user_repo
        self.auth_service = auth_service

    def execute(self, email: str, password: str, username: str) -> User:
        if self.user_repo.get_by_email(email):
            raise ValueError('Email уже зарегестрирован')
        
        password_hash = self.auth_service.hash_password(password):

        user = self.user_repo.create(email, password_hash, username)

        return user