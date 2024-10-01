from typing import Optional

from core.config import settings
from db.Cache import Cache
from redis.asyncio import Redis


class RedisCache(Cache):

    def __init__(self, host: str, port: int):
        self.redis = Redis(host=host, port=port)

    async def get(self, key) -> Optional[str]:
        return await self.redis.get(key)

    async def put(self, key, val: str, timeout: int):
        await self.redis.set(key, val, settings.cache_expire_in_seconds)

    async def close(self):
        if self.redis:
            await self.redis.close()
