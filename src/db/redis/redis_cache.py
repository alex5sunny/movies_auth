from typing import Optional

from core.config import settings
from db.cache import Cache
from redis.asyncio import Redis


class RedisCache(Cache):

    def __init__(self):
        self.redis = Redis(host=settings.redis_host, port=settings.redis_port)

    async def get(self, key) -> Optional[str]:
        return await self.redis.get(key)

    async def put(self, key, val: str, timeout: int):
        await self.redis.set(key, val, settings.cache_expire_in_seconds)

    async def close(self):
        if self.redis:
            await self.redis.close()
