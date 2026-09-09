import logging

import httpx

logger = logging.getLogger(__name__)


class RateLimiterClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=2.0)  # 2 секунды таймаут

    async def check_limit(
        self, user_id: int, action: str, limit: int
    ) -> tuple[bool, int | None]:
        try:
            response = await self.client.post(
                f"{self.base_url}/check-limit",
                json={"user_id": user_id, "action": action, "limit": limit},
            )
        except httpx.HTTPError as error:
            logger.warning(
                "Rate limiter недоступен, проверка пропущена: user_id=%s action=%s error=%s",
                user_id,
                action,
                error,
            )
            return True, None

        try:
            data = response.json()
        except ValueError:
            logger.warning(
                "Rate limiter вернул невалидный JSON, проверка пропущена: "
                "user_id=%s action=%s status=%s",
                user_id,
                action,
                response.status_code,
            )
            return True, None

        if response.status_code == 200:
            return True, None
        if response.status_code == 429:
            return False, data.get("retry_after")

        logger.warning(
            "Rate limiter вернул неожиданный статус, проверка пропущена: "
            "user_id=%s action=%s status=%s",
            user_id,
            action,
            response.status_code,
        )
        return True, None

    async def close(self):
        await self.client.aclose()
