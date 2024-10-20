from collections.abc import Awaitable, Callable
from typing import Any, TypeAlias, final

from typing_extensions import Self, override

from ...core.exceptions import PyventusException
from ...core.subscriptions import Subscription
from ...core.utils import CallableWrapper, attributes_repr, formatted_repr
from ...events.handlers import EventHandler

EventCallbackType: TypeAlias = Callable[..., Any]
"""Type alias for the event callback invoked when the event occurs."""

SuccessCallbackType: TypeAlias = Callable[..., Awaitable[None] | None]
"""Type alias for the callback invoked when the event response completes successfully."""

FailureCallbackType: TypeAlias = Callable[[Exception], Awaitable[None] | None]
"""Type alias for the callback invoked when the event response fails."""


@final
class EventSubscriber(EventHandler, Subscription):
    """
    A class that represents an `EventHandler` subscribed to an `EventLinker`.

    **Notes:**

    -   This class combines the `EventHandler` interface with the `Subscription`
        base class, providing a convenient way to handle events and manage the
        subscription lifecycle.

    -   This class is not intended to be subclassed or instantiated directly.
    """

    # Attributes for the EventSubscriber
    __slots__ = ("__event_callback", "__success_callback", "__failure_callback", "__once")

    def __init__(
        self,
        teardown_callback: Callable[[Self], bool],
        event_callback: EventCallbackType,
        success_callback: SuccessCallbackType | None,
        failure_callback: FailureCallbackType | None,
        force_async: bool,
        once: bool,
    ) -> None:
        """
        Initialize an instance of `EventSubscriber`.

        :param teardown_callback: A callback function invoked during the unsubscription process to perform
            cleanup or teardown operations associated with the subscription. It should return `True` if the
            cleanup was successful, or `False` if the teardown has already been executed and the subscription
            is no longer active.
        :param event_callback: The callback to be executed when the event occurs.
        :param success_callback: The callback to be executed when the event response completes successfully.
        :param failure_callback: The callback to be executed when the event response fails.
        :param force_async: Determines whether to force all callbacks to run asynchronously.
            If `True`, synchronous callbacks will be converted to run asynchronously in a
            thread pool, using the `asyncio.to_thread` function. If `False`, callbacks
            will run synchronously or asynchronously as defined.
        :param once: Specifies if the event subscriber is a one-time subscription.
        """
        # Initialize the base Subscription class with the teardown callback
        super().__init__(teardown_callback=teardown_callback)

        # Ensure the 'once' parameter is a boolean
        if not isinstance(once, bool):
            raise PyventusException("The 'once' argument must be a boolean value.")

        # Wrap and set the event callback
        self.__event_callback = CallableWrapper[..., Any](event_callback, force_async=force_async)

        # Ensure that the event callback is not a generator.
        if self.__event_callback.is_generator:
            raise PyventusException("The 'event_callback' cannot be a generator.")

        # Wrap and set the success callback, if provided.
        self.__success_callback = (
            CallableWrapper[..., None](
                success_callback,
                force_async=force_async,
            )
            if success_callback
            else None
        )

        # Ensure that the success callback is not a generator.
        if self.__success_callback and self.__success_callback.is_generator:
            raise PyventusException("The 'success_callback' cannot be a generator.")

        # Wrap and set the failure callback, if provided.
        self.__failure_callback = (
            CallableWrapper[[Exception], None](
                failure_callback,
                force_async=force_async,
            )
            if failure_callback
            else None
        )

        # Ensure that the failure callback is not a generator.
        if self.__failure_callback and self.__failure_callback.is_generator:
            raise PyventusException("The 'failure_callback' cannot be a generator.")

        # Store the one-time subscription flag.
        self.__once: bool = once

    @override
    def __repr__(self) -> str:
        return formatted_repr(
            instance=self,
            info=(
                attributes_repr(
                    event_callback=self.__event_callback,
                    success_callback=self.__success_callback,
                    failure_callback=self.__failure_callback,
                    once=self.__once,
                )
                + f", {super().__repr__()}"
            ),
        )

    @property
    def once(self) -> bool:
        """
        Determine if the event subscriber is a one-time subscription.

        :return: A boolean value indicating if the event subscriber
            is a one-time subscription.
        """
        return self.__once

    @override
    async def _handle_event(self, *args: Any, **kwargs: Any) -> Any:
        # Execute the event callback with the provided arguments and return the result
        return await self.__event_callback.execute(*args, **kwargs)

    @override
    async def _handle_success(self, results: Any) -> None:
        if self.__success_callback is None:
            # If no success callback is set, exit early
            return
        elif results is None:
            # If results are None, invoke the success callback without parameters
            await self.__success_callback.execute()
        else:
            # Invoke the success callback with the given results
            await self.__success_callback.execute(results)

    @override
    async def _handle_failure(self, exception: Exception) -> None:
        if self.__failure_callback is None:
            # If no failure callback is set, exit early
            return
        else:
            # Invoke the failure callback with the provided exception
            await self.__failure_callback.execute(exception)

    @override
    def __getstate__(self) -> dict[str, Any]:
        # Retrieve the state of the base Subscription class
        state: dict[str, Any] = super().__getstate__()

        # Add the state of the EventSubscriber attributes
        state["__event_callback"] = self.__event_callback
        state["__success_callback"] = self.__success_callback
        state["__failure_callback"] = self.__failure_callback
        state["__once"] = self.__once

        # Return the complete state for serialization
        return state

    @override
    def __setstate__(self, state: dict[str, Any]) -> None:
        # Restore the state of the base Subscription class
        super().__setstate__(state)

        # Restore the state of the EventSubscriber attributes
        self.__event_callback = state["__event_callback"]
        self.__success_callback = state["__success_callback"]
        self.__failure_callback = state["__failure_callback"]
        self.__once = state["__once"]
