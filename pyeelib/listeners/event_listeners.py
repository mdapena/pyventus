import asyncio
from sys import version_info
from typing import Callable, Any

if version_info >= (3, 10):
    from typing import ParamSpec
else:
    from typing_extensions import ParamSpec

P = ParamSpec("P")
""" A generic type to represent the parameter names and types of the callback function. """


class EventListener:
    """
    A class that encapsulates event callback functions.

    The `EventListener` class provides a mechanism for managing event listeners and their associated callback functions.

    The event listener can be triggered by invoking the instance as a function and passing the necessary arguments.
    If the event listener has a TTL value set, it will be decremented each time the listener is triggered.
    Once the TTL reaches zero, the event listener will no longer be triggered.
    """

    @property
    def ttl(self) -> int | None:
        """
        Retrieves the Time to Listen (TTL) value for the event listener.
        :return: The TTL value representing the maximum number of times the listener can be triggered.
        """
        return self._ttl

    @property
    def is_async(self) -> bool:
        """
        Determines if the callback function is asynchronous (coroutine).
        :return: `True` if the callback is asynchronous; otherwise, `False`.
        """
        return self._is_async

    def __init__(self, callback: Callable[P, Any], ttl: int | None = None) -> None:
        """
        Initializes an instance of the `EventListener` class.
        :param callback: The callback function to be executed when the event occurs.
        :param ttl: The Time to Listen (TTL) value for the event listener. Defaults to None.
        :raise ValueError: If `ttl` is not `None` and is less than 1.
        """
        if ttl is not None and ttl < 1:
            raise ValueError("EventListener 'ttl' must be greater than 0.")

        self._is_async: bool = asyncio.iscoroutinefunction(callback)
        """ A boolean flag indicating whether the callback function is asynchronous (coroutine). """

        self._callback: Callable[P, Any] = callback
        """ The callback function to be executed when the event occurs. """

        self._ttl: int | None = ttl
        """ The maximum number of times the listener can be triggered. (Time to Listen). """

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> None:
        """
        Executes the event listener by invoking the associated callback function with the provided arguments.
        :param args: Variable-length argument list.
        :param kwargs: Arbitrary keyword arguments.
        :return: Coroutine
        """
        # Check ttl: return if zero, decrement if greater than zero
        if self.ttl is not None:
            if self.ttl > 0:
                self._ttl -= 1
            else:
                return

        # Check callback: await if asynchronous, thread and await if synchronous
        if self._is_async:
            await self._callback(*args, **kwargs)
        else:
            await asyncio.to_thread(self._callback, *args, **kwargs)
