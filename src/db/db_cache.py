from typing import Optional

from db.cache import Cache

cache: Optional[Cache] = None


async def get_cache() -> Cache:
    return cache
