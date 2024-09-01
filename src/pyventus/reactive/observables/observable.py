from asyncio import Task, create_task, gather, run
from collections.abc import AsyncGenerator, Awaitable, Callable, Generator
from concurrent.futures import ThreadPoolExecutor
from sys import gettrace
from threading import Lock
from typing import Any, Generic, TypeAlias, TypeVar, final, overload

from typing_extensions import override

from ...core.exceptions import PyventusException
from ...core.loggers import Logger
from ...core.subscriptions import SubscriptionContext
from ...core.utils import (
    attributes_repr,
    formatted_repr,
    get_callable_name,
    is_callable_async,
    is_callable_generator,
    is_loop_running,
    validate_callable,
)
from ..subscribers import CompleteCallbackType, ErrorCallbackType, NextCallbackType, Subscriber

_OutT = TypeVar("_OutT", covariant=True)
"""A generic type representing the value that will be streamed through the observable."""

_CtxT = TypeVar("_CtxT", contravariant=True)
"""A generic type representing the value type for the Observable and Subscriber within the subscription context."""

ObservableCallbackReturnType: TypeAlias = (
    Generator[_OutT, None, None] | AsyncGenerator[_OutT, None] | Awaitable[_OutT] | _OutT
)
"""Type alias for the return type of the observable callback."""

ObservableCallbackType: TypeAlias = Callable[..., ObservableCallbackReturnType[_OutT]]
"""Type alias for the observable callback."""


class Observable(Generic[_OutT]):
    """
    A class that provides a lazy push-style notification mechanism for streaming data to a set of subscribers.

    **Notes:**

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
    class ObservableSubscriptionContext(Generic[_CtxT], SubscriptionContext["Observable[_CtxT]", Subscriber[_CtxT]]):
        """
        A context manager for observable subscriptions.

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

        # Attributes for the ObservableSubscriptionContext
        __slots__ = ("__next_callback", "__error_callback", "__complete_callback", "__force_async")

        def __init__(self, observable: "Observable[_CtxT]", force_async: bool, is_stateful: bool) -> None:
            """
            Initialize an instance of `ObservableSubscriptionContext`.

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
            self.__next_callback: NextCallbackType[_CtxT] | None = None
            self.__error_callback: ErrorCallbackType | None = None
            self.__complete_callback: CompleteCallbackType | None = None
            self.__force_async: bool = force_async

        @override
        def __repr__(self) -> str:  # pragma: no cover
            return formatted_repr(
                instance=self,
                info=(
                    attributes_repr(
                        next_callback=self.__next_callback,
                        error_callback=self.__error_callback,
                        complete_callback=self.__complete_callback,
                        force_async=self.__force_async,
                    )
                    + f", {super().__repr__()}"
                ),
            )

        @override
        def _exit(self) -> Subscriber[_CtxT]:
            # Ensure that the source is not None
            if self._source is None:
                raise PyventusException("The subscription context is closed.")

            # Ensure that at least one callback is defined before performing the subscription
            if self.__next_callback is None and self.__error_callback is None and self.__complete_callback is None:
                raise PyventusException("At least one callback must be defined before performing the subscription.")

            # Subscribe the defined callbacks to the specified
            # observable and store the returned subscriber.
            subscriber: Subscriber[_CtxT] = self._source.subscribe(
                next_callback=self.__next_callback,
                error_callback=self.__error_callback,
                complete_callback=self.__complete_callback,
                force_async=self.__force_async,
            )

            # Remove context-specific attributes
            del self.__next_callback, self.__error_callback, self.__complete_callback, self.__force_async

            # Return the subscriber
            return subscriber

        def on_next(self, callback: NextCallbackType[_CtxT]) -> NextCallbackType[_CtxT]:
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
            self, callback: NextCallbackType[_CtxT]
        ) -> (
            tuple[NextCallbackType[_CtxT], "Observable.ObservableSubscriptionContext[_CtxT]"] | NextCallbackType[_CtxT]
        ):
            """
            Subscribe the decorated callback as the observer's `next` function for the specified observable.

            :param callback: The callback to be executed when the observable emits a new value.
            :return: A tuple containing the decorated callback and its subscription context
                if the context is stateful; otherwise, returns the decorated callback alone.
            """
            # Store the provided callback in the subscription context
            self.__next_callback = callback

            # Set error and complete callbacks to None
            self.__error_callback = None
            self.__complete_callback = None

            # Determine if the subscription context is stateful
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
        if not isinstance(subscriber, Subscriber):
            raise PyventusException("The 'subscriber' argument must be an instance of Subscriber.")
        return subscriber

    # Attributes for the Observable
    __slots__ = (
        "__args",
        "__kwargs",
        "__callback",
        "__callback_name",
        "__is_callback_async",
        "__is_callback_generator",
        "__subscribers",
        "__background_tasks",
        "__thread_lock",
        "__logger",
    )

    def __init__(
        self,
        callback: ObservableCallbackType[_OutT],
        args: tuple[Any, ...] | None = None,
        kwargs: dict[str, Any] | None = None,
        debug: bool | None = None,
    ) -> None:
        """
        Initialize an instance of `Observable`.

        :param callback: A callback function that defines the behavior of the `Observable`.
            This function is responsible for generating the stream of data emitted to subscribers.
        :param args: Positional arguments to be passed to the callback.
        :param kwargs: Keyword arguments to be passed to the callback.
        :param debug: Specifies the debug mode for the logger. If `None`,
            the mode is determined based on the execution environment.
        """
        # Validate that the provided callback
        validate_callable(callback)

        # Store the callback and its metadata
        self.__callback: ObservableCallbackType[_OutT] = callback
        self.__callback_name: str = get_callable_name(callback)
        self.__is_callback_async: bool = is_callable_async(callback)
        self.__is_callback_generator: bool = is_callable_generator(callback)

        # Store the positional and keyword arguments for the callback
        self.__args: tuple[Any, ...] = args if args else ()
        self.__kwargs: dict[str, Any] = kwargs if kwargs else {}

        # Initialize the set of subscribers
        self.__subscribers: set[Subscriber[_OutT]] = set()

        # Initialize the set of background tasks
        self.__background_tasks: set[Task[None]] = set()

        # Create a lock object for thread synchronization
        self.__thread_lock: Lock = Lock()

        # Set up the logger with the appropriate debug mode
        self.__logger: Logger = Logger(
            name=self.__class__.__name__,
            debug=debug if debug is not None else bool(gettrace() is not None),
        )

    def __repr__(self) -> str:  # pragma: no cover
        """
        Retrieve a string representation of the instance.

        :return: A string representation of the instance.
        """
        return formatted_repr(
            instance=self,
            info=attributes_repr(
                args=self.__args,
                kwargs=self.__kwargs,
                callback=self.__callback_name,
                is_callback_async=self.__is_callback_async,
                is_callback_generator=self.__is_callback_generator,
                subscribers=self.__subscribers,
                background_tasks=self.__background_tasks,
                thread_lock=self.__thread_lock,
                debug=self.__logger.debug_enabled,
            ),
        )

    def __remove_background_task(self, task: Task[None]) -> None:
        """
        Remove the specified background task from the task registry.

        :param task:  The background task to be removed from the registry.
        :return: None.
        """
        with self.__thread_lock:
            self.__background_tasks.discard(task)

    async def __execute(self) -> None:
        """
        Execute the main callback of the `Observable` and manages the emission of data to subscribers.

        This method is responsible for invoking the Observable's callback, emitting the stream of
        data to subscribers, and managing the execution of their `next`, `error`, and `completion`
        workflows.

        :return: None
        """
        # Execute the main callback, handling
        # any exceptions that may occur
        try:
            if self.__is_callback_generator:
                # If the callback is a generator, initialize it to start retrieving values
                generator = self.__callback(*self.__args, **self.__kwargs)

                # Retrieve and emit values from the generator
                # to all subscribers concurrently
                while True:
                    await gather(
                        *[
                            subscriber.next(
                                value=(
                                    await anext(generator)  # type: ignore[arg-type]
                                    if self.__is_callback_async
                                    else next(generator)  # type: ignore[arg-type]
                                ),
                            )
                            for subscriber in self.get_subscribers()
                        ]
                    )
            else:
                # If the callback is a regular function, invoke it and
                # emit the result to all subscribers concurrently
                await gather(
                    *[
                        subscriber.next(
                            value=(
                                await self.__callback(*self.__args, **self.__kwargs)  # type: ignore[misc]
                                if self.__is_callback_async
                                else self.__callback(*self.__args, **self.__kwargs)
                            ),
                        )
                        for subscriber in self.get_subscribers()
                    ]
                )

                # Signal that the observable has
                # completed emitting values
                raise Completed
        except (StopIteration, StopAsyncIteration):
            pass  # Ignore StopIteration signals from sync or async generators
        except Observable.Completed:
            # Notify all subscribers that the Observable has completed emitting values
            await gather(*[subscriber.complete() for subscriber in self.get_subscribers()])
        except Exception as exception:
            # Notify all subscribers of any errors encountered during callback execution
            await gather(*[subscriber.error(exception) for subscriber in self.get_subscribers()])

    def get_subscribers(self) -> set[Subscriber[_OutT]]:
        """
        Retrieve all registered subscribers.

        :return: A set of all registered subscribers.
        """
        with self.__thread_lock:
            return self.__subscribers.copy()

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
    ) -> "Observable.ObservableSubscriptionContext[_OutT]": ...

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
    ) -> Subscriber[_OutT] | "Observable.ObservableSubscriptionContext[_OutT]":
        """
        Subscribe the specified callbacks to the current `Observable`.

        This method can be utilized in three ways:

        -   As a regular function: Automatically creates and subscribes an observer
            with the specified callbacks.

        -   As a decorator: Creates and subscribes an observer, using the decorated
            callback as the next callback.

        -   As a context manager: Enables a step-by-step definition of the observer's callbacks
            prior to subscription, which occurs immediately after exiting the context.

        :param next_callback: The callback to be executed when the observable emits a new value.
        :param error_callback: The callback to be executed when the observable encounters an error.
        :param complete_callback: The callback that will be executed when the observable has completed emitting values.
        :param force_async: Determines whether to force all callbacks to run asynchronously.
        :param stateful_subctx: A flag indicating whether the subscription context preserves its state (`stateful`)
            or not (`stateless`) after exiting the subscription block. If `True`, the context retains its state,
            allowing access to stored objects, including the `observable` and the `subscriber` object. If `False`,
            the context is stateless, and the stored state is cleared upon exiting the subscription block to
            prevent memory leaks. The term 'subctx' refers to 'Subscription Context'.
        :return: A `Subscriber` if callbacks are provided; otherwise, an `ObservableSubscriptionContext`.
        """
        # If no callbacks are provided, create a subscription context for progressive definition
        if next_callback is None and error_callback is None and complete_callback is None:
            return Observable.ObservableSubscriptionContext[_OutT](
                observable=self, force_async=force_async, is_stateful=stateful_subctx
            )
        else:
            # Create a subscriber with the provided callbacks
            subscriber = Subscriber[_OutT](
                teardown_callback=self.remove_subscriber,
                next_callback=next_callback,
                error_callback=error_callback,
                complete_callback=complete_callback,
                force_async=force_async,
            )

            # Acquire lock to ensure thread safety
            with self.__thread_lock:
                # Add the subscriber to the observable
                self.__subscribers.add(subscriber)

            # Return the subscriber
            return subscriber

    def remove_subscriber(self, subscriber: Subscriber[_OutT]) -> bool:
        """
        Remove the specified subscriber from the observable.

        :param subscriber: The subscriber to be removed from the observable.
        :return: `True` if the subscriber was successfully removed; `False` if
            the subscriber was not found in the observable.
        """
        # Get the valid subscriber instance
        valid_subscriber: Subscriber[_OutT] = self.get_valid_subscriber(subscriber)

        # Acquire lock to ensure thread safety
        with self.__thread_lock:
            # Check if the subscriber is registered; return False if not
            if valid_subscriber not in self.__subscribers:
                return False

            # Remove the subscriber from the observable
            self.__subscribers.remove(valid_subscriber)

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

        return True

    async def wait_for_tasks(self) -> None:
        """
        Wait for all background tasks associated with the `Observable` to complete.

        It ensures that any ongoing tasks are finished before proceeding.

        :return: None.
        """
        # Acquire lock to ensure thread safety
        with self.__thread_lock:
            # Retrieve the current set of background tasks and clear the registry
            tasks: set[Task[None]] = self.__background_tasks
            self.__background_tasks = set()

        # Await the completion of all background tasks
        await gather(*tasks)

    def __call__(self, executor: ThreadPoolExecutor | None = None) -> None:
        """
        Execute the current `Observable`.

        Depending on the context, Observables manage their execution differently:

        -   In a synchronous environment, a new event loop is started to execute
            the `Observable`. The loop then waits for all scheduled tasks to
            finish before closing, preserving synchronous execution while
            still benefiting from concurrent execution.

        -   In an asynchronous setting, the `Observable` is scheduled as a
            background task within the running asyncio event loop.

        -   When a thread-based executor is provided, the `Observable`'s
            execution is submitted to the given thread.

        :param executor: An optional `ThreadPoolExecutor` instance for executing
            the `Observable` within the given thread-based executor.
        :return: None
        """
        if executor is None:
            # Check if there is an active event loop
            loop_running: bool = is_loop_running()

            if loop_running:
                # Schedule the Observable execution in the running loop as a background task
                task: Task[None] = create_task(self.__execute())

                # Remove the Task from the set of background tasks upon completion
                task.add_done_callback(self.__remove_background_task)

                # Acquire lock to ensure thread safety
                with self.__thread_lock:
                    # Add the Task to the set of background tasks
                    self.__background_tasks.add(task)
            else:
                # Execute the Observable in a new event loop
                # and wait for its execution to complete
                run(self.__execute())
        else:
            # Validate that the executor is an instance of ThreadPoolExecutor
            if not isinstance(executor, ThreadPoolExecutor):
                raise PyventusException("The 'executor' argument must be an instance of ThreadPoolExecutor.")

            # Submit the Observable's execution to
            # the provided thread-based executor
            executor.submit(self)


Completed = Observable.Completed()
"""Signal raised to indicate that the observable has completed emitting values and will not emit any more."""
