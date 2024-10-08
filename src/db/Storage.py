from abc import ABC, abstractmethod


class Storage(ABC):

    @abstractmethod
    async def open(self):
        pass

    @abstractmethod
    async def close(self):
        pass

    @abstractmethod
    async def create_schema(self) -> None:
        pass

    @abstractmethod
    async def purge_schema(self) -> None:
        pass
