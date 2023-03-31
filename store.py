from abc import ABC, abstractmethod
from asyncio import LifoQueue
from typing import List

from task import Task


class Store(ABC):

    @abstractmethod
    async def put(self, task: Task):
        pass

    @abstractmethod
    async def get(self) -> Task:
        pass


class MemoryStore(Store):
    def __init__(self):
        self._tasks: LifoQueue[Task] = LifoQueue()

    async def put(self, task: Task):
        await self._tasks.put(task)

    async def get(self) -> Task:
        return await self._tasks.get()
