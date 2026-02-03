from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.register_user import UserRegistrationService
from app.application.services.security.auth_service import AuthService
from app.application.services.security.login_user import UserAuthenticationService
from app.application.services.user_service import UserService
from app.domain.interfaces.user_repository import IUserRepository
from app.infrastructure.database.connection import get_db
from app.infrastructure.database.repositories.user_repository import UserRepository


def get_auth_service() -> AuthService:
    return AuthService()


def get_user_repository(session: AsyncSession = Depends(get_db)) -> IUserRepository:
    return UserRepository(session)


def get_user_service(repository: IUserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(repository)


def get_auth_login(
        user_repo: UserRepository = Depends(get_user_repository),
        auth_service: AuthService = Depends(get_auth_service)
) -> UserAuthenticationService:
    return UserAuthenticationService(
        user_repo=user_repo,
        auth_service=auth_service
    )


def get_auth_registration(
        user_repo: UserRepository = Depends(get_user_repository),
        auth_service: AuthService = Depends(get_auth_service)
) -> UserRegistrationService:
    return UserRegistrationService(
        user_repo=user_repo,
        auth_service=auth_service
    )
