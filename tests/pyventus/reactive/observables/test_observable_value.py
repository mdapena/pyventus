import asyncio
from collections.abc import Callable, Generator
from contextlib import contextmanager
from typing import Any

import pytest
from pyventus import PyventusException
from pyventus.reactive import ObservableValue, ObservableValueValidatorType
from pyventus.reactive.subscribers.subscriber import Subscriber

from ....fixtures import CallableMock, DummyCallable
from ....utils import get_private_attr


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
        obsv_validators = get_private_attr(obsv, "__validators")

        # Assert
        assert obsv is not None
        assert isinstance(obsv, ObservableValue)
        assert get_private_attr(obsv, "__seed") is seed
        assert get_private_attr(obsv, "__value") is seed
        assert get_private_attr(obsv, "__exception") is None
        assert obsv_validators is None if not validators else len(obsv_validators) == len(validators)

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

    def test_value_retrieval(self) -> None:
        # Arrange
        seed: Any = object()
        value: Any = object()
        assert seed is not value

        # Act/Assert
        obsv = ObservableValue[Any](seed=seed)
        assert obsv.value is obsv.get_value() is seed

        # Act/Assert
        obsv.value = value
        assert obsv.value is obsv.get_value() is value

    # =================================
    # Test Cases for value update
    # =================================

    def test_value_update(self) -> None:
        # Arrange
        value1: Any = object()
        value2: Any = object()

        # Act/Assert: Initial
        obsv = ObservableValue[Any](seed=object())
        assert obsv.value is not value1 and obsv.value is not value2

        # Act/Assert: Setter
        obsv.value = value1
        assert obsv.value is value1 and obsv.value is not value2

        # Act/Assert: Method
        obsv.set_value(value2)
        assert obsv.value is not value1 and obsv.value is value2

    # =================================

    def test_validators_execution_on_value_update(self) -> None:
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

        # Act/Assert: Setter
        obsv.value = value1
        assert validator1.call_count == validator2.call_count == 1
        assert validator1.last_args == validator2.last_args == (value1,)
        assert validator1.last_kwargs == validator2.last_kwargs == {}

        # Act/Assert: Method
        obsv.set_value(value2)
        assert validator1.call_count == validator2.call_count == 2
        assert validator1.last_args == validator2.last_args == (value2,)
        assert validator1.last_kwargs == validator2.last_kwargs == {}

        # Act/Assert: Clear
        obsv.clear_value()
        assert validator1.call_count == validator2.call_count == 2
        assert validator1.last_args == validator2.last_args == (value2,)
        assert validator1.last_kwargs == validator2.last_kwargs == {}

    # =================================

    def test_value_update_with_validators(self) -> None:
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

        # Act/Assert: Initial
        assert obsv.value is None
        assert obsv.error is None

        # Act/Assert: Valid|Setter
        obsv.value = value1
        assert obsv.value is value1 and obsv.value not in [value2, value3, value4]
        assert obsv.error is None

        # Act/Assert: Valid|Method
        obsv.set_value(value2)
        assert obsv.value is value2 and obsv.value not in [value1, value3, value4]
        assert obsv.error is None

        # Act/Assert: Invalid|Last-Validator
        obsv.value = value4
        assert obsv.value is value4 and obsv.value not in [value1, value2, value3]
        assert isinstance(obsv.error, ValueError)

        # Act/Assert: Invalid|First-Validator
        obsv.set_value(None)  # type: ignore[unreachable]
        assert obsv.value is None
        assert isinstance(obsv.error, AttributeError)

        # Act/Assert: Valid|Error-Reset
        obsv.value = value3
        assert obsv.value is value3 and obsv.value not in [value1, value2, value4]
        assert obsv.error is None

    # =================================
    # Test Cases for value update order
    # =================================

    @contextmanager
    def value_update_order_tests(self) -> Generator[ObservableValue[float], None, None]:
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
        obsv.value = 0.0025
        obsv.set_value(0.0015)
        obsv.value = 0.0005
        yield obsv

        # Assert
        assert obsv.value == 0.0005
        assert obsv.error is None

    # =================================

    def test_value_update_order_in_sync_context(self) -> None:
        # Arrange/Act/Assert
        with self.value_update_order_tests():
            pass

    # =================================

    async def test_value_update_order_in_async_context(self) -> None:
        # Arrange/Act/Assert
        with self.value_update_order_tests() as obsv:
            await obsv.wait_for_tasks()

    # =================================
    # Test Cases for clear value
    # =================================

    def test_clear_value_without_validators(self) -> None:
        # Arrange
        obsv = ObservableValue[int](seed=-1)
        obsv.subscribe(next_callback=lambda value: None)

        # Act
        obsv.value = 2
        obsv.clear_value()

        # Assert
        assert obsv.value == -1
        assert obsv.error is None
        assert len(obsv.get_subscribers()) == 0

    # =================================

    def test_clear_value_with_validators(self) -> None:
        # Arrange
        obsv = ObservableValue[int](seed=-1, validators=[Validators.choices([0, 1])])
        obsv.subscribe(next_callback=lambda value: None)

        # Act
        obsv.value = 2
        obsv.clear_value()

        # Assert
        assert obsv.value == -1
        assert obsv.error is None
        assert len(obsv.get_subscribers()) == 0

    # =================================
    # Test Cases for clear value order
    # =================================

    @contextmanager
    def clear_value_order_tests(self) -> Generator[ObservableValue[float], None, None]:
        # Arrange
        obsv = ObservableValue[float](
            seed=0.0,
            validators=[
                Validators.required,
                Validators.delay,
            ],
        )
        obsv.subscribe(next_callback=print)

        # Act
        obsv.value = 0.0025
        obsv.set_value(0.0015)
        obsv.value = None  # type: ignore[assignment]
        obsv.set_value(0.0005)
        obsv.clear_value()
        yield obsv

        # Assert
        assert obsv.value == 0.0
        assert obsv.error is None
        assert len(obsv.get_subscribers()) == 0

    # =================================

    def test_clear_value_order_in_sync_context(self) -> None:
        # Arrange/Act/Assert
        with self.clear_value_order_tests():
            pass

    # =================================

    async def test_clear_value_order_in_async_context(self) -> None:
        # Arrange/Act/Assert
        with self.clear_value_order_tests() as obsv:
            await obsv.wait_for_tasks()

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
        sub = obsv.prime_subscribers(
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
        subs = obsv.prime_subscribers(
            [
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
            ]
        )
        for s in subs:
            s.unsubscribe()
        sub = obsv.prime_subscribers(sub)

        yield obsv  # Yield control for any additional processing.

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
        assert isinstance(sub, Subscriber)
        assert isinstance(subs, list)

    # =================================

    def test_prime_subscriber_in_sync_context(self) -> None:
        # Arrange/Act/Assert
        with self.prime_subscriber_tests():
            pass

    # =================================

    async def test_prime_subscriber_in_async_context(self) -> None:
        # Arrange/Act/Assert
        with self.prime_subscriber_tests() as obsv:
            await obsv.wait_for_tasks()

    # =================================
    # Test Cases for notifications
    # =================================

    def test_notifications(self) -> None:
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
        obsv.value = value1

        obsv.subscribe(
            next_callback=next_callback,
            error_callback=error_callback,
            complete_callback=complete_callback,
        )
        obsv.set_value(value3)
        obsv.value = None
        obsv.set_value(value2)
        obsv.clear_value()

        obsv.value = value1
        obsv.clear_value()

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
        obsv.value = 0.0025
        obsv.value = None  # type: ignore[assignment]
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
        obsv.value = 0.0005
        sub.unsubscribe()
        obsv.value = 0.0001
        obsv.clear_value()
        obsv.subscribe(
            next_callback=next_callback,
            error_callback=error_callback,
            complete_callback=complete_callback,
        )
        obsv.value = 0.001
        obsv.clear_value()

        yield obsv  # Yield control for any additional processing.

        # Assert
        assert obsv.value == 0.0
        assert obsv.error is None
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
        # Arrange/Act/Assert
        with self.notification_order_tests():
            pass

    # =================================

    async def test_notification_order_in_async_context(self) -> None:
        # Arrange/Act/Assert
        with self.notification_order_tests() as obsv:
            await obsv.wait_for_tasks()
