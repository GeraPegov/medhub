from venv import logger

from fastapi import Cookie, Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.infrastructure.database.connection import get_db
from app.infrastructure.database.repositories.user_repository import UserRepositopry
from app.infrastructure.security.auth_service import AuthService

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl='auth/login',
    tokenUrl='auth/login')


def get_auth_service() -> AuthService:
    """Зависимость для сервиса авторизаци"""
    return AuthService()

def get_user_repository(session: AsyncSession = Depends(get_db)) -> UserRepositopry:
    """Зависиммость для репозитория пользователя"""
    return UserRepositopry(session)

async def get_current_user(
        token = Cookie(None, alias='access_token'),
        auth_service: AuthService = Depends(get_auth_service),
        user_repo: UserRepositopry = Depends(get_user_repository)
) -> User | None:
    """Получение текущего пользователя из токена"""
    try:
        if not token:
            return None
        user_id = auth_service.verify_token(token)
        user = await user_repo.get_by_id(user_id)
        logger.info(f'user {user}')
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Пользователь не найден'
            )
        return user
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Невалидный токен',
            headers={'WWW-Authenticate': 'Bearer'}
        ) from None
