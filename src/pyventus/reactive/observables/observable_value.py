from collections.abc import Awaitable, Callable
from typing import Generic, Literal, TypeAlias, TypeVar, final

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

    -   Updates to the encapsulated value are managed through a queue, preserving the order of changes and
        preventing inconsistent states and notifications.

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
                for validator in self.__validators:
                    await validator.execute(value)

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

    @property
    def error(self) -> Exception | None:
        """
        Retrieve the current error, or None if no error exists.

        :return: The current error, or None if no error exists.
        """
        with self._thread_lock:
            return self.__exception

    def get_value(self) -> _OutT:
        """
        Retrieve the current value.

        :return: The current value.
        """
        with self._thread_lock:
            return self.__value

    @overload
    def set_value(self, value: _OutT) -> None: ...  # type: ignore[misc]

    @overload
    def set_value(self, value: _OutT, wait: Literal[False]) -> None: ...  # type: ignore[misc]

    @overload
    def set_value(self, value: _OutT, wait: Literal[True]) -> Awaitable[None]: ...  # type: ignore[misc]

    @final  # Prevent overriding in subclasses to maintain the integrity of the _OutT type.
    def set_value(self, value: _OutT, wait: bool = False) -> Awaitable[None] | None:  # type: ignore[misc,return]
        """
        Update the current value to the specified one.

        The provided value is validated against the defined validators. If it is deemed valid, it is stored,
        and the next notification is triggered. If the value is considered invalid by any of the validators,
        it is stored alongside the raised exception, and an error notification is issued.

        :param value: The value to set as the current value.
        :param wait: If set to `True`, the awaitable of the operation is returned, so it can be awaited as
            needed before proceeding. If set to `False` (default), the operation runs as a background task,
            and no value is returned.
        :return: None, or an awaitable if `wait` is set to `True`.
        """
        # Ensure that the 'wait' parameter is of boolean type.
        if not isinstance(wait, bool):
            raise PyventusException("The 'wait' argument must be a boolean value.")

        if wait:
            # Return the operation's awaitable for the caller.
            return self._set_value(value)
        else:
            # Submit the operation to the AsyncIO processor.
            self.__processing_service.submit(self._set_value, value)

    @overload
    def clear_value(self) -> None: ...

    @overload
    def clear_value(self, wait: Literal[False]) -> None: ...

    @overload
    def clear_value(self, wait: Literal[True]) -> Awaitable[None]: ...

    def clear_value(self, wait: bool = False) -> Awaitable[None] | None:  # type: ignore[return]
        """
        Clear the current value and reset it to its initial state.

        This operation will trigger the completion notification and the removal of all current subscribers.

        :param wait: If set to `True`, the awaitable of the operation is returned, so it can be awaited as
            needed before proceeding. If set to `False` (default), the operation runs as a background task,
            and no value is returned.
        :return: None, or an awaitable if `wait` is set to `True`.
        """
        # Ensure that the 'wait' parameter is of boolean type.
        if not isinstance(wait, bool):
            raise PyventusException("The 'wait' argument must be a boolean value.")

        if wait:
            # Return the operation's awaitable for the caller.
            return self._clear_value()
        else:
            # Submit the operation to the AsyncIO processor.
            self.__processing_service.submit(self._clear_value)

    @overload
    def prime_subscribers(self, subscribers: set[Subscriber[_OutT]]) -> None: ...

    @overload
    def prime_subscribers(self, subscribers: set[Subscriber[_OutT]], wait: Literal[False]) -> None: ...

    @overload
    def prime_subscribers(self, subscribers: set[Subscriber[_OutT]], wait: Literal[True]) -> Awaitable[None]: ...

    def prime_subscribers(self, subscribers: set[Subscriber[_OutT]], wait: bool = False) -> Awaitable[None] | None:  # type: ignore[return]
        """
        Prime the specified subscribers with the current value or error.

        :param subscribers: The set of subscribers to be primed.
        :param wait: If set to `True`, the awaitable of the operation is returned, so it can be awaited as
            needed before proceeding. If set to `False` (default), the operation runs as a background task,
            and no value is returned.
        :return: None, or an awaitable if `wait` is set to `True`.
        """
        # Ensure that the 'wait' parameter is of boolean type.
        if not isinstance(wait, bool):
            raise PyventusException("The 'wait' argument must be a boolean value.")

        # Validate the given subscribers.
        valid_subscribers: set[Subscriber[_OutT]] = {
            self.get_valid_subscriber(subscriber) for subscriber in subscribers
        }

        # Acquire lock to ensure thread safety.
        with self._thread_lock:
            value: _OutT = self.__value
            exception: Exception | None = self.__exception

        # Notify the subscribers accordingly.
        if wait:
            # Return the operation's awaitable for the caller.
            if exception is None:
                return self._emit_next(value=value, selected_subscribers=valid_subscribers)
            return self._emit_error(exception=exception, selected_subscribers=valid_subscribers)
        else:
            # Submit the notification operation to the AsyncIO processor.
            if exception is None:
                self.__processing_service.submit(
                    self._emit_next,
                    value=value,
                    selected_subscribers=valid_subscribers,
                )
            else:
                self.__processing_service.submit(
                    self._emit_error,
                    exception=exception,
                    selected_subscribers=valid_subscribers,
                )

    async def wait_for_tasks(self) -> None:
        """
        Wait for all background tasks associated with the `ObservableValue` to complete.

        It ensures that any ongoing tasks are finished before proceeding.

        :return: None.
        """
        # Await the completion of all background tasks.
        await self.__processing_service.wait_for_tasks()
