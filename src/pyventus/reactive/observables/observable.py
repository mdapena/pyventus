from abc import ABC
from asyncio import gather
from sys import gettrace
from threading import Lock
from typing import Generic, TypeVar, final

from typing_extensions import Self, overload, override

from ...core.exceptions import PyventusException
from ...core.loggers import Logger
from ...core.subscriptions import SubscriptionContext
from ...core.utils import attributes_repr, summarized_repr
from ..subscribers import CompleteCallbackType, ErrorCallbackType, NextCallbackType, Subscriber

_OutT = TypeVar("_OutT", covariant=True)
"""A generic type representing the value that will be streamed through the observable."""

_SubCtxT = TypeVar("_SubCtxT", contravariant=True)
"""A generic type representing the value type for the Observable and Subscriber within the subscription context."""

_SubCtxO = TypeVar("_SubCtxO", bound="Observable")  # type: ignore[type-arg]
"""A generic type representing the observable type used in the subscription context."""


class Observable(ABC, Generic[_OutT]):
    """
    A base class that defines a lazy push-style notification mechanism for streaming data to subscribers.

    **Notes:**

    -   The `Observable` class serves as a foundation for implementing various observable types with different
        dispatch logic and strategies, encapsulating the essential protocols and workflows for streaming data
        to subscribers in a reactive manner.

    -   This class is parameterized by the type of value that will be streamed through the observable. This
        type parameter is covariant, allowing it to be either the specified type or any subtype.

    -   The `subscribe()` method can be utilized as a regular function, a decorator, or a context manager.
        When used as a regular function, it automatically creates and subscribes an observer with the specified
        callbacks. As a decorator, it creates and subscribes an observer, using the decorated callback as the
        next callback. Finally, when employed as a context manager with the `with` statement, it enables a
        step-by-step definition of the observer's callbacks prior to its subscription, which occurs
        immediately after exiting the context.

    -   This class has been designed with *thread safety* in mind. All of its methods synchronize access to
        mutable attributes to prevent race conditions when managing observables in a multi-threaded environment.
    """

    @final
    class ObservableSubCtx(Generic[_SubCtxO, _SubCtxT], SubscriptionContext[_SubCtxO, Subscriber[_SubCtxT]]):
        """
        A context manager for Observable subscriptions.

        **Notes:**

        -   This class establishes a context block for a step-by-step definition of the observer's
            callbacks prior to the actual subscription, which occurs immediately upon exiting the
            context block.

        -   This class can be used as either a decorator or a context manager. When used as a
            decorator, it creates and subscribes an observer, using the decorated callback as
            the next callback. When employed as a context manager with the `with` statement,
            it enables a step-by-step definition of the observer's callbacks prior to its
            subscription, which occurs immediately after exiting the context.

        -   This subscription context can be `stateful`, retaining references to the `observable`
            and `subscriber`, or `stateless`, which clears the context upon exiting the
            subscription block.

        -   This class is not intended to be subclassed or manually instantiated.
        """

        # Attributes for the ObservableSubCtx
        __slots__ = ("__next_callback", "__error_callback", "__complete_callback", "__force_async")

        def __init__(self, observable: _SubCtxO, force_async: bool, is_stateful: bool) -> None:
            """
            Initialize an instance of `ObservableSubCtx`.

            :param observable: The observable to which the observer will be subscribed.
            :param force_async: Determines whether to force all callbacks to run asynchronously.
            :param is_stateful: A flag indicating whether the context preserves its state (`stateful`) or
                not (`stateless`) after exiting the subscription context. If `True`, the context retains its
                state, allowing access to stored objects, including the `observable` and the `subscriber`
                object. If `False`, the context is stateless, and the stored state is cleared upon
                exiting the subscription context to prevent memory leaks.
            """
            # Initialize the base SubscriptionContext class
            super().__init__(source=observable, is_stateful=is_stateful)

            # Initialize variables
            self.__next_callback: NextCallbackType[_SubCtxT] | None = None
            self.__error_callback: ErrorCallbackType | None = None
            self.__complete_callback: CompleteCallbackType | None = None
            self.__force_async: bool = force_async

        @override
        def _exit(self) -> Subscriber[_SubCtxT]:
            # Ensure that the source is not None.
            if self._source is None:  # pragma: no cover
                raise PyventusException("The subscription context is closed.")

            # Ensure that at least one callback is defined before performing the subscription.
            if self.__next_callback is None and self.__error_callback is None and self.__complete_callback is None:
                raise PyventusException("At least one callback must be defined before performing the subscription.")

            # Subscribe the defined callbacks to the specified
            # observable and store the returned subscriber.
            subscriber: Subscriber[_SubCtxT] = self._source.subscribe(
                next_callback=self.__next_callback,
                error_callback=self.__error_callback,
                complete_callback=self.__complete_callback,
                force_async=self.__force_async,
            )

            # Remove context-specific attributes.
            del self.__next_callback, self.__error_callback, self.__complete_callback, self.__force_async

            # Return the subscriber.
            return subscriber

        def on_next(self, callback: NextCallbackType[_SubCtxT]) -> NextCallbackType[_SubCtxT]:
            """
            Set the observer's next callback.

            :param callback: The callback to be executed when the observable emits a new value.
            :return: The decorated callback.
            """
            self.__next_callback = callback
            return callback

        def on_error(self, callback: ErrorCallbackType) -> ErrorCallbackType:
            """
            Set the observer's error callback.

            :param callback: The callback to be executed when the observable encounters an error.
            :return: The decorated callback.
            """
            self.__error_callback = callback
            return callback

        def on_complete(self, callback: CompleteCallbackType) -> CompleteCallbackType:
            """
            Set the observer's complete callback.

            :param callback: The callback that will be executed when the observable has completed emitting values.
            :return: The decorated callback.
            """
            self.__complete_callback = callback
            return callback

        def __call__(
            self, callback: NextCallbackType[_SubCtxT]
        ) -> (
            tuple[NextCallbackType[_SubCtxT], "Observable.ObservableSubCtx[_SubCtxO, _SubCtxT]"]
            | NextCallbackType[_SubCtxT]
        ):
            """
            Subscribe the decorated callback as the observer's `next` function for the specified observable.

            :param callback: The callback to be executed when the observable emits a new value.
            :return: A tuple containing the decorated callback and its subscription context
                if the context is `stateful`; otherwise, returns the decorated callback alone.
            """
            # Store the provided callback in the subscription context.
            self.__next_callback = callback

            # Set error and complete callbacks to None.
            self.__error_callback = None
            self.__complete_callback = None

            # Determine if the subscription context is stateful.
            is_stateful: bool = self._is_stateful

            # Call the exit method to finalize the
            # subscription process and clean up any necessary context.
            self.__exit__(None, None, None)

            # Return a tuple containing the decorated callback
            # and the current subscription context if the context
            # is stateful; otherwise, return just the callback.
            return (callback, self) if is_stateful else callback

    @final
    class Completed(Exception):
        """Exception raised to indicate that an observable sequence has completed."""

    @staticmethod
    def get_valid_subscriber(subscriber: Subscriber[_OutT]) -> Subscriber[_OutT]:
        """
        Validate and return the specified subscriber.

        :param subscriber: The subscriber to validate.
        :return: The validated subscriber.
        :raises PyventusException: If the subscriber is not an instance of `Subscriber`.
        """
        # Validate that the subscriber is an instance of Subscriber.
        if not isinstance(subscriber, Subscriber):
            raise PyventusException("The 'subscriber' argument must be an instance of Subscriber.")
        return subscriber

    # Attributes for the Observable
    __slots__ = ("__subscribers", "__thread_lock", "__logger")

    def __init__(self, debug: bool | None = None) -> None:
        """
        Initialize an instance of `Observable`.

        :param debug: Specifies the debug mode for the logger. If `None`,
            the mode is determined based on the execution environment.
        """
        # Initialize the set of subscribers.
        self.__subscribers: set[Subscriber[_OutT]] = set()

        # Create a lock object for thread synchronization.
        self.__thread_lock: Lock = Lock()

        # Validate the debug argument.
        if debug is not None and not isinstance(debug, bool):
            raise PyventusException("The 'debug' argument must be a boolean value.")

        # Set up the logger with the appropriate debug mode.
        self.__logger: Logger = Logger(source=self, debug=debug if debug is not None else bool(gettrace() is not None))

    def __repr__(self) -> str:
        """
        Retrieve a string representation of the instance.

        :return: A string representation of the instance.
        """
        return attributes_repr(
            subscribers=self.__subscribers,
            thread_lock=self.__thread_lock,
            debug=self.__logger.debug_enabled,
        )

    @property
    def _logger(self) -> Logger:
        """
        Retrieve the logger instance.

        :return: The logger instance used for logging messages.
        """
        return self.__logger

    @property
    def _thread_lock(self) -> Lock:
        """
        Retrieve the thread lock instance.

        :return: The thread lock instance used to ensure thread-safe operations.
        """
        return self.__thread_lock

    def _log_subscriber_exception(self, subscriber: Subscriber[_OutT], exception: Exception) -> None:
        """
        Log an unhandled exception that occurred during the execution of a subscriber's callback.

        :param subscriber: The subscriber instance that encountered the exception.
        :param exception: The exception instance to be logged.
        :return: None.
        """
        self.__logger.error(action="Exception:", msg=f"{exception!r} at {summarized_repr(subscriber)}.")

    @final  # Prevent overriding in subclasses to maintain the integrity of the _OutT type.
    async def _emit_next(self, value: _OutT) -> None:  # type: ignore[misc]
        """
        Emit the next value to all subscribers.

        This method notifies all subscribers of the next value in the stream.

        :param value: The value to be emitted to all subscribers.
        :return: None.
        """
        # Acquire lock to ensure thread safety.
        with self.__thread_lock:
            # Get all subscribers and filter those with a next callback to optimize execution.
            subscribers: list[Subscriber[_OutT]] = [
                subscriber for subscriber in self.__subscribers if subscriber.has_next_callback
            ]

        # Exit if there are no subscribers.
        if not subscribers:
            # Log a debug message if debug mode is enabled.
            if self.__logger.debug_enabled:
                self.__logger.debug(
                    action="Emitting Next Value:",
                    msg=f"No subscribers to notify of the next value: {value!r}.",
                )
            return

        # Log the emission of the next value if debug mode is enabled.
        if self.__logger.debug_enabled:
            self.__logger.debug(
                action="Emitting Next Value:",
                msg=f"Notifying {len(subscribers)} subscribers of the next value: {value!r}.",
            )

        # If there is only one subscriber, handle it directly.
        if len(subscribers) == 1:
            try:
                # Notify the subscriber and await its response.
                subscriber: Subscriber[_OutT] = subscribers.pop()
                await subscriber.next(value)
            except Exception as e:
                # Log any exceptions that occur during notification.
                self._log_subscriber_exception(subscriber, e)
        else:
            # Notify all subscribers concurrently.
            results = await gather(*[subscriber.next(value) for subscriber in subscribers], return_exceptions=True)

            # Log any exceptions that occur during notification.
            for subscriber, result in zip(subscribers, results, strict=True):
                if isinstance(result, Exception):
                    self._log_subscriber_exception(subscriber, result)

    @final
    async def _emit_error(self, exception: Exception) -> None:
        """
        Emit the error that occurred to all subscribers.

        This method notifies all subscribers of the error that occurred.

        :param exception: The exception to be emitted to all subscribers.
        :return: None.
        """
        # Acquire lock to ensure thread safety.
        with self.__thread_lock:
            # Get all subscribers and filter those with an error callback to optimize execution.
            subscribers: list[Subscriber[_OutT]] = [
                subscriber for subscriber in self.__subscribers if subscriber.has_error_callback
            ]

        # Exit if there are no subscribers.
        if not subscribers:
            # Log an error message.
            self.__logger.error(
                action="Emitting Error:",
                msg=f"No subscribers to notify of the error: {exception!r}.",
            )
            return

        # Log the error emission if debug mode is enabled.
        if self.__logger.debug_enabled:
            self.__logger.debug(
                action="Emitting Error:",
                msg=f"Notifying {len(subscribers)} subscribers of the error: {exception!r}.",
            )

        # If there is only one subscriber, handle it directly.
        if len(subscribers) == 1:
            try:
                # Notify the subscriber and await its response.
                subscriber: Subscriber[_OutT] = subscribers.pop()
                await subscriber.error(exception)
            except Exception as e:
                # Log any exceptions that occur during notification.
                self._log_subscriber_exception(subscriber, e)
        else:
            # Notify all subscribers concurrently.
            results = await gather(*[subscriber.error(exception) for subscriber in subscribers], return_exceptions=True)

            # Log any exceptions that occur during notification.
            for subscriber, result in zip(subscribers, results, strict=True):
                if isinstance(result, Exception):
                    self._log_subscriber_exception(subscriber, result)

    @final
    async def _emit_complete(self) -> None:
        """
        Emit the completion signal to all subscribers.

        This method notifies all subscribers that the stream has completed.

        :return: None.
        """
        # Acquire lock to ensure thread safety.
        with self.__thread_lock:
            # Get all subscribers and filter those with a complete callback to optimize execution.
            subscribers: list[Subscriber[_OutT]] = [
                subscriber for subscriber in self.__subscribers if subscriber.has_complete_callback
            ]

            # Unsubscribe all observers since the stream has completed.
            self.__subscribers.clear()

        # Exit if there are no subscribers.
        if not subscribers:
            # Log a debug message if debug mode is enabled.
            if self.__logger.debug_enabled:
                self.__logger.debug(
                    action="Emitting Completion:",
                    msg="No subscribers to notify of completion.",
                )
            return

        # Log the emission if debug is enabled.
        if self.__logger.debug_enabled:
            self.__logger.debug(
                action="Emitting Completion:",
                msg=f"Notifying {len(subscribers)} subscribers of completion.",
            )

        # If there is only one subscriber, handle it directly.
        if len(subscribers) == 1:
            try:
                # Notify the subscriber and await its response.
                subscriber: Subscriber[_OutT] = subscribers.pop()
                await subscriber.complete()
            except Exception as e:
                # Log any exceptions that occur during notification.
                self._log_subscriber_exception(subscriber, e)
        else:
            # Notify all subscribers concurrently.
            results = await gather(*[subscriber.complete() for subscriber in subscribers], return_exceptions=True)

            # Log any exceptions that occur during notification.
            for subscriber, result in zip(subscribers, results, strict=True):
                if isinstance(result, Exception):
                    self._log_subscriber_exception(subscriber, result)

    def get_subscribers(self) -> set[Subscriber[_OutT]]:
        """
        Retrieve all registered subscribers.

        :return: A set of all registered subscribers.
        """
        with self.__thread_lock:
            return self.__subscribers.copy()

    def get_subscriber_count(self) -> int:
        """
        Retrieve the number of registered subscribers.

        :return: The total count of subscribers in the observable.
        """
        with self.__thread_lock:
            return len(self.__subscribers)

    def contains_subscriber(self, subscriber: Subscriber[_OutT]) -> bool:
        """
        Determine if the specified subscriber is present in the observable.

        :param subscriber: The subscriber to be checked.
        :return: `True` if the subscriber is found; `False` otherwise.
        """
        valid_subscriber: Subscriber[_OutT] = self.get_valid_subscriber(subscriber)
        with self.__thread_lock:
            return valid_subscriber in self.__subscribers

    @overload
    def subscribe(
        self, *, force_async: bool = False, stateful_subctx: bool = False
    ) -> "Observable.ObservableSubCtx[Self, _OutT]": ...

    @overload
    def subscribe(
        self,
        next_callback: NextCallbackType[_OutT] | None = None,
        error_callback: ErrorCallbackType | None = None,
        complete_callback: CompleteCallbackType | None = None,
        *,
        force_async: bool = False,
    ) -> Subscriber[_OutT]: ...

    def subscribe(
        self,
        next_callback: NextCallbackType[_OutT] | None = None,
        error_callback: ErrorCallbackType | None = None,
        complete_callback: CompleteCallbackType | None = None,
        *,
        force_async: bool = False,
        stateful_subctx: bool = False,
    ) -> Subscriber[_OutT] | "Observable.ObservableSubCtx[Self, _OutT]":
        """
        Subscribe the specified callbacks to the current `Observable`.

        This method can be utilized in three ways:

        -   **As a regular function:** Automatically creates and subscribes an observer
            with the specified callbacks.

        -   **As a decorator:** Creates and subscribes an observer, using the decorated
            callback as the next callback.

        -   **As a context manager:** Enables a step-by-step definition of the observer's
            callbacks prior to subscription, which occurs immediately after exiting the context.

        :param next_callback: The callback to be executed when the observable emits a new value.
        :param error_callback: The callback to be executed when the observable encounters an error.
        :param complete_callback: The callback that will be executed when the observable has completed emitting values.
        :param force_async: Determines whether to force all callbacks to run asynchronously.
        :param stateful_subctx: A flag indicating whether the subscription context preserves its state (`stateful`)
            or not (`stateless`) after exiting the subscription block. If `True`, the context retains its state,
            allowing access to stored objects, including the `observable` and the `subscriber` object. If `False`,
            the context is stateless, and the stored state is cleared upon exiting the subscription block to
            prevent memory leaks. The term 'subctx' refers to 'Subscription Context'.
        :return: A `Subscriber` if callbacks are provided; otherwise, an `ObservableSubCtx`.
        """
        if next_callback is None and error_callback is None and complete_callback is None:
            # If no callbacks are provided, create a subscription context for progressive definition.
            return Observable.ObservableSubCtx[Self, _OutT](
                observable=self,
                force_async=force_async,
                is_stateful=stateful_subctx,
            )
        else:
            # Create a subscriber with the provided callbacks.
            subscriber = Subscriber[_OutT](
                teardown_callback=self.remove_subscriber,
                next_callback=next_callback,
                error_callback=error_callback,
                complete_callback=complete_callback,
                force_async=force_async,
            )

            # Acquire lock to ensure thread safety.
            with self.__thread_lock:
                # Add the subscriber to the observable.
                self.__subscribers.add(subscriber)

            # Log the subscription if debug is enabled
            if self.__logger.debug_enabled:
                self.__logger.debug(action="Subscribed:", msg=f"{subscriber}")

            # Return the subscriber.
            return subscriber

    def remove_subscriber(self, subscriber: Subscriber[_OutT]) -> bool:
        """
        Remove the specified subscriber from the observable.

        :param subscriber: The subscriber to be removed from the observable.
        :return: `True` if the subscriber was successfully removed; `False` if
            the subscriber was not found in the observable.
        """
        # Get the valid subscriber instance.
        valid_subscriber: Subscriber[_OutT] = self.get_valid_subscriber(subscriber)

        # Acquire lock to ensure thread safety.
        with self.__thread_lock:
            # Check if the subscriber is registered; return False if not.
            if valid_subscriber not in self.__subscribers:
                return False

            # Remove the subscriber from the observable.
            self.__subscribers.remove(valid_subscriber)

        # Log the removal if the debug mode is enabled
        if self.__logger.debug_enabled:
            self.__logger.debug(action="Removed:", msg=f"{valid_subscriber}")

        return True

    def remove_all(self) -> bool:
        """
        Remove all subscribers from the observable.

        :return: `True` if the observable was successfully cleared; `False`
            if the observable was already empty.
        """
        # Acquire lock to ensure thread safety
        with self.__thread_lock:
            # Check if the observable is already empty
            if not self.__subscribers:
                return False

            # Clear the observable
            self.__subscribers.clear()

        if self.__logger.debug_enabled:
            self.__logger.debug(action="Removed:", msg="All subscribers.")

        return True


Completed = Observable.Completed()
"""Signal raised to indicate that the observable has completed emitting values."""
