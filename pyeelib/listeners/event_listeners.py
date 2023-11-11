import asyncio
from typing import ParamSpec, Callable, Coroutine

P = ParamSpec("P")


class EventListener:

    @property
    def ttl(self) -> int | None:
        return self._ttl

    @property
    def is_async(self) -> bool:
        return self._is_async

    def __init__(self, callback: Callable[P, Coroutine | None], ttl: int | None = None) -> None:
        if ttl is not None and ttl < 1:
            raise ValueError("EventListener ttl must be greater than 0")

        self._is_async: bool = asyncio.iscoroutinefunction(callback)
        self._callback: Callable[P, None] = callback
        self._ttl: int | None = ttl

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> None:
        if self.ttl is not None:
            if self.ttl > 0:
                self._ttl -= 1
            else:
                return

        if self._is_async:
            await self._callback(*args, **kwargs)
        else:
            await asyncio.to_thread(self._callback, *args, **kwargs)
