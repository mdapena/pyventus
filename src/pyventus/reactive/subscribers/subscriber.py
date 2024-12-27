from collections.abc import Awaitable, Callable
from typing import Any, Generic, TypeAlias, TypeVar, final

from typing_extensions import Self, override

from ...core.exceptions import PyventusException
from ...core.subscriptions import Subscription
from ...core.utils import CallableWrapper, attributes_repr, formatted_repr
from ..observers import Observer

_InT = TypeVar("_InT", contravariant=True)
"""A generic type representing the input value for the `next` method."""

NextCallbackType: TypeAlias = Callable[[_InT], Awaitable[None] | None]
"""Type alias for the callback to be executed when the observable emits a new value."""

ErrorCallbackType: TypeAlias = Callable[[Exception], Awaitable[None] | None]
"""Type alias for the callback to be executed when the observable encounters an error."""

CompleteCallbackType: TypeAlias = Callable[[], Awaitable[None] | None]
"""Type alias for the callback that will be executed when the observable has completed emitting values."""


@final
class Subscriber(Generic[_InT], Observer[_InT], Subscription):
    """
    A class that represents an `Observer` subscribed to an `Observable`.

    **Notes:**

    -   This class combines the `Observer` interface with the `Subscription`
        base class, offering a convenient way to both respond to state changes
        emitted by an observable and manage the subscription lifecycle.

    -   This class is not intended to be subclassed or instantiated directly.
    """

    # Attributes for the Subscriber
    __slots__ = ("__next_callback", "__error_callback", "__complete_callback")

    def __init__(
        self,
        teardown_callback: Callable[[Self], bool],
        next_callback: NextCallbackType[_InT] | None,
        error_callback: ErrorCallbackType | None,
        complete_callback: CompleteCallbackType | None,
        force_async: bool,
    ) -> None:
        """
        Initialize an instance of `Subscriber`.

        :param teardown_callback: A callback function invoked during the unsubscription process to perform
            cleanup or teardown operations associated with the subscription. It should return `True` if the
            cleanup was successful, or `False` if the teardown has already been executed and the subscription
            is no longer active.
        :param next_callback: The callback to be executed when the observable emits a new value.
        :param error_callback: The callback to be executed when the observable encounters an error.
        :param complete_callback: The callback that will be executed when the observable has completed emitting values.
        :param force_async: Determines whether to force all callbacks to run asynchronously.
            If `True`, synchronous callbacks will be converted to run asynchronously in a
            thread pool, using the `asyncio.to_thread` function. If `False`, callbacks
            will run synchronously or asynchronously as defined.
        """
        # Initialize the base Subscription class with the teardown callback
        super().__init__(teardown_callback=teardown_callback)

        # Ensure that at least one of the callbacks (next, error, or complete) is defined.
        if next_callback is None and error_callback is None and complete_callback is None:
            raise PyventusException("At least one of the callbacks (next, error, or complete) must be defined.")

        # Wrap and set the next callback, if provided
        self.__next_callback = (
            CallableWrapper[[_InT], None](
                next_callback,
                force_async=force_async,
            )
            if next_callback
            else None
        )

        # Ensure that the next callback is not a generator.
        if self.__next_callback and self.__next_callback.is_generator:
            raise PyventusException("The 'next_callback' cannot be a generator.")

        # Wrap and set the error callback, if provided
        self.__error_callback = (
            CallableWrapper[[Exception], None](
                error_callback,
                force_async=force_async,
            )
            if error_callback
            else None
        )

        # Ensure that the error callback is not a generator.
        if self.__error_callback and self.__error_callback.is_generator:
            raise PyventusException("The 'error_callback' cannot be a generator.")

        # Wrap and set the complete callback, if provided
        self.__complete_callback = (
            CallableWrapper[[], None](
                complete_callback,
                force_async=force_async,
            )
            if complete_callback
            else None
        )

        # Ensure that the complete callback is not a generator.
        if self.__complete_callback and self.__complete_callback.is_generator:
            raise PyventusException("The 'complete_callback' cannot be a generator.")

    @override
    def __repr__(self) -> str:
        return formatted_repr(
            instance=self,
            info=(
                attributes_repr(
                    next_callback=self.__next_callback,
                    error_callback=self.__error_callback,
                    complete_callback=self.__complete_callback,
                )
                + f", {super().__repr__()}"
            ),
        )

    @property
    def has_next_callback(self) -> bool:
        """
        Determine whether the subscriber has a next callback assigned.

        :return: `True` if the subscriber has a next callback assigned; otherwise, `False`.
        """
        return self.__next_callback is not None

    @property
    def has_error_callback(self) -> bool:
        """
        Determine whether the subscriber has an error callback assigned.

        :return: `True` if the subscriber has an error callback assigned; otherwise, `False`.
        """
        return self.__error_callback is not None

    @property
    def has_complete_callback(self) -> bool:
        """
        Determine whether the subscriber has a complete callback assigned.

        :return: `True` if the subscriber has a complete callback assigned; otherwise, `False`.
        """
        return self.__complete_callback is not None

    @override
    async def next(self, value: _InT) -> None:
        if self.__next_callback is None:
            # If no next callback is set, exit early
            return
        else:
            # Invoke the next callback with the provided value
            await self.__next_callback.execute(value)

    @override
    async def error(self, exception: Exception) -> None:
        if self.__error_callback is None:
            # If no error callback is set, exit early
            return
        else:
            # Invoke the error callback with the provided exception
            await self.__error_callback.execute(exception)

    @override
    async def complete(self) -> None:
        if self.__complete_callback is None:
            # If no complete callback is set, exit early
            return
        else:
            # Invoke the complete callback
            await self.__complete_callback.execute()

    @override
    def __getstate__(self) -> dict[str, Any]:
        # Retrieve the state of the base Subscription class
        state: dict[str, Any] = super().__getstate__()

        # Add the state of the Subscriber attributes
        state["__next_callback"] = self.__next_callback
        state["__error_callback"] = self.__error_callback
        state["__complete_callback"] = self.__complete_callback

        # Return the complete state for serialization
        return state

    @override
    def __setstate__(self, state: dict[str, Any]) -> None:
        # Restore the state of the base Subscription class
        super().__setstate__(state)

        # Restore the state of the Subscriber attributes
        self.__next_callback = state["__next_callback"]
        self.__error_callback = state["__error_callback"]
        self.__complete_callback = state["__complete_callback"]
