from abc import ABC, abstractmethod
from datetime import timedelta, datetime

from exceptions import TaskDestroy


class Trigger(ABC):
    def __init__(self, timeout: timedelta = timedelta(seconds=0.01)):
        if not timeout:
            self._timeout = timedelta(seconds=0.01)
        else:
            self._timeout = timeout
        self._last_check: datetime | None = None

    @abstractmethod
    async def is_done(self) -> bool:
        pass

    async def check(self) -> bool:
        if self._last_check and self._last_check + self._timeout <= datetime.now():
            self._last_check = datetime.now()
            return await self.is_done()
        elif not self._last_check:
            self._last_check = datetime.now()
            return await self.is_done()
        return False

class DateTrigger(Trigger):
    def __init__(self, run_date: datetime, timeout: timedelta = None):
        super().__init__(timeout=timeout)
        self._run_date = run_date

    async def is_done(self) -> bool:

        is_done = datetime.now() >= self._run_date
        if is_done:
            raise TaskDestroy
        return False


class OuterTrigger(Trigger):
    def __init__(self, timeout: timedelta = None):
        super().__init__(timeout=timeout)
        self._is_done = False
        self._is_destroy: bool = True

    async def trigger(self, is_destroy: bool = True):
        if self._is_done:
            raise TaskDestroy
        self._is_done = True
        self._is_destroy = is_destroy

    async def is_done(self) -> bool:
        if self._is_done and self._is_destroy:
            raise TaskDestroy
        if self._is_done:
            self._is_done = False
            return True
        return False


class IntervalTrigger(Trigger):

    def __init__(self,  interval: timedelta, repeat: int | None = None, is_infinity: bool = False, timeout: timedelta = None):
        super().__init__(timeout=timeout)
        self._interval = interval
        self._run_date = (datetime.now() + interval)
        self._is_infinity = is_infinity
        self._repeat = repeat

    async def is_done(self) -> bool:
        is_done = self._run_date <= datetime.now()
        if not is_done:
            return False
        if self._is_infinity:
            self._run_date += self._interval
            return True
        if self._repeat and self._repeat > 1:
            self._repeat -= 1
            self._run_date += self._interval
            return True
        raise TaskDestroy
