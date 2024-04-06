from asyncio import iscoroutinefunction, to_thread
from datetime import datetime
from inspect import isfunction, isclass, isbuiltin, ismethod
from typing import Callable, Any, final, ParamSpec, TypeAlias

from ..core.exceptions import PyventusException
from ..core.loggers import StdOutLogger

P = ParamSpec("P")
"""A generic type representing the names and types of the event callback parameters."""

EventCallbackType: TypeAlias = Callable[P, Any]
"""Type alias for the event callback invoked when the associated event occurs."""

SuccessCallbackType: TypeAlias = Callable[..., Any]
"""Type alias for the callback invoked upon successful completion of the event."""

FailureCallbackType: TypeAlias = Callable[[Exception], Any]
"""Type alias for the callback invoked when the event processing fails."""


@final
class EventHandler:
    """
    A class that encapsulates event callbacks and provides a mechanism for executing them
    when the event occurs. This class manages both asynchronous and synchronous execution
    and handles event completion in both success and error scenarios.

    **Notes:**

    -   The `__call__` method of the `EventHandler` class is an asynchronous method
        that returns a `Coroutine`. It should never be treated as a synchronous function.

    -   This class is not intended to be subclassed or manually created. It is used
        internally to encapsulate the callbacks associated with an event and manage
        their execution.

    -   The event handler can be invoked by calling the instance as a function and
        passing the required arguments.

    ---
    Read more in the
    [Pyventus docs for Event Handler](https://mdapena.github.io/pyventus/tutorials/event-linker/).
    """

    @staticmethod
    def get_callback_name(
        callback: EventCallbackType | SuccessCallbackType | FailureCallbackType | None,  # type: ignore[type-arg]
    ) -> str:
        """
        Retrieves the name of the provided callback.
        :param callback: The callback object.
        :return: The name of the callback as a string.
        """
        if callback is not None and hasattr(callback, "__name__"):
            return callback.__name__
        elif callback is not None and hasattr(callback, "__class__"):
            return type(callback).__name__
        else:
            return "None"

    @staticmethod
    def validate_callback(
        callback: EventCallbackType | SuccessCallbackType | FailureCallbackType,  # type: ignore[type-arg]
    ) -> None:
        """
        Validates whether the provided callback is a valid callable object.
        :param callback: The callback to be validated.
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
        Checks whether the provided callback is an asynchronous function or method.
        :param callback: The callback to be checked.
        :return: `True` if the callback is an asynchronous function or method, `False` otherwise.
        :raises PyventusException: If the callback is not a callable or a string.
        """
        if ismethod(callback) or isfunction(callback) or isbuiltin(callback):
            return iscoroutinefunction(callback)
        elif not isclass(callback) and hasattr(callback, "__call__"):  # A callable class instance
            return iscoroutinefunction(callback.__call__)
        else:
            raise PyventusException("Expected a callable or a string, but got: {0}".format(callback))

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
        Determines if the event handler is a one-time subscription.
        :return: A boolean value indicating if the event handler is
            a one-time subscription.
        """
        return self._once

    @property
    def force_async(self) -> bool:
        """
        Determines whether all callbacks are forced to run asynchronously.
        :return: A boolean value indicating if all callbacks are forced to run
            asynchronously. If `True`, synchronous callbacks will be converted to
            run asynchronously in a thread pool, using the `asyncio.to_thread`
            function. If `False`, callbacks will run synchronously or
            asynchronously as defined.
        """
        return self._force_async

    @property
    def timestamp(self) -> datetime:
        """
        Retrieves the timestamp when the event handler was created.
        :return: The timestamp when the event handler was created.
        """
        return self._timestamp

    def __init__(
        self,
        once: bool,
        force_async: bool,
        event_callback: EventCallbackType,  # type: ignore[type-arg]
        success_callback: SuccessCallbackType | None = None,
        failure_callback: FailureCallbackType | None = None,
    ) -> None:
        """
        Initialize an instance of `EventHandler`.
        :param once: Specifies if the event handler is a one-time subscription.
        :param force_async: Determines whether to force all callbacks to run asynchronously.
            If `True`, synchronous callbacks will be converted to run asynchronously in a
            thread pool, using the `asyncio.to_thread` function. If `False`, callbacks
            will run synchronously or asynchronously as defined.
        :param event_callback: The callback to be executed when the event occurs.
        :param success_callback: The callback to be executed when the event execution
            completes successfully. Default is `None`.
        :param failure_callback: The callback to be executed when the event execution
            fails. Default is `None`.
        :raises PyventusException: If the provided callbacks are invalid.
        """
        # Validate callbacks
        EventHandler.validate_callback(callback=event_callback)

        if success_callback is not None:
            EventHandler.validate_callback(callback=success_callback)

        if failure_callback is not None:
            EventHandler.validate_callback(callback=failure_callback)

        # Validate flags
        if not isinstance(once, bool):
            raise PyventusException("The 'once' argument must be a boolean value.")
        if not isinstance(force_async, bool):
            raise PyventusException("The 'force_async' argument must be a boolean value.")

        # Set the event handler flags
        self._once: bool = once
        self._force_async: bool = force_async

        # Set the event handler callbacks
        self._event_callback: EventCallbackType = event_callback  # type: ignore[type-arg]
        self._success_callback: SuccessCallbackType | None = success_callback
        self._failure_callback: FailureCallbackType | None = failure_callback

        # Set the event handler callbacks flags
        self._is_event_callback_async: bool = EventHandler.is_async(event_callback)
        self._is_success_callback_async: bool | None = (
            EventHandler.is_async(success_callback) if success_callback else None
        )
        self._is_failure_callback_async: bool | None = (
            EventHandler.is_async(failure_callback) if failure_callback else None
        )

        # Set the event handler timestamp
        self._timestamp: datetime = datetime.now()

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> None:
        """
        Executes the event flow by invoking the associated callbacks.
        :param args: Positional arguments to be passed to the event callback.
        :param kwargs: Keyword arguments to be passed to the event callback.
        :return: Coroutine
        """
        # Event callback results
        results: Any | None = None

        try:
            # Invoke the event callback.
            if self._is_event_callback_async:
                results = await self._event_callback(*args, **kwargs)
            elif self._force_async:
                results = await to_thread(self._event_callback, *args, **kwargs)
            else:
                results = self._event_callback(*args, **kwargs)
        except Exception as exception:
            # Log the exception with error level
            StdOutLogger.error(name=f"{self.__class__.__name__}", action="Exception:", msg=f"{exception}")

            # Invoke the failure callback and pass the exception.
            if self._failure_callback:
                if self._is_failure_callback_async:
                    await self._failure_callback(exception)
                elif self._force_async:
                    await to_thread(self._failure_callback, exception)
                else:
                    self._failure_callback(exception)
        else:
            # Invoke the success callback and pass the results, if any.
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
        """
        Returns a formatted string representation of the event handler.
        :return: A string representation of the event handler.
        """
        return "".join(
            [
                f"Event Callback: `{EventHandler.get_callback_name(callback=self._event_callback)}",
                "` (Async) | " if self._is_event_callback_async else "` (Sync) | ",
                (
                    "Success Callback: `".join(
                        [
                            EventHandler.get_callback_name(callback=self._success_callback),
                            "` (Async) | " if self._is_success_callback_async else "` (Sync) | ",
                        ]
                    )
                    if self._success_callback
                    else ""
                ),
                (
                    "Failure Callback: `".join(
                        [
                            EventHandler.get_callback_name(callback=self._failure_callback),
                            "` (Async) | " if self._is_failure_callback_async else "` (Sync) | ",
                        ]
                    )
                    if self._failure_callback
                    else ""
                ),
                f"Once: {self.once} | ",
                f"Force Async: {self.force_async} | ",
                f"Timestamp: {self.timestamp.strftime('%Y-%m-%d %I:%M:%S %p')}",
            ]
        )
