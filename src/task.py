import uuid
from abc import ABC, abstractmethod
from enum import Enum
from typing import Coroutine, Awaitable, Callable, Dict, Any, List
from uuid import uuid4, UUID

from trigger import Trigger


class TaskStatuses(str, Enum):
    base = 'base'
    destroyed = 'destroyed'


class Task(ABC):
    def __init__(self, trigger: Trigger):
        self._trigger = trigger
        self._status = TaskStatuses.base
        self._task_id = uuid4()

    @property
    def task_id(self) -> UUID:
        return self._task_id

    @property
    def status(self) -> TaskStatuses:
        return self._status

    @status.setter
    def status(self, value: TaskStatuses):
        self._status = value

    @property
    def trigger(self) -> Trigger:
        return self._trigger

    @abstractmethod
    async def execute(self):
        pass


class AsyncTask(Task):
    def __init__(self, trigger: Trigger, func: Callable, args=None, kwargs=None):
        super().__init__(trigger)
        self._coroutine = func
        self._args = args or list()
        self._kwargs = kwargs or dict()

    async def execute(self):
        return await self._coroutine(*self._args, **self._kwargs)
