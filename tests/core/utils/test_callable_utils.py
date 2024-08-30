from collections.abc import Callable
from threading import current_thread, main_thread
from typing import Any

import pytest
from pyventus import PyventusException
from pyventus.core.utils import (
    get_callable_name,
    is_callable_async,
    is_callable_generator,
    validate_callable,
)
from pyventus.core.utils.callable_utils import CallableWrapper

from ...fixtures import CallableMock, DummyCallable


class TestCallableUtils:
    # =================================
    # Test Cases for validate_callable
    # =================================

    @pytest.mark.parametrize(
        "cb",
        [  # Valid callables
            *DummyCallable.Sync().ALL,
            *DummyCallable.Sync.Generator().ALL,
            *DummyCallable.Async().ALL,
            *DummyCallable.Async.Generator().ALL,
        ],
    )
    def test_validate_callable_with_valid_input(self, cb: Callable[..., Any]) -> None:
        # Arrange, Act, and Assert
        validate_callable(cb)

    # =================================

    @pytest.mark.parametrize(
        ["cb", "exception"],
        [  # Invalid callables
            (None, PyventusException),
            (True, PyventusException),
            (DummyCallable.Invalid(), PyventusException),
        ],
    )
    def test_validate_callable_with_invalid_input(self, cb: Any, exception: type[Exception]) -> None:
        # Arrange, Act, and Assert
        with pytest.raises(exception):
            validate_callable(cb)

    # =================================
    # Test Cases for get_callable_name
    # =================================

    @pytest.mark.parametrize(
        ["cb", "expected"],
        [
            (None, "None"),
            (True, "Unknown"),
            (DummyCallable.Invalid, "Unknown"),
            (DummyCallable.Invalid(), "Unknown"),
            *[(c, n) for c, n in zip(DummyCallable.Sync().ALL, DummyCallable.Sync().ALL_NAMES)],
            *[(c, n) for c, n in zip(DummyCallable.Sync.Generator().ALL, DummyCallable.Sync.Generator().ALL_NAMES)],
        ],
    )
    def test_get_callable_name(self, cb: Callable[..., Any], expected: str) -> None:
        # Arrange, Act, and Assert
        assert get_callable_name(cb) == expected

    # =================================
    # Test Cases for is_callable_async
    # =================================

    @pytest.mark.parametrize(
        ["cb", "expected"],
        [
            (None, False),
            (True, False),
            (DummyCallable.Invalid, False),
            (DummyCallable.Invalid(), False),
            *[(c, False) for c in DummyCallable.Sync().ALL],
            *[(c, False) for c in DummyCallable.Sync.Generator().ALL],
            *[(c, True) for c in DummyCallable.Async().ALL],
            *[(c, True) for c in DummyCallable.Async.Generator().ALL],
        ],
    )
    def test_is_callable_async(self, cb: Callable[..., Any], expected: bool) -> None:
        # Arrange, Act, and Assert
        assert is_callable_async(cb) is expected

    # =================================
    # Test Cases for is_callable_generator
    # =================================

    @pytest.mark.parametrize(
        ["cb", "expected"],
        [
            (None, False),
            (True, False),
            (DummyCallable.Invalid, False),
            (DummyCallable.Invalid(), False),
            *[(cb, False) for cb in DummyCallable.Sync().ALL],
            *[(cb, True) for cb in DummyCallable.Sync.Generator().ALL],
            *[(cb, False) for cb in DummyCallable.Async().ALL],
            *[(cb, True) for cb in DummyCallable.Async.Generator().ALL],
        ],
    )
    def test_is_callable_generator(self, cb: Callable[..., Any], expected: bool) -> None:
        # Arrange, Act, and Assert
        assert is_callable_generator(cb) is expected

    # =================================
    # Test Cases for CallableWrapper
    # =================================

    def test_callable_wrapper_creation_with_valid_input(self) -> None:
        # Arrange/Act: Create an instance of CallableWrapper
        callable_wrapper: CallableWrapper[..., Any] = CallableWrapper[..., Any](
            DummyCallable.Async.func, force_async=True
        )

        # Assert: Check that the callable_wrapper is created
        # successfully and has the expected properties
        assert callable_wrapper
        assert callable_wrapper.force_async is True
        assert callable_wrapper.name == get_callable_name(DummyCallable.Async.func)

    # =================================

    def test_callable_wrapper_creation_with_invalid_input(self) -> None:
        # Arrange: Prepare invalid inputs for CallableWrapper
        invalid_generator_callable = DummyCallable.Async.Generator.func
        invalid_force_async_value = None

        # Act & Assert: Verify that creating CallableWrapper with
        # invalid inputs raises the expected exceptions
        with pytest.raises(PyventusException):
            CallableWrapper[..., Any](invalid_generator_callable, force_async=True)

        with pytest.raises(PyventusException):
            CallableWrapper[..., Any](
                DummyCallable.Async.func,
                force_async=invalid_force_async_value,  # type: ignore[arg-type]
            )

    # =================================

    @pytest.mark.parametrize(
        ["cb", "force_async", "args", "kwargs"],
        [
            *[  # Synchronous call scenarios
                (CallableMock.Sync(return_value=None, raise_exception=None), True, (), {}),
                (CallableMock.Sync(return_value=None, raise_exception=None), False, (), {}),
                (CallableMock.Sync(return_value=None, raise_exception=ValueError("str")), False, (), {}),
                (CallableMock.Sync(return_value="str", raise_exception=None), False, ("str", 0), {"str": ...}),
            ],
            *[  # Asynchronous call scenarios
                (CallableMock.Async(return_value=None, raise_exception=None), True, (), {}),
                (CallableMock.Async(return_value=None, raise_exception=None), False, (), {}),
                (CallableMock.Async(return_value=None, raise_exception=ValueError("str")), False, (), {}),
                (CallableMock.Async(return_value="str", raise_exception=None), False, ("str", 0), {"str": ...}),
            ],
        ],
    )
    @pytest.mark.asyncio
    async def test_callable_wrapper_execution(
        self, cb: CallableMock.Base, force_async: bool, args: tuple[Any, ...], kwargs: dict[str, Any]
    ) -> None:
        # Arrange: Create an instance of CallableWrapper with the provided callable mock
        callable_wrapper: CallableWrapper[..., Any] = CallableWrapper[..., Any](cb, force_async=force_async)

        try:
            # Act: Attempt to call the wrapper with the specified arguments
            return_value = await callable_wrapper(*args, **kwargs)
        except Exception as e:
            # Assert: Check if the raised exception matches the expected exception
            assert cb.exception is e
        else:
            # Assert: Verify the return value matches the expected return value
            assert cb.return_value is return_value  # Asserts

        # Final assertions: Verify the call count and arguments used
        assert cb.call_count == 1
        assert cb.last_args == args
        assert cb.last_kwargs == kwargs

    # =================================

    @pytest.mark.asyncio
    async def test_callable_wrapper_sync_callable_force_async_disabled(self) -> None:
        # Arrange: Define the assertion function
        def assertion() -> None:
            # Assert that the current thread is the
            # main thread when force_async is False.
            assert current_thread() is main_thread()

        # Create a CallableWrapper instance with force_async set to False
        callable_wrapper: CallableWrapper[..., Any] = CallableWrapper[..., Any](assertion, force_async=False)

        # Act and Arrange
        await callable_wrapper()  # This should run in the main thread

    # =================================

    @pytest.mark.asyncio
    async def test_callable_wrapper_sync_callable_force_async_enabled(self) -> None:
        # Arrange: Define the assertion function
        def assertion() -> None:
            # Assert that the current thread is not the
            # main thread due to force_async being enabled.
            assert current_thread() is not main_thread()

        # Create a CallableWrapper instance with force_async set to True
        callable_wrapper: CallableWrapper[..., Any] = CallableWrapper[..., Any](assertion, force_async=True)

        # Act: Execute the callable wrapper
        await callable_wrapper()  # This should run in a different thread

    # =================================

    @pytest.mark.asyncio
    async def test_callable_wrapper_async_callable_with_force_async_flag(self) -> None:
        # Arrange: Define the assertion function
        async def assertion() -> None:
            # Assert that the current thread is the main thread in an async context.
            assert current_thread() is main_thread()

        # Create CallableWrapper instances for the async callable
        callable_wrapper1: CallableWrapper[..., Any] = CallableWrapper[..., Any](assertion, force_async=False)
        callable_wrapper2: CallableWrapper[..., Any] = CallableWrapper[..., Any](assertion, force_async=True)

        # Act: Execute the callable wrappers
        await callable_wrapper1()  # This should run in the main thread
        await callable_wrapper2()  # This should also run in the main thread
