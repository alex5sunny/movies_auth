from abc import ABC, abstractmethod


class Storage(ABC):

    @abstractmethod
    async def open(self):
        pass

    @abstractmethod
    async def close(self):
        pass
