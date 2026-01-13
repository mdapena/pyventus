from asyncio import gather
from collections.abc import Awaitable, Callable
from typing import Generic, TypeAlias, TypeVar, final

from typing_extensions import Self, overload, override

from ...core.exceptions import PyventusException
from ...core.processing.asyncio.asyncio_processing_service import AsyncIOProcessingService
from ...core.utils import CallableWrapper
from ..subscribers import CompleteCallbackType, ErrorCallbackType, NextCallbackType, Subscriber
from .observable import Observable

_OutT = TypeVar("_OutT", covariant=True)
"""A generic type representing the value that will be streamed through the ObservableValue."""

ObservableValueValidatorType: TypeAlias = Callable[[_OutT], None | Awaitable[None]]
"""Type alias for an ObservableValue validator."""


class ObservableValue(Generic[_OutT], Observable[_OutT]):
    """
    An observable subclass that encapsulates a value and offers a mechanism for streaming its updates reactively.

    **Notes:**

    -   The `ObservableValue` class is a value-centric observable that focuses solely on a single value and its
        changes over time. It notifies subscribers of the next value when valid, of an error when the value is
        deemed invalid by a validator, and of completion when the value is cleared or reset.

    -   Validators are responsible for validating incoming values. When a value is deemed invalid, the validator
        must raise an exception so that an error notification can be triggered. However, despite the value being
        invalid, it is stored alongside the raised exception, ensuring that both remain accessible until a new
        change is made.

    -   Changes to the encapsulated value are managed through a queue, preserving the order of updates and
        preventing inconsistent states and notifications.

    -   Subscribers can be notified of the current value or error upon subscription by setting the `prime_subscriber`
        property of the `subscribe()` method to True.

    -   Changes to the value are delivered to subscribers in a lazy manner, allowing them to receive incremental
        notifications as they occur.
    """

    # Attributes for the ObservableValue
    __slots__ = ("__seed", "__value", "__exception", "__validators", "__processing_service")

    def __init__(
        self,
        seed: _OutT,
        validators: list[ObservableValueValidatorType[_OutT]] | None = None,
        debug: bool | None = None,
    ) -> None:
        """
        Initialize an instance of `ObservableValue`.

        :param seed: The initial value for the `ObservableValue`. This value is used during initialization
            and reset operations, restoring the observable to its original state. No validation is applied
            to this value.
        :param validators: A list of validators that check incoming values. When a value is deemed invalid,
            the validator must raise an exception to trigger an error notification. Validators can be either
            synchronous or asynchronous callables.
        :param debug: Specifies the debug mode for the logger. If `None`, the mode is determined based
            on the execution environment.
        """
        # Initialize the base Observable class with the specified debug mode.
        super().__init__(debug=debug)

        # Check if validators are provided and ensure they are of type list.
        if validators is not None and not isinstance(validators, list):
            raise PyventusException("The 'validators' argument must be a list.")

        # Set the initial seed value and initialize the current value and exception.
        self.__seed: _OutT = seed
        self.__value: _OutT = self.__seed
        self.__exception: Exception | None = None

        # Wrap validators in a unified interface if they are provided.
        self.__validators: list[CallableWrapper[[_OutT], None]] | None = (
            [CallableWrapper(validator, force_async=False) for validator in validators] if validators else None
        )

        # Create an AsyncIO processing service to manage value updates and notifications.
        # The enforce_submission_order option is enabled to ensure that changes are processed sequentially.
        self.__processing_service: AsyncIOProcessingService = AsyncIOProcessingService(enforce_submission_order=True)

    @final  # Prevent overriding in subclasses to maintain the integrity of the _OutT type.
    async def _set_value(self, value: _OutT) -> None:  # type: ignore[misc]
        """
        Update the current value to the specified one.

        The provided value is validated against the defined validators. If it is deemed valid, it is stored,
        and the next notification is triggered. If the value is considered invalid by any of the validators,
        it is stored alongside the raised exception, and an error notification is issued.

        :param value: The value to set as the current value.
        :return: None.
        """
        try:
            # Validate the value using defined validators, if any.
            if self.__validators:
                await gather(*[validator.execute(value) for validator in self.__validators])

            # Acquire lock to ensure thread safety.
            # Update the current value and reset the exception.
            with self._thread_lock:
                self.__value = value
                self.__exception = None

            # Notify subscribers of the new valid value.
            await self._emit_next(value)
        except Exception as exception:
            # Acquire lock to ensure thread safety.
            # Store the current value and the raised exception.
            with self._thread_lock:
                self.__value = value
                self.__exception = exception

            # Notify subscribers of the error encountered.
            await self._emit_error(exception)

    async def _clear_value(self) -> None:
        """
        Clear the current value and reset it to its initial state.

        This operation will trigger the completion notification and the removal of all current subscribers.

        :return: None
        """
        # Acquire a lock to ensure thread safety.
        # Reset the value to the initial state and clear any exceptions.
        with self._thread_lock:
            self.__value = self.__seed
            self.__exception = None

        # Notify subscribers that the value has been cleared and reset.
        await self._emit_complete()

    @property
    def value(self) -> _OutT:
        """
        Retrieve the current value.

        :return: The current value.
        """
        return self.get_value()

    @value.setter
    @final  # Prevent overriding in subclasses to maintain the integrity of the _OutT type.
    def value(self, value: _OutT) -> None:  # type: ignore[misc]
        """
        Update the current value to the specified one.

        The provided value is validated against the defined validators. If it is deemed valid, it is stored,
        and the next notification is triggered. If the value is considered invalid by any of the validators,
        it is stored alongside the raised exception, and an error notification is issued.

        :param value: The value to set as the current value.
        :return: None.
        """
        self.set_value(value)

    @property
    def error(self) -> Exception | None:
        """
        Retrieve the current error, or None if no error exists.

        :return: The current error, or None if no error exists.
        """
        with self._thread_lock:
            return self.__exception

    @property
    def has_error(self) -> bool:
        """
        Determine whether an error exists.

        :return: `True` if there is an error; otherwise, `False`.
        """
        with self._thread_lock:
            return self.__exception is not None

    def get_value(self) -> _OutT:
        """
        Retrieve the current value.

        :return: The current value.
        """
        with self._thread_lock:
            return self.__value

    @final  # Prevent overriding in subclasses to maintain the integrity of the _OutT type.
    def set_value(self, value: _OutT) -> None:  # type: ignore[misc]
        """
        Update the current value to the specified one.

        The provided value is validated against the defined validators. If it is deemed valid, it is stored,
        and the next notification is triggered. If the value is considered invalid by any of the validators,
        it is stored alongside the raised exception, and an error notification is issued.

        :param value: The value to set as the current value.
        :return: None.
        """
        self.__processing_service.submit(self._set_value, value)

    def clear_value(self) -> None:
        """
        Clear the current value and reset it to its initial state.

        This operation will trigger the completion notification and the removal of all current subscribers.

        :return: None
        """
        self.__processing_service.submit(self._clear_value)

    @overload
    def subscribe(
        self,
        *,
        force_async: bool = False,
        stateful_subctx: bool = False,
        prime_subscriber: bool = False,
    ) -> "Observable.ObservableSubCtx[Self, _OutT]": ...

    @overload
    def subscribe(
        self,
        next_callback: NextCallbackType[_OutT] | None = None,
        error_callback: ErrorCallbackType | None = None,
        complete_callback: CompleteCallbackType | None = None,
        *,
        force_async: bool = False,
        prime_subscriber: bool = False,
    ) -> Subscriber[_OutT]: ...

    @override
    def subscribe(
        self,
        next_callback: NextCallbackType[_OutT] | None = None,
        error_callback: ErrorCallbackType | None = None,
        complete_callback: CompleteCallbackType | None = None,
        *,
        force_async: bool = False,
        stateful_subctx: bool = False,
        prime_subscriber: bool = False,
    ) -> Subscriber[_OutT] | Observable.ObservableSubCtx[Self, _OutT]:
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
        :param prime_subscriber: A boolean flag that determines whether to prime the subscriber with the
            current value or error upon subscription.
        :return: A `Subscriber` if callbacks are provided; otherwise, an `ObservableSubCtx`.
        """
        # Perform the subscription.
        result: Subscriber[_OutT] | Observable.ObservableSubCtx[Self, _OutT] = super().subscribe(
            next_callback=next_callback,
            error_callback=error_callback,
            complete_callback=complete_callback,
            force_async=force_async,
            stateful_subctx=stateful_subctx,
        )  # type: ignore[call-overload]

        # If the result is of type Subscriber and the prime_subscriber property
        # is set to True, initialize the subscriber with the current value or error.
        if isinstance(result, Subscriber) and prime_subscriber:
            # Acquire lock to ensure thread safety.
            with self._thread_lock:
                value: _OutT = self.__value
                exception: Exception | None = self.__exception

            # Notify the subscriber accordingly.
            if exception is None:
                self.__processing_service.submit(self._emit_next, value=value, selected_subscribers={result})
            else:
                self.__processing_service.submit(self._emit_error, exception=exception, selected_subscribers={result})

        # Return the result of the subscription.
        return result

    async def wait_for_tasks(self) -> None:
        """
        Wait for all background tasks associated with the `ObservableValue` to complete.

        It ensures that any ongoing tasks are finished before proceeding.

        :return: None.
        """
        # Await the completion of all background tasks.
        while self.__processing_service.task_count:
            await self.__processing_service.wait_for_tasks()
