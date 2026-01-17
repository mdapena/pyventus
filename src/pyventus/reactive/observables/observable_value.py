from collections.abc import Awaitable, Callable
from typing import Generic, TypeAlias, TypeVar, final

from typing_extensions import overload, override

from ...core.exceptions import PyventusException
from ...core.processing.asyncio.asyncio_processing_service import AsyncIOProcessingService
from ...core.utils import CallableWrapper, attributes_repr, formatted_repr
from ..subscribers import Subscriber
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
        deemed invalid by a validator, and of completion when the value is cleared and reset.

    -   Validators are responsible for validating incoming values. When a value is deemed invalid, the validator
        must raise an exception so that an error notification can be triggered. However, despite the value being
        invalid, it is stored alongside the raised exception, ensuring that both remain accessible until a new
        change is made.

    -   Update and retrieval operations are managed through a queue, ensuring that their order is preserved and
        no inconsistent states or notifications are generated during execution.

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

        :param seed: The initial value for the observable. This value is used during initialization and reset
            operations to restore the observable to its original state. No validation is applied to this value.
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

    @override
    def __repr__(self) -> str:
        return formatted_repr(
            instance=self,
            info=(
                attributes_repr(
                    seed=self.__seed,
                    value=self.__value,
                    exception=self.__exception,
                    validators=self.__validators,
                    processing_service=self.__processing_service,
                )
                + f", {super().__repr__()}"
            ),
        )

    async def _get_error(self, callback: CallableWrapper[[Exception | None], None]) -> None:
        """
        Retrieve the current error, if any, through the specified callback.

        :param callback: The callback that receives the current error, if any.
        :return: None.
        """
        with self._thread_lock:
            exception: Exception | None = self.__exception
        await callback.execute(exception)

    async def _get_value(self, callback: CallableWrapper[[_OutT], None]) -> None:
        """
        Retrieve the current value through the specified callback.

        :param callback: The callback that receives the current value.
        :return: None.
        """
        with self._thread_lock:
            value: _OutT = self.__value
        await callback.execute(value)

    @final  # Prevent overriding in subclasses to maintain the integrity of the _OutT type.
    async def _set_value(self, value: _OutT, subscribers: tuple[Subscriber[_OutT], ...]) -> None:  # type: ignore[misc]
        """
        Update the current value to the specified one.

        The provided value is validated against the defined validators. If it is deemed valid, it is stored,
        and the next notification is triggered. If the value is considered invalid by any of the validators,
        it is stored alongside the raised exception, and an error notification is issued.

        :param value: The value to set as the current value.
        :param subscribers: The collection of subscribers to be notified of the value update.
        :return: None.
        """
        try:
            # Validate the value using defined validators, if any.
            if self.__validators:
                for validator in self.__validators:
                    await validator.execute(value)

            # Acquire lock to ensure thread safety.
            # Update the current value and reset the exception.
            with self._thread_lock:
                self.__value = value
                self.__exception = None

            # Notify subscribers of the new valid value.
            await self._emit_next(value, subscribers)
        except Exception as exception:
            # Acquire lock to ensure thread safety.
            # Store the current value and the raised exception.
            with self._thread_lock:
                self.__value = value
                self.__exception = exception

            # Notify subscribers of the error encountered.
            await self._emit_error(exception, subscribers)

    async def _clear_value(self, subscribers: tuple[Subscriber[_OutT], ...]) -> None:
        """
        Clear the current value and reset it to its initial state.

        This operation will trigger the completion notification and remove the specified subscribers.

        :param subscribers: The collection of subscribers to be notified of the value reset.
        :return: None.
        """
        # Acquire a lock to ensure thread safety.
        with self._thread_lock:
            self.__value = self.__seed
            self.__exception = None

        # Notify subscribers that the value has been cleared and reset.
        await self._emit_complete(subscribers)

    async def _prime_subscribers(self, subscribers: set[Subscriber[_OutT]]) -> None:
        """
        Prime the specified subscribers with the current value or error.

        :param subscribers: The set of subscribers to be primed.
        :return: None.
        """
        # Acquire a lock to ensure thread safety.
        with self._thread_lock:
            value: _OutT = self.__value
            exception: Exception | None = self.__exception

        # Notify the subscribers accordingly.
        if exception is None:
            await self._emit_next(value, subscribers)
        else:
            await self._emit_error(exception, subscribers)

    def get_error(
        self, callback: Callable[[Exception | None], None | Awaitable[None]], force_async: bool = False
    ) -> None:
        """
        Retrieve the current error, if any.

        The current error will be received through the parameters of the provided callback, and its execution will be
        enqueued with the other operations to ensure that the received error corresponds to the correct state at the
        time the current method was invoked, preventing any inconsistencies.

        :param callback: The callback to be invoked with the current error, if any.
        :param force_async: Determines whether to force the callback to run asynchronously. If `True`, the synchronous
            callback will be converted to run asynchronously in a thread pool using the `asyncio.to_thread` function.
            If `False`, the callback will run synchronously or asynchronously as defined.
        :return: None.
        :raises PyventusException: If the provided callback is a generator.
        """
        # Wrap the callback to ensure a consistent interface for invocation.
        valid_callback: CallableWrapper[[Exception | None], None] = CallableWrapper(callback, force_async=force_async)

        # Verify that the provided callback is not a generator.
        if valid_callback.is_generator:
            raise PyventusException("The 'callback' argument cannot be a generator.")

        # Schedule the processing of the error retrieval with the provided callback, ensuring that the received error
        # corresponds to the state at the time the `get_error` method was invoked, preventing any inconsistencies.
        self.__processing_service.submit(self._get_error, valid_callback)

    def get_value(self, callback: Callable[[_OutT], None | Awaitable[None]], force_async: bool = False) -> None:
        """
        Retrieve the current value.

        The current value will be received through the parameters of the provided callback, and its execution will be
        enqueued with the other operations to ensure that the received value corresponds to the correct state at the
        time the current method was invoked, preventing any inconsistencies.

        :param callback: The callback to be invoked with the current value.
        :param force_async: Determines whether to force the callback to run asynchronously. If `True`, the synchronous
            callback will be converted to run asynchronously in a thread pool using the `asyncio.to_thread` function.
            If `False`, the callback will run synchronously or asynchronously as defined.
        :return: None.
        :raises PyventusException: If the provided callback is a generator.
        """
        # Wrap the callback to ensure a consistent interface for invocation.
        valid_callback: CallableWrapper[[_OutT], None] = CallableWrapper(callback, force_async=force_async)

        # Verify that the provided callback is not a generator.
        if valid_callback.is_generator:
            raise PyventusException("The 'callback' argument cannot be a generator.")

        # Schedule the processing of the value retrieval with the provided callback, ensuring that the received value
        # corresponds to the state at the time the `get_value` method was invoked, preventing any inconsistencies.
        self.__processing_service.submit(self._get_value, valid_callback)

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
        with self._thread_lock:
            subscribers: tuple[Subscriber[_OutT], ...] = tuple(self._subscribers)
        self.__processing_service.submit(self._set_value, value, subscribers)

    def clear_value(self) -> None:
        """
        Clear the current value and reset it to its initial state.

        This operation will trigger the completion notification and the removal of all current subscribers.

        :return: None.
        """
        with self._thread_lock:
            subscribers: tuple[Subscriber[_OutT], ...] = tuple(self._subscribers)
            self._subscribers.clear()
        self.__processing_service.submit(self._clear_value, subscribers)

    @overload
    def prime_subscribers(self, subscriber: Subscriber[_OutT], /) -> Subscriber[_OutT]: ...

    @overload
    def prime_subscribers(self, *subscribers: Subscriber[_OutT]) -> tuple[Subscriber[_OutT], ...]: ...

    def prime_subscribers(self, *subscribers: Subscriber[_OutT]) -> Subscriber[_OutT] | tuple[Subscriber[_OutT], ...]:
        """
        Prime the specified subscribers with the current value or error.

        :param subscribers: One or more subscribers to be primed.
        :return: The same subscribers as input.
        :raises PyventusException: If no subscribers are given.
        """
        if not subscribers:
            raise PyventusException("At least one subscriber must be provided.")

        if len(subscribers) == 1:
            self.__processing_service.submit(
                self._prime_subscribers,
                {self.get_valid_subscriber(subscribers[0])},
            )
            return subscribers[0]
        else:
            self.__processing_service.submit(
                self._prime_subscribers,
                {self.get_valid_subscriber(subscriber) for subscriber in subscribers},
            )
            return subscribers

    async def wait_for_tasks(self) -> None:
        """
        Wait for all background tasks associated with the `ObservableValue` to complete.

        It ensures that any ongoing tasks are finished before proceeding.

        :return: None.
        """
        await self.__processing_service.wait_for_tasks()
