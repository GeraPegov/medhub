import httpx

class RateLimiterClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=2.0)  # 2 секунды таймаут

    async def check_limit(
        self,
        user_id: int,
        action: str,
        limit: int
    ) -> tuple[bool, int | None]:
        """
        Проверяет rate limit через Go сервис.

        Returns:
            (allowed, retry_after): allowed=True если можно выполнить действие,
                                     retry_after в секундах если лимит превышен
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/check-limit",
                json={
                    "user_id": user_id,
                    "action": action,
                    "limit": limit
                }
            )
            
            data = response.json()
            
            if response.status_code == 200:
                return True, None
            elif response.status_code == 429:
                return False, data.get("retry_after")
            else:
                # Если Go сервис недоступен — пропускаем проверку (graceful degradation)
                return True, None
                
        except Exception as e:
            # Логируем ошибку, но не блокируем пользователя
            print(f"Rate limiter error: {e}")
            return True, None
    
    async def close(self):
        await self.client.aclose()