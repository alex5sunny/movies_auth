from abc import ABC, abstractmethod


class Cache(ABC):

    @abstractmethod
    async def get(self, key) -> str:
        pass

    @abstractmethod
    async def put(self, key, val: str, timeout: int):
        pass

    @abstractmethod
    async def close(self):
        pass
