from typing import Optional

from db.Cache import Cache

cache: Optional[Cache] = None


async def get_cache() -> Cache:
    return cache
