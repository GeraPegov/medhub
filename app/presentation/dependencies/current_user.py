from fastapi import Cookie, Depends, HTTPException, status

from app.domain.entities.user import UserEntity
from app.infrastructure.database.repositories.cache_repository import CachedRepository
from app.infrastructure.security.auth_service import AuthService
from app.presentation.dependencies.auth import get_auth_service
from app.presentation.dependencies.cache import get_cache_repositories


async def get_current_user(
        token = Cookie(None, alias='access_token'),
        auth_service: AuthService = Depends(get_auth_service),
        cache_repo: CachedRepository = Depends(get_cache_repositories)
) -> UserEntity | None:
    """Получение текущего пользователя из токена"""
    try:
        if not token:
            return None
        user_id = auth_service.verify_token(token)
        user = await cache_repo.get_user(user_id)
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
