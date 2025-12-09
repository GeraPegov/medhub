from fastapi import Cookie, Depends

from app.domain.entities.user import UserEntity
from app.infrastructure.database.repositories.cache_repository import CachedUser
from app.infrastructure.security.auth_service import AuthService
from app.presentation.dependencies.auth import get_auth_service
from app.presentation.dependencies.cache import get_cache_user


async def get_current_user(
        token = Cookie(None, alias='access_token'),
        auth_service: AuthService = Depends(get_auth_service),
        cache_repo: CachedUser = Depends(get_cache_user)
) -> UserEntity | None:
    if not token:
        return None
    user_id = auth_service.verify_token(token)
    user = await cache_repo.get_user(user_id)
    if not user:
        return None
    return user
