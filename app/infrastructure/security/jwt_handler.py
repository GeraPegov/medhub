from datetime import datetime, timedelta

from jose import JWTError, jwt

from app.infrastructure.config import settings


class JWTHandler:
    """Работа с JWT токенами"""

    def create_token(self, user_id: int) -> str:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

        payload = {
            "sub": str(user_id),
            "exp": expire
        }

        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    def verify_token(self, token: str) -> int:
        '''Возвращает user_id или выбрасывает исключение'''

        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            user_id = int(payload.get("sub"))
            return user_id
        except JWTError:
            raise ValueError('Невалидный токен')
