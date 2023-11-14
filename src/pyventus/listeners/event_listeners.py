import asyncio
from sys import version_info
from typing import Callable, Any

from src.pyventus.core.exceptions import PyventusException

if version_info >= (3, 10):  # pragma: no cover
    from typing import ParamSpec
else:  # pragma: no cover
    from typing_extensions import ParamSpec

P = ParamSpec("P")
""" A generic type to represent the parameter names and types of the callback function. """


class EventListener:
    """
    A class that encapsulates event callback functions.

    The `EventListener` class provides a mechanism for managing event listeners and their
    associated callback functions.

    **Note**: The event listener can be invoked by calling the instance as a function
    and passing the necessary arguments. If the event listener has the `once` property
    set to `True`, it will only be invoked once when the event occurs. If `once` is set
    to `False` (default), the event listener will be invoked every time the event occurs
    until explicitly unsubscribed. Also, this class is not intended to be subclassed or
    created manually. It is used internally to encapsulate the callback function associated
    with an event listener.

    **Important**: The `__call__` method of the `EventListener` class is always an async method
    and returns a coroutine. It should never be treated as a synchronous function.
    """

    # Event listener attributes
    __slots__ = ('_is_async', '_callback', '_once')

    @property
    def once(self) -> bool:
        """
        Determines if the listener is a one-time listener.
        :return: `True` if the listener is a one-time listener; otherwise, `False`.
        """
        return self._once

    def __init__(self, callback: Callable[P, Any], once: bool = False) -> None:
        """
        Initializes an instance of the `EventListener` class.
        :param callback: The callback function to be executed when the event occurs.
        :param once: Specifies if the listener is a one-time listener. If set to `True`,
            the listener will be invoked once when the event occurs and then automatically
            unsubscribed. If set to `False` (default), the listener can be invoked multiple
            times until explicitly unsubscribed.
        :raise PyventusException: If `callback` is not a callable.
        """
        if not callable(callback):
            raise PyventusException("EventListener 'callback' must be a callable.")

        self._is_async: bool = asyncio.iscoroutinefunction(callback)
        """ A boolean flag indicating whether the callback function is asynchronous (coroutine). """

        self._callback: Callable[P, Any] = callback
        """ The callback function to be executed when the event occurs. """

        self._once: bool = once
        """ Specifies if the listener is a one-time listener. """

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> None:
        """
        Executes the event listener by invoking the associated callback function with the provided arguments.
        :param args: Variable-length argument list.
        :param kwargs: Arbitrary keyword arguments.
        :return: Coroutine
        """
        # Check callback: await if asynchronous, thread and await if synchronous
        if self._is_async:
            await self._callback(*args, **kwargs)
        else:
            await asyncio.to_thread(self._callback, *args, **kwargs)
