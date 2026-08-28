from fastapi import Cookie, Depends

from app.application.services.cache_service import CachedUserService
from app.application.services.security.auth_service import AuthService
from app.domain.entities.user import UserEntity
from app.presentation.dependencies.auth import get_auth_service
from app.presentation.dependencies.cache import get_cached_user_service


async def get_current_user(
    access_token=Cookie(None, alias="access_token"),
    auth_service: AuthService = Depends(get_auth_service),
    cached_user_service: CachedUserService = Depends(get_cached_user_service),
) -> UserEntity | None:
    if not access_token:
        return None
    user_id = auth_service.verify_token(access_token)
    if not user_id:
        return None
    user = await cached_user_service.get_user(user_id)
    return user
