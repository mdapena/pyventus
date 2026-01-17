import asyncio
from collections.abc import Callable, Generator
from contextlib import contextmanager
from threading import current_thread, main_thread
from typing import Any

import pytest
from pyventus import PyventusException
from pyventus.reactive import ObservableValue, ObservableValueValidatorType
from pyventus.reactive.subscribers.subscriber import Subscriber

from ....fixtures import CallableMock, DummyCallable
from ....utils import get_private_attr


def assertion(condition: bool, message: str) -> None:
    assert condition, message


class Validators:
    @staticmethod
    def required(value: Any) -> None:
        """Validate that the value is provided."""
        if value is None:
            raise AttributeError("Value is required and cannot be None.")

    @staticmethod
    async def delay(seconds: float) -> None:
        """Introduce a delay for a specified time in seconds."""
        await asyncio.sleep(seconds)

    @staticmethod
    def choices(valid_choices: list[Any]) -> Callable[[Any], None]:
        """Validate that the value is among the valid choices."""

        def validator(value: Any) -> None:
            if value not in valid_choices:
                raise ValueError(f"Value must be one of {valid_choices}. Current value: {value}.")

        return validator


class TestObservableValue:
    # =================================
    # Test Cases for creation
    # =================================

    @pytest.mark.parametrize(
        ["seed", "validators"],
        [
            (0, None),
            (None, []),
            (object(), [CallableMock.Sync()]),
            ("string", [CallableMock.Async()]),
            (False, [*DummyCallable.Sync().ALL]),
            (True, [*DummyCallable.Async().ALL]),
            (..., [*DummyCallable.Sync().ALL, *DummyCallable.Async().ALL]),
        ],
    )
    def test_creation_with_valid_input(
        self, seed: Any, validators: list[ObservableValueValidatorType[Any]] | None
    ) -> None:
        # Arrange/Act
        obsv = ObservableValue[Any](seed=seed, validators=validators)

        # Assert
        assert obsv is not None
        assert isinstance(obsv, ObservableValue)
        assert get_private_attr(obsv, "__seed") is seed
        assert get_private_attr(obsv, "__value") is seed
        assert get_private_attr(obsv, "__exception") is None
        assert (
            not validators
            if (obsv_validators := get_private_attr(obsv, "__validators")) is None
            else len(obsv_validators) == len(validators)  # type: ignore[arg-type]
        )

    # =================================

    @pytest.mark.parametrize(
        ["validators", "exception"],
        [
            ((), PyventusException),
            (..., PyventusException),
            ("str", PyventusException),
            (set(), PyventusException),
            ([DummyCallable.Invalid()], PyventusException),
        ],
    )
    def test_creation_with_invalid_input(self, validators: Any, exception: type[Exception]) -> None:
        # Arrange/Act/Assert
        with pytest.raises(exception):
            ObservableValue(seed=None, validators=validators)

    # =================================
    # Tests Cases for Value retrieval
    # =================================

    def value_retrieval_tests(self) -> ObservableValue[Any]:
        # Arrange
        seed: Any = object()
        value: Any = object()
        assert seed is not value

        # Act: Initial
        obsv = ObservableValue[Any](seed=seed)
        obsv.get_value(  # Assert
            lambda cv: assertion(
                cv is seed,
                f"{cv} is {seed}",
            )
        )

        # Act: Update
        obsv.set_value(value)
        obsv.get_value(  # Assert
            lambda cv: assertion(
                cv is value,
                f"{cv} is {value}",
            )
        )

        with pytest.raises(PyventusException):
            obsv.get_value(DummyCallable.Invalid())  # type: ignore[arg-type]

        with pytest.raises(PyventusException):
            obsv.get_value(DummyCallable.Sync.Generator())  # type: ignore[arg-type]

        with pytest.raises(PyventusException):
            obsv.get_value(DummyCallable.Async.Generator())  # type: ignore[arg-type]

        # Return obsv for any additional processing.
        return obsv

    # =================================

    def test_value_retrieval_in_sync_context(self) -> None:
        self.value_retrieval_tests()

    # =================================

    async def test_value_retrieval_in_async_context(self) -> None:
        await self.value_retrieval_tests().wait_for_tasks()

    # =================================

    def test_value_retrieval_with_force_async_flag(self) -> None:
        # Arrange
        def different_thread(value: int) -> None:
            assert current_thread() is not main_thread()
            assert value == 1

        def same_thread(value: int) -> None:
            assert current_thread() is main_thread()
            assert value == 1

        obsv = ObservableValue[int](seed=1)

        # Act/Assert
        obsv.get_value(different_thread, force_async=True)
        obsv.get_value(same_thread, force_async=False)
        obsv.get_value(same_thread)

    # =================================
    # Tests Cases for Error retrieval
    # =================================

    def error_retrieval_tests(self) -> ObservableValue[Any]:
        # Arrange
        exception: Any = ValueError("Invalid")
        validator: CallableMock.Base = CallableMock.Sync(raise_exception=exception)

        # Act/Assert: Initial
        obsv = ObservableValue[Any](seed=object(), validators=[validator])
        obsv.get_error(
            lambda ce: assertion(
                ce is None,
                f"{ce} is None",
            )
        )

        # Act/Assert: Update
        obsv.set_value(object())
        obsv.get_error(  # Assert
            lambda ce: assertion(
                ce is exception,
                f"{ce} is {exception}",
            )
        )

        with pytest.raises(PyventusException):
            obsv.get_error(DummyCallable.Invalid())  # type: ignore[arg-type]

        with pytest.raises(PyventusException):
            obsv.get_error(DummyCallable.Sync.Generator())  # type: ignore[arg-type]

        with pytest.raises(PyventusException):
            obsv.get_error(DummyCallable.Async.Generator())  # type: ignore[arg-type]

        # Return obsv for any additional processing.
        return obsv

    # =================================

    def test_error_retrieval_in_sync_context(self) -> None:
        self.error_retrieval_tests()

    # =================================

    async def test_error_retrieval_in_async_context(self) -> None:
        await self.error_retrieval_tests().wait_for_tasks()

    # =================================

    def test_error_retrieval_with_force_async_flag(self) -> None:
        # Arrange
        def different_thread(exception: Exception | None) -> None:
            assert current_thread() is not main_thread()
            assert exception is None

        def same_thread(exception: Exception | None) -> None:
            assert current_thread() is main_thread()
            assert exception is None

        obsv = ObservableValue[int](seed=1)

        # Act/Assert
        obsv.get_error(different_thread, force_async=True)
        obsv.get_error(same_thread, force_async=False)
        obsv.get_error(same_thread)

    # =================================
    # Test Cases for validator execution
    # =================================

    @contextmanager
    def validator_execution_tests(self) -> Generator[ObservableValue[Any], None, None]:
        # Arrange
        value1: Any = object()
        value2: Any = object()
        validator1: CallableMock.Base = CallableMock.Sync()
        validator2: CallableMock.Base = CallableMock.Async()
        obsv = ObservableValue[Any](
            seed=None,
            validators=[
                validator1,
                validator2,
            ],
        )

        # Act
        obsv.set_value(value1)
        obsv.set_value(value2)
        obsv.clear_value()

        # Yield control for any additional processing.
        yield obsv

        # Assert
        assert validator1.call_count == validator2.call_count == 2
        assert validator1.last_args == validator2.last_args == (value2,)
        assert validator1.last_kwargs == validator2.last_kwargs == {}

    # =================================

    def test_validator_execution_in_sync_context(self) -> None:
        with self.validator_execution_tests():
            pass

    # =================================

    async def test_validator_execution_in_async_context(self) -> None:
        with self.validator_execution_tests() as obsv:
            await obsv.wait_for_tasks()

    # =================================
    # Test Cases for value update
    # =================================

    def value_update_without_validators_tests(self) -> ObservableValue[Any]:
        # Arrange
        value1: Any = object()
        value2: Any = object()

        # Act: Initial
        obsv = ObservableValue[Any](seed=object())
        obsv.get_value(  # Assert
            lambda cv: assertion(
                cv is not value1 and cv is not value2,
                f"{cv} is not {value1} and {cv} is not {value2}",
            )
        )

        # Act: Update
        obsv.set_value(value1)
        obsv.get_value(  # Assert
            lambda cv: assertion(
                cv is value1 and cv is not value2,
                f"{cv} is {value1} and {cv} is not {value2}",
            )
        )

        # Act: Update
        obsv.set_value(value2)
        obsv.get_value(  # Assert
            lambda cv: assertion(
                cv is not value1 and cv is value2,
                f"{cv} is not {value1} and {cv} is {value2}",
            )
        )

        # Return obsv for any additional processing.
        return obsv

    # =================================

    def test_value_update_without_validators_in_sync_context(self) -> None:
        self.value_update_without_validators_tests()

    # =================================

    async def test_value_update_without_validators_in_async_context(self) -> None:
        await self.value_update_without_validators_tests().wait_for_tasks()

    # =================================

    def value_update_with_validators_tests(self) -> ObservableValue[Any]:
        # Arrange
        value1: Any = object()
        value2: Any = object()
        value3: Any = object()
        value4: Any = object()
        obsv = ObservableValue[Any](
            seed=None,
            validators=[
                Validators.required,
                Validators.choices([value1, value2, value3]),
            ],
        )

        # Act: Initial
        obsv.get_value(  # Assert
            lambda cv: assertion(
                cv is None,
                f"{cv} is None",
            )
        )
        obsv.get_error(  # Assert
            lambda ce: assertion(
                ce is None,
                f"{ce} is None",
            )
        )

        # Act: Valid
        obsv.set_value(value1)
        obsv.get_value(  # Assert
            lambda cv: assertion(
                cv is value1 and cv not in [value2, value3, value4],
                f"{cv} is {value1} and {cv} not in {[value2, value3, value4]}",
            )
        )
        obsv.get_error(  # Assert
            lambda ce: assertion(
                ce is None,
                f"{ce} is None",
            )
        )

        # Act/Assert: Valid
        obsv.set_value(value2)
        obsv.get_value(  # Assert
            lambda cv: assertion(
                cv is value2 and cv not in [value1, value3, value4],
                f"{cv} is {value2} and {cv} not in {[value1, value3, value4]}",
            )
        )
        obsv.get_error(  # Assert
            lambda ce: assertion(
                ce is None,
                f"{ce} is None",
            )
        )

        # Act: Invalid - Last-Validator
        obsv.set_value(value4)
        obsv.get_value(  # Assert
            lambda cv: assertion(
                cv is value4 and cv not in [value1, value2, value3],
                f"{cv} is {value4} and {cv} not in {[value1, value2, value3]}",
            )
        )
        obsv.get_error(  # Assert
            lambda ce: assertion(
                isinstance(ce, ValueError),
                f"isinstance({type(ce)}, ValueError)",
            )
        )

        # Act: Invalid - First-Validator
        obsv.set_value(None)
        obsv.get_value(  # Assert
            lambda cv: assertion(
                cv is None,
                f"{cv} is None",
            )
        )
        obsv.get_error(  # Assert
            lambda ce: assertion(
                isinstance(ce, AttributeError),
                f"isinstance({type(ce)}, AttributeError)",
            )
        )

        # Act: Valid - Error/Reset
        obsv.set_value(value3)
        obsv.get_value(  # Assert
            lambda cv: assertion(
                cv is value3 and cv not in [value1, value2, value4],
                f"{cv} is {value3} and {cv} not in {[value1, value2, value4]}",
            )
        )
        obsv.get_error(  # Assert
            lambda ce: assertion(
                ce is None,
                f"{ce} is None",
            )
        )

        # Return obsv for any additional processing.
        return obsv

    # =================================

    def test_value_update_with_validators_in_sync_context(self) -> None:
        self.value_update_with_validators_tests()

    # =================================

    async def test_value_update_with_validators_in_async_context(self) -> None:
        await self.value_update_with_validators_tests().wait_for_tasks()

    # =================================
    # Test Cases for value update order
    # =================================

    def value_update_order_tests(self) -> ObservableValue[float]:
        # Arrange
        obsv = ObservableValue[float](
            seed=0.0,
            validators=[
                Validators.required,
                Validators.delay,
            ],
        )

        # Act
        obsv.set_value(0.0035)
        obsv.set_value(0.0025)
        obsv.set_value(0.0015)
        obsv.set_value(0.0005)

        # Assert
        obsv.get_value(
            lambda cv: assertion(
                cv == 0.0005,
                f"{cv} == 0.0005",
            )
        )
        obsv.get_error(
            lambda ce: assertion(
                ce is None,
                f"{ce} is None",
            )
        )

        # Return obsv for any additional processing.
        return obsv

    # =================================

    def test_value_update_order_in_sync_context(self) -> None:
        self.value_update_order_tests()

    # =================================

    async def test_value_update_order_in_async_context(self) -> None:
        await self.value_update_order_tests().wait_for_tasks()

    # =================================
    # Test Cases for clear value
    # =================================

    def clear_value_without_validators_tests(self) -> ObservableValue[int]:
        # Arrange
        obsv = ObservableValue[int](seed=-1)
        obsv.subscribe(print)

        # Act
        obsv.set_value(2)
        obsv.clear_value()

        # Assert
        obsv.get_value(
            lambda cv: assertion(
                cv == -1,
                f"{cv} == -1",
            )
        )
        obsv.get_error(
            lambda ce: assertion(
                ce is None,
                f"{ce} is None",
            )
        )
        assert len(obsv.get_subscribers()) == 0

        # Return obsv for any additional processing.
        return obsv

    # =================================

    def test_clear_value_without_validators_in_sync_context(self) -> None:
        self.clear_value_without_validators_tests()

    # =================================

    async def test_clear_value_without_validators_in_async_context(self) -> None:
        await self.clear_value_without_validators_tests().wait_for_tasks()

    # =================================

    def clear_value_with_validators_tests(self) -> ObservableValue[int]:
        # Arrange
        obsv = ObservableValue[int](seed=-1, validators=[Validators.choices([0, 1])])
        obsv.subscribe(next_callback=lambda value: None)

        # Act
        obsv.set_value(2)
        obsv.clear_value()

        # Assert
        obsv.get_value(
            lambda cv: assertion(
                cv == -1,
                f"{cv} == -1",
            )
        )
        obsv.get_error(
            lambda ce: assertion(
                ce is None,
                f"{ce} is None",
            )
        )
        assert len(obsv.get_subscribers()) == 0

        # Return obsv for any additional processing.
        return obsv

    # =================================

    def test_clear_value_with_validators_in_sync_context(self) -> None:
        self.clear_value_with_validators_tests()

    # =================================

    async def test_clear_value_with_validators_in_async_context(self) -> None:
        await self.clear_value_with_validators_tests().wait_for_tasks()

    # =================================
    # Test Cases for clear value order
    # =================================

    def clear_value_order_tests(self) -> ObservableValue[float]:
        # Arrange
        obsv = ObservableValue[float](
            seed=0.0,
            validators=[
                Validators.required,
                Validators.delay,
            ],
        )
        obsv.subscribe(print)

        # Act
        obsv.set_value(0.0025)
        obsv.set_value(0.0015)
        obsv.set_value(None)  # type: ignore[arg-type]
        obsv.set_value(0.0005)
        obsv.clear_value()
        obsv.subscribe(print)
        obsv.subscribe(print)

        # Assert
        obsv.get_value(
            lambda cv: assertion(
                cv == 0.0,
                f"{cv} == 0.0",
            )
        )
        obsv.get_error(
            lambda ce: assertion(
                ce is None,
                f"{ce} is None",
            )
        )
        assert len(obsv.get_subscribers()) == 2

        # Return obsv for any additional processing.
        return obsv

    # =================================

    def test_clear_value_order_in_sync_context(self) -> None:
        self.clear_value_order_tests()

    # =================================

    async def test_clear_value_order_in_async_context(self) -> None:
        await self.clear_value_order_tests().wait_for_tasks()

    # =================================
    # Test Cases for prime subscriber
    # =================================

    @contextmanager
    def prime_subscriber_tests(self) -> Generator[ObservableValue[float], None, None]:
        # Arrange
        next_callback = CallableMock.Async()
        error_callback = CallableMock.Sync()
        complete_callback = CallableMock.Async()
        obsv = ObservableValue[float](
            seed=0.0,
            validators=[
                Validators.required,
                Validators.delay,
            ],
        )

        # Act
        sub1 = obsv.prime_subscribers(
            obsv.subscribe(
                next_callback=next_callback,
                error_callback=error_callback,
                complete_callback=complete_callback,
            )
        )
        obsv.set_value(0.0035)
        obsv.set_value(0.0025)
        obsv.set_value(None)  # type: ignore[arg-type]
        obsv.prime_subscribers(
            obsv.subscribe(
                next_callback=next_callback,
                error_callback=error_callback,
                complete_callback=complete_callback,
            )
        )
        obsv.set_value(0.0015)
        obsv.clear_value()
        obsv.set_value(0.0005)
        obsv.subscribe(
            next_callback=next_callback,
            error_callback=error_callback,
            complete_callback=complete_callback,
        )
        sub2, sub3 = obsv.prime_subscribers(
            obsv.subscribe(
                next_callback=next_callback,
                error_callback=error_callback,
                complete_callback=complete_callback,
            ),
            obsv.subscribe(
                next_callback=next_callback,
                error_callback=error_callback,
                complete_callback=complete_callback,
            ),
        )
        sub3.unsubscribe()
        sub2.unsubscribe()
        sub1 = obsv.prime_subscribers(sub1)

        with pytest.raises(PyventusException):
            obsv.prime_subscribers()

        # Yield control for any additional processing.
        yield obsv

        # Assert
        assert next_callback.call_count == 8
        assert next_callback.last_args == (0.0005,)
        assert next_callback.last_kwargs == {}
        assert error_callback.call_count == 2
        assert isinstance(error_callback.last_args[0], AttributeError)
        assert error_callback.last_kwargs == {}
        assert complete_callback.call_count == 2
        assert complete_callback.last_args == ()
        assert complete_callback.last_kwargs == {}
        assert isinstance(sub1, Subscriber)
        assert isinstance(sub2, Subscriber)
        assert isinstance(sub3, Subscriber)

    # =================================

    def test_prime_subscriber_in_sync_context(self) -> None:
        with self.prime_subscriber_tests():
            pass

    # =================================

    async def test_prime_subscriber_in_async_context(self) -> None:
        with self.prime_subscriber_tests() as obsv:
            await obsv.wait_for_tasks()

    # =================================
    # Test Cases for notifications
    # =================================

    @contextmanager
    def notification_tests(self) -> Generator[ObservableValue[float], None, None]:
        # Arrange
        value1: Any = object()
        value2: Any = object()
        value3: Any = object()
        next_callback = CallableMock.Async()
        error_callback = CallableMock.Sync()
        complete_callback = CallableMock.Async()
        obsv = ObservableValue[Any](
            seed=None,
            validators=[
                Validators.required,
                Validators.choices([value1, value2]),
            ],
        )

        # Act
        obsv.subscribe(
            next_callback=next_callback,
            error_callback=error_callback,
            complete_callback=complete_callback,
        )
        obsv.set_value(value1)
        obsv.subscribe(
            next_callback=next_callback,
            error_callback=error_callback,
            complete_callback=complete_callback,
        )
        obsv.set_value(value3)
        obsv.set_value(None)
        obsv.set_value(value2)
        obsv.clear_value()
        obsv.set_value(value1)
        obsv.clear_value()

        # Yield control for any additional processing.
        yield obsv

        # Assert
        assert next_callback.call_count == 3
        assert next_callback.last_args == (value2,)
        assert next_callback.last_kwargs == {}
        assert error_callback.call_count == 4
        assert isinstance(error_callback.last_args[0], AttributeError)
        assert error_callback.last_kwargs == {}
        assert complete_callback.call_count == 2
        assert complete_callback.last_args == ()
        assert complete_callback.last_kwargs == {}

    # =================================

    def test_notification_in_sync_context(self) -> None:
        with self.notification_tests():
            pass

    # =================================

    async def test_notification_in_async_context(self) -> None:
        with self.notification_tests() as obsv:
            await obsv.wait_for_tasks()

    # =================================
    # Test Cases for notifications order
    # =================================

    @contextmanager
    def notification_order_tests(self) -> Generator[ObservableValue[float], None, None]:
        # Arrange
        next_callback = CallableMock.Async()
        error_callback = CallableMock.Sync()
        complete_callback = CallableMock.Async()
        obsv = ObservableValue[float](
            seed=0.0,
            validators=[
                Validators.required,
                Validators.delay,
            ],
        )

        # Act
        obsv.subscribe(
            next_callback=next_callback,
            error_callback=error_callback,
            complete_callback=complete_callback,
        )
        obsv.set_value(0.0035)
        obsv.set_value(0.0025)
        obsv.set_value(None)  # type: ignore[arg-type]
        obsv.subscribe(
            next_callback=next_callback,
            error_callback=error_callback,
            complete_callback=complete_callback,
        )
        obsv.set_value(0.0015)
        sub = obsv.subscribe(
            next_callback=next_callback,
            error_callback=error_callback,
            complete_callback=complete_callback,
        )
        obsv.set_value(0.0005)
        sub.unsubscribe()
        obsv.set_value(0.0001)
        obsv.clear_value()
        obsv.subscribe(
            next_callback=next_callback,
            error_callback=error_callback,
            complete_callback=complete_callback,
        )
        obsv.set_value(0.001)
        obsv.clear_value()

        # Assert
        obsv.get_value(
            lambda cv: assertion(
                cv == 0.0,
                f"{cv} == 0.0",
            )
        )
        obsv.get_error(
            lambda ce: assertion(
                ce is None,
                f"{ce} is None",
            )
        )

        # Yield control for any additional processing.
        yield obsv

        assert next_callback.call_count == 10
        assert next_callback.last_args == (0.001,)
        assert next_callback.last_kwargs == {}
        assert error_callback.call_count == 1
        assert isinstance(error_callback.last_args[0], AttributeError)
        assert error_callback.last_kwargs == {}
        assert complete_callback.call_count == 3
        assert complete_callback.last_args == ()
        assert complete_callback.last_kwargs == {}

    # =================================

    def test_notification_order_in_sync_context(self) -> None:
        with self.notification_order_tests():
            pass

    # =================================

    async def test_notification_order_in_async_context(self) -> None:
        with self.notification_order_tests() as obsv:
            await obsv.wait_for_tasks()
