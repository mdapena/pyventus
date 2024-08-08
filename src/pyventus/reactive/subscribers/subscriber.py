import sys
from typing import Awaitable, Callable, Generic, TypeAlias, TypeVar, final

from ..observers import Observer
from ...core.subscriptions import Subscription
from ...core.utils import CallableWrapper

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


_in_T = TypeVar("_in_T", contravariant=True)
"""A generic type representing the input value for the `next` method."""

NextCallbackType: TypeAlias = Callable[[_in_T], Awaitable[None] | None]
"""Type alias for the callback to be executed when the observable emits a new value."""

ErrorCallbackType: TypeAlias = Callable[[Exception], Awaitable[None] | None]
"""Type alias for the callback to be executed when the observable encounters an error."""

CompleteCallbackType: TypeAlias = Callable[[], Awaitable[None] | None]
"""Type alias for the callback that will be executed when the observable has completed emitting values."""


@final
class Subscriber(Generic[_in_T], Observer[_in_T], Subscription):
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
        next_callback: NextCallbackType[_in_T] | None,
        error_callback: ErrorCallbackType | None,
        complete_callback: CompleteCallbackType | None,
        force_async: bool,
    ) -> None:
        """
        Initializes an instance of `Subscriber`.
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

        # Wrap and set the next callback, if provided
        self.__next_callback = (
            CallableWrapper[[_in_T], None](
                next_callback,
                force_async=force_async,
            )
            if next_callback
            else None
        )

        # Wrap and set the error callback, if provided
        self.__error_callback = (
            CallableWrapper[[Exception], None](
                error_callback,
                force_async=force_async,
            )
            if error_callback
            else None
        )

        # Wrap and set the complete callback, if provided
        self.__complete_callback = (
            CallableWrapper[[], None](
                complete_callback,
                force_async=force_async,
            )
            if complete_callback
            else None
        )

    async def next(self, value: _in_T) -> None:
        if self.__next_callback is None:
            # If no next callback is set, exit early
            return
        else:
            # Invoke the next callback with the provided value
            await self.__next_callback(value)

    async def error(self, exception: Exception) -> None:
        if self.__error_callback is None:
            # If no error callback is set, exit early
            return
        else:
            # Invoke the error callback with the provided exception
            await self.__error_callback(exception)

    async def complete(self) -> None:
        if self.__complete_callback is None:
            # If no complete callback is set, exit early
            return
        else:
            # Invoke the complete callback
            await self.__complete_callback()

    def __str__(self) -> str:
        return (
            f"Subscriber("
            f"next_callback={self.__next_callback}, "
            f"error_callback={self.__error_callback}, "
            f"complete_callback={self.__complete_callback}, "
            f"timestamp='{self.timestamp.strftime('%Y-%m-%d %I:%M:%S %p')}')"
        )
