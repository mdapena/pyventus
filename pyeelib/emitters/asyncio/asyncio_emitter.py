import asyncio
from asyncio import Task
from typing import Set, Callable, ParamSpec, Coroutine, Type

from pyeelib.emitters import EventEmitter
from pyeelib.linkers import EventLinker

P = ParamSpec("P")


class AsyncioEmitter(EventEmitter):

    def __init__(self, event_linker: Type[EventLinker] = EventLinker):
        super().__init__(event_linker=event_linker)
        self._background_tasks: Set[Task] = set()

    def _execute(self, *args: P.args, callback: Callable[P, Coroutine], **kwargs: P.kwargs) -> None:
        task: Task = asyncio.create_task(callback(*args, **kwargs))

        def done_callback(t: Task):
            self._background_tasks.remove(task)

            if t.cancelled():
                return

            exception: BaseException = t.exception()

            if exception:
                self.emit(exception)

        task.add_done_callback(done_callback)
        self._background_tasks.add(task)
