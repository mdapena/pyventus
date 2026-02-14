import asyncio
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from pyventus.reactive import ObservableStream

from ....fixtures import CallableMock


class TestObservableStream:
    # =================================
    # Test Cases for creation
    # =================================

    def test_creation(self) -> None:
        # Arrange/Act
        obss = ObservableStream[Any]()

        # Assert
        assert obss is not None
        assert isinstance(obss, ObservableStream)

    # =================================
    # Test Cases for value entry
    # =================================

    @contextmanager
    def run_value_entry_tests(self) -> Generator[ObservableStream[Any], None, None]:
        # Arrange
        value1: Any = object()
        value2: Any = object()
        callback1: CallableMock.Base = CallableMock.Sync()
        callback2: CallableMock.Base = CallableMock.Async()
        obss = ObservableStream[Any]()
        sub1 = obss.subscribe(
            next_callback=callback1,
            error_callback=callback1,
            complete_callback=callback1,
        )
        sub2 = obss.subscribe(
            next_callback=callback2,
            error_callback=callback2,
            complete_callback=callback2,
        )

        # Act
        obss.next(value1)
        obss.next(value2)
        sub1.unsubscribe()
        obss.next(value1)
        sub2.unsubscribe()
        obss.next(value2)

        # Yield control for any additional processing.
        yield obss

        # Assert
        assert callback1.call_count == 2
        assert callback1.last_args == (value2,)
        assert callback1.last_kwargs == {}
        assert callback2.call_count == 3
        assert callback2.last_args == (value1,)
        assert callback2.last_kwargs == {}

    # =================================

    def test_value_entry_in_sync_context(self) -> None:
        with self.run_value_entry_tests():
            pass

    # =================================

    async def test_value_entry_in_async_context(self) -> None:
        with self.run_value_entry_tests() as obss:
            await obss.wait_for_tasks()

    # =================================
    # Test Cases for error entry
    # =================================

    @contextmanager
    def run_error_entry_tests(self) -> Generator[ObservableStream[Any], None, None]:
        # Arrange
        error1: Exception = Exception("Exception message")
        error2: Exception = Exception("Exception message")
        callback1: CallableMock.Base = CallableMock.Sync()
        callback2: CallableMock.Base = CallableMock.Async()
        obss = ObservableStream[Any]()
        sub1 = obss.subscribe(
            next_callback=callback1,
            error_callback=callback1,
            complete_callback=callback1,
        )
        sub2 = obss.subscribe(
            next_callback=callback2,
            error_callback=callback2,
            complete_callback=callback2,
        )

        # Act
        obss.error(error1)
        obss.error(error2)
        sub1.unsubscribe()
        obss.error(error1)
        sub2.unsubscribe()
        obss.error(error2)

        # Yield control for any additional processing.
        yield obss

        # Assert
        assert callback1.call_count == 2
        assert callback1.last_args == (error2,)
        assert callback1.last_kwargs == {}
        assert callback2.call_count == 3
        assert callback2.last_args == (error1,)
        assert callback2.last_kwargs == {}

    # =================================

    def test_error_entry_in_sync_context(self) -> None:
        with self.run_error_entry_tests():
            pass

    # =================================

    async def test_error_entry_in_async_context(self) -> None:
        with self.run_error_entry_tests() as obss:
            await obss.wait_for_tasks()

    # =================================
    # Test Cases for completion entry
    # =================================

    @contextmanager
    def run_completion_entry_tests(self) -> Generator[ObservableStream[Any], None, None]:
        # Arrange
        callback1: CallableMock.Base = CallableMock.Sync()
        callback2: CallableMock.Base = CallableMock.Async()
        obss = ObservableStream[Any]()
        sub1 = obss.subscribe(
            next_callback=callback1,
            error_callback=callback1,
            complete_callback=callback1,
        )
        sub2 = obss.subscribe(
            next_callback=callback2,
            error_callback=callback2,
            complete_callback=callback2,
        )

        # Act
        obss.complete()
        obss.complete()

        # Yield control for any additional processing.
        yield obss

        # Assert
        assert callback1.call_count == 1
        assert callback1.last_args == ()
        assert callback1.last_kwargs == {}
        assert callback2.call_count == 1
        assert callback2.last_args == ()
        assert callback2.last_kwargs == {}
        assert sub1.unsubscribe() is False
        assert sub2.unsubscribe() is False

    # =================================

    def test_completion_entry_in_sync_context(self) -> None:
        with self.run_completion_entry_tests():
            pass

    # =================================

    async def test_completion_entry_in_async_context(self) -> None:
        with self.run_completion_entry_tests() as obss:
            await obss.wait_for_tasks()

    # =================================
    # Test Cases for notifications order
    # =================================

    @contextmanager
    def run_notification_order_tests(self) -> Generator[ObservableStream[float], None, None]:
        # Arrange
        error1 = Exception("Error 1")
        error2 = Exception("Error 2")

        callback1 = CallableMock.Sync()
        callback2 = CallableMock.Async()
        callback3 = CallableMock.Sync()

        obss = ObservableStream[float]()

        async def next_callback(delay: float) -> None:
            await asyncio.sleep(delay)
            callback1(delay)

        async def error_callback(err: Exception) -> None:
            await asyncio.sleep(0.0025)
            await callback2(err)

        async def complete_callback() -> None:
            await asyncio.sleep(0.0015)
            callback3()

        # Act
        sub1 = obss.subscribe(
            next_callback=next_callback,
            error_callback=error_callback,
            complete_callback=complete_callback,
        )
        obss.next(0.0035)
        obss.next(0.0025)
        sub2 = obss.subscribe(
            next_callback=next_callback,
            error_callback=error_callback,
            complete_callback=complete_callback,
        )
        obss.next(0.0015)
        obss.error(error1)
        sub1.unsubscribe()
        obss.next(0.0005)
        obss.complete()
        obss.next(0.0001)
        obss.error(error2)
        obss.complete()

        # Yield control for any additional processing.
        yield obss

        # Assert
        assert callback1.call_count == 5
        assert callback1.last_args == (0.0005,)
        assert callback1.last_kwargs == {}
        assert callback2.call_count == 2
        assert callback2.last_args == (error1,)
        assert callback2.last_kwargs == {}
        assert callback3.call_count == 1
        assert callback3.last_args == ()
        assert callback3.last_kwargs == {}
        assert sub1.unsubscribe() is False
        assert sub2.unsubscribe() is False

    # =================================

    def test_notification_order_in_sync_context(self) -> None:
        with self.run_notification_order_tests():
            pass

    # =================================

    async def test_notification_order_in_async_context(self) -> None:
        with self.run_notification_order_tests() as obss:
            await obss.wait_for_tasks()
