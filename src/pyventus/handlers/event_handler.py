from asyncio import iscoroutinefunction, to_thread
from datetime import datetime
from inspect import isfunction, isclass, isbuiltin, ismethod
from typing import Callable, Any, final, ParamSpec, TypeAlias

from ..core.exceptions import PyventusException
from ..core.loggers import StdOutLogger

P = ParamSpec("P")
""" A generic type to represent the parameter names and types of the callbacks. """

EventCallbackType: TypeAlias = Callable[P, Any]
""" Type alias for the main callback invoked when an associated event occurs. """

SuccessCallbackType: TypeAlias = Callable[..., Any]
""" Type alias for a callback invoked upon successful completion of an event. """

FailureCallbackType: TypeAlias = Callable[[Exception], Any]
""" Type alias for a callback invoked when event processing fails. """


@final
class EventHandler:
    """
    A class that encapsulates event callbacks.

    The `EventHandler` class provides a mechanism for managing and executing callbacks
    when an event occurs.

    **Important**: The `__call__` method of the `EventHandler` class is always an async
    method and returns a `Coroutine`. It should never be treated as a sync function.

    **Note:** The event handler can be invoked by calling the instance as a function
    and passing the necessary arguments. This class is not intended to be subclassed
    or created manually. It is used internally to encapsulate the callbacks
    associated with an event.
    """

    # Event handler attributes
    __slots__ = (
        "_once",
        "_force_async",
        "_event_callback",
        "_success_callback",
        "_failure_callback",
        "_is_event_callback_async",
        "_is_success_callback_async",
        "_is_failure_callback_async",
        "_timestamp",
    )

    @property
    def once(self) -> bool:
        """
        Determines if the handler is a one-time handler.
        :return: `True` if the event handler is a one-time handler; otherwise, `False`.
        """
        return self._once

    @property
    def force_async(self) -> bool:
        """
        Determines whether all callbacks are forced to run asynchronously.
        :return: A boolean value indicating whether synchronous callbacks will be converted to run
            asynchronously in a thread pool, using the `asyncio.to_thread` function. Returns `True`
            if callbacks will be converted to run asynchronously, and `False` if callbacks will
            run synchronously or asynchronously as defined.
        """
        return self._force_async

    @property
    def timestamp(self) -> datetime:
        """
        Gets the timestamp of when the event handler was registered.
        :return: The timestamp of when this handler was registered.
        """
        return self._timestamp

    @staticmethod
    def get_callback_name(
        callback: EventCallbackType | SuccessCallbackType | FailureCallbackType | None,  # type: ignore[type-arg]
    ) -> str:
        if callback is not None and hasattr(callback, "__name__"):
            return callback.__name__
        elif callback is not None and hasattr(callback, "__class__"):
            return callback.__class__.__name__
        else:
            return "None"

    @staticmethod
    def validate_callback(
        callback: EventCallbackType | SuccessCallbackType | FailureCallbackType,  # type: ignore[type-arg]
    ) -> None:
        """
        Validates that the provided callback is a compatible callable.
        :param callback: The callback to validate.
        :return: None
        :raises PyventusException: If the callback is not a callable object.
        """
        if not callable(callback):
            raise PyventusException(
                f"'{callback.__name__ if hasattr(callback, '__name__') else callback}' is not a callable object."
            )

    @staticmethod
    def is_async(
        callback: EventCallbackType | SuccessCallbackType | FailureCallbackType,  # type: ignore[type-arg]
    ) -> bool:
        """
        Checks if a callback is an asynchronous function or method.
        :param callback: The callback to check.
        :return: `True` if the callback is an asynchronous function or method,
            `False` otherwise.
        """
        if ismethod(callback) or isfunction(callback) or isbuiltin(callback):
            return iscoroutinefunction(callback)
        elif not isclass(callback) and hasattr(callback, "__call__"):  # a callable class instance
            return iscoroutinefunction(callback.__call__)
        else:
            raise PyventusException("Expected a callable or a string, but got: {0}".format(callback))

    def __init__(
        self,
        once: bool,
        force_async: bool,
        event_callback: EventCallbackType,  # type: ignore[type-arg]
        success_callback: SuccessCallbackType | None = None,
        failure_callback: FailureCallbackType | None = None,
    ) -> None:
        """
        Initializes an instance of the `EventHandler` class.
        :param once: Specifies if the event handler is a one-time handler. If set to `True`,
            the handler will be invoked once when the event occurs and then automatically
            unsubscribed. If set to `False`, the handler can be invoked multiple times
            until explicitly unsubscribed.
        :param force_async: Whether to force all callbacks to run asynchronously.
            If `True`, synchronous callbacks will be converted to run asynchronously in a
            thread pool, using the `asyncio.to_thread` function. If `False`, callbacks will
            run synchronously or asynchronously as defined.
        :param event_callback: The callback to be executed when the event occurs.
        :param success_callback: The callback to be executed when the event execution
            completes successfully.
        :param failure_callback: The callback to be executed when the event execution fails.
        :raises PyventusException: If callbacks are invalid.
        """
        # Validate callbacks
        EventHandler.validate_callback(callback=event_callback)

        if success_callback is not None:
            EventHandler.validate_callback(callback=success_callback)

        if failure_callback is not None:
            EventHandler.validate_callback(callback=failure_callback)

        # Store flags
        self._once: bool = once
        self._force_async: bool = force_async

        # Store callbacks
        self._event_callback: EventCallbackType = event_callback  # type: ignore[type-arg]
        self._success_callback: SuccessCallbackType | None = success_callback
        self._failure_callback: FailureCallbackType | None = failure_callback

        # Callback flags
        self._is_event_callback_async: bool = EventHandler.is_async(event_callback)
        self._is_success_callback_async: bool | None = (
            EventHandler.is_async(success_callback) if success_callback else None
        )
        self._is_failure_callback_async: bool | None = (
            EventHandler.is_async(failure_callback) if failure_callback else None
        )

        # Set timestamp
        self._timestamp: datetime = datetime.now()

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> None:
        """
        Executes the event handler by invoking the associated callbacks.
        :param args: Variable-length argument list.
        :param kwargs: Arbitrary keyword arguments.
        :return: Coroutine
        """
        # Callback results
        results: Any | None = None

        try:
            # Invokes the event callback.
            if self._is_event_callback_async:
                results = await self._event_callback(*args, **kwargs)
            elif self._force_async:
                results = await to_thread(self._event_callback, *args, **kwargs)
            else:
                results = self._event_callback(*args, **kwargs)
        except Exception as exception:
            # Log the exception with error level
            StdOutLogger.error(name=f"{self.__class__.__name__}", action="Exception:", msg=f"{exception}")

            # Invokes failure callback.
            if self._failure_callback:
                if self._is_failure_callback_async:
                    await self._failure_callback(exception)
                elif self._force_async:
                    await to_thread(self._failure_callback, exception)
                else:
                    self._failure_callback(exception)
        else:
            # Invokes success callback.
            if self._success_callback:
                if self._is_success_callback_async:
                    if results is None:
                        await self._success_callback()
                    else:
                        await self._success_callback(results)
                elif self._force_async:
                    if results is None:
                        await to_thread(self._success_callback)
                    else:
                        await to_thread(self._success_callback, results)
                else:
                    if results is None:
                        self._success_callback()
                    else:
                        self._success_callback(results)

    def __str__(self) -> str:
        return (
            f"Once: {self.once} | "
            f"Force Async: {self.force_async} | "
            f"Event Callback: '{EventHandler.get_callback_name(callback=self._event_callback)}'"
            f"{' (Async)' if self._is_event_callback_async else ' (Sync)'} | "
            f"Success Callback: '{EventHandler.get_callback_name(callback=self._success_callback)}'"
            f"{(' (Async)' if self._is_success_callback_async else ' (Sync)') if self._success_callback else ''} | "
            f"Failure Callback: '{EventHandler.get_callback_name(callback=self._failure_callback)}'"
            f"{(' (Async)' if self._is_failure_callback_async else ' (Sync)') if self._failure_callback else ''} | "
            f"Timestamp: {self.timestamp.strftime('%Y-%m-%d %I:%M:%S %p')}"
        )
