from __future__ import annotations
import asyncio
from asyncio import LifoQueue
from datetime import timedelta, datetime

from exceptions import TaskDestroy
from store import MemoryStore, Store
from task import Task, AsyncTask, TaskStatuses
from trigger import IntervalTrigger, DateTrigger, OuterTrigger


class Scheduler:
    def __init__(self, store: Store = MemoryStore()):

        self._store = store
        self._executing_tasks: LifoQueue = LifoQueue()

    async def start(self):
        await asyncio.gather(self._execute_tasks(), self._check_triggers())


    async def add(self, task: Task):
        await self._store.put(task)

    async def _execute_tasks(self):
        while True:
            task = await self._executing_tasks.get()
            await task.execute()

    async def _check_triggers(self):
        while True:
            await asyncio.sleep(0)
            task = await self._store.get()
            try:
                is_done = await task.trigger.check()
                if not is_done:
                    await self._store.put(task)

                    await asyncio.sleep(0)
                    continue
            except TaskDestroy:
                is_done = True
                task.status = TaskStatuses.destroyed
            if is_done:
                await self._executing_tasks.put(task)

            if task.status != TaskStatuses.destroyed:
                await self._store.put(task)
            await asyncio.sleep(0)


async def say_hello():
    print('hello')


async def main():
    scheduler = Scheduler()

    trigger = IntervalTrigger(interval=timedelta(seconds=1), repeat=5)
    await scheduler.add(AsyncTask(trigger=trigger, func=say_hello))
    await scheduler.start()


asyncio.run(main())
