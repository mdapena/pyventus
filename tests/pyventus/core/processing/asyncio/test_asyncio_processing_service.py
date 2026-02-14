import asyncio
import time
from collections import deque
from collections.abc import Awaitable, Callable, Generator
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from threading import Lock, current_thread, main_thread
from typing import Any

import pytest
from pyventus.core.exceptions.pyventus_exception import PyventusException
from pyventus.core.processing.asyncio import AsyncIOProcessingService
from typing_extensions import override

from .....fixtures import CallableMock, DummyCallable
from ..processing_service_test import ProcessingServiceTest


class TestAsyncIOProcessingService(ProcessingServiceTest):
    # =================================
    # Test Cases for is_loop_running
    # =================================

    def test_is_loop_running_in_sync_context(self) -> None:
        # Arrange/Act/Assert
        loop_running: bool = AsyncIOProcessingService.is_loop_running()
        assert not loop_running

    # =================================

    async def test_is_loop_running_in_async_context(self) -> None:
        # Arrange/Act/Assert
        loop_running: bool = AsyncIOProcessingService.is_loop_running()
        assert loop_running

    # =================================
    # Test Cases for creation
    # =================================

    @pytest.mark.parametrize(
        ["force_async", "enforce_submission_order"],
        [
            (None, None),
            (False, False),
            (True, False),
            (False, True),
            (True, True),
        ],
    )
    def test_creation_with_valid_input(self, force_async: bool | None, enforce_submission_order: bool | None) -> None:
        # Arrange/Act
        kwargs: dict[str, Any] = {}
        if force_async is not None:
            kwargs["force_async"] = force_async
        if enforce_submission_order is not None:
            kwargs["enforce_submission_order"] = enforce_submission_order
        processing_service = AsyncIOProcessingService(**kwargs)

        # Assert
        assert processing_service is not None
        assert isinstance(processing_service, AsyncIOProcessingService)
        assert processing_service._thread_lock is not None
        assert isinstance(processing_service._tasks, set)
        assert len(processing_service._tasks) == 0

        if not force_async:
            assert processing_service.force_async is False
        else:
            assert processing_service.force_async is True

        if not enforce_submission_order:
            assert processing_service._submission_queue is None
            assert processing_service._is_submission_queue_busy is False
            assert processing_service.enforce_submission_order is False
        else:
            assert isinstance(processing_service._submission_queue, deque)
            assert len(processing_service._submission_queue) == 0
            assert processing_service._is_submission_queue_busy is False
            assert processing_service.enforce_submission_order is True

    # =================================

    @pytest.mark.parametrize(
        ["force_async", "enforce_submission_order", "exception"],
        [
            (None, False, PyventusException),
            (False, None, PyventusException),
            ("True", True, PyventusException),
            (True, "True", PyventusException),
        ],
    )
    def test_creation_with_invalid_input(
        self, force_async: Any, enforce_submission_order: Any, exception: type[Exception]
    ) -> None:
        # Arrange/Act/Assert
        with pytest.raises(exception):
            AsyncIOProcessingService(force_async=force_async, enforce_submission_order=enforce_submission_order)

    # =================================
    # Test Cases for submission
    # =================================

    @override
    def run_submission_test_case_in_sync_ctx(self, test_case: ProcessingServiceTest.SubmissionTestCase) -> None:
        processing_service: AsyncIOProcessingService | None = None

        # Arrange/Act/Assert
        processing_service = AsyncIOProcessingService()
        with test_case.execute(processing_service):
            pass

        # Arrange/Act/Assert
        processing_service = AsyncIOProcessingService(force_async=False, enforce_submission_order=False)
        with test_case.execute(processing_service):
            pass

        # Arrange/Act/Assert
        processing_service = AsyncIOProcessingService(force_async=False, enforce_submission_order=True)
        with test_case.execute(processing_service):
            pass

        # Arrange/Act/Assert
        processing_service = AsyncIOProcessingService(force_async=True, enforce_submission_order=False)
        with test_case.execute(processing_service):
            pass

        # Arrange/Act/Assert
        processing_service = AsyncIOProcessingService(force_async=True, enforce_submission_order=True)
        with test_case.execute(processing_service):
            pass

    # =================================

    @override
    async def run_submission_test_case_in_async_ctx(self, test_case: ProcessingServiceTest.SubmissionTestCase) -> None:
        processing_service: AsyncIOProcessingService | None = None

        # Arrange/Act/Assert
        processing_service = AsyncIOProcessingService()
        with test_case.execute(processing_service):
            await processing_service.wait_for_tasks()

        # Arrange/Act/Assert
        processing_service = AsyncIOProcessingService(force_async=False, enforce_submission_order=False)
        with test_case.execute(processing_service):
            await processing_service.wait_for_tasks()

        # Arrange/Act/Assert
        processing_service = AsyncIOProcessingService(force_async=True, enforce_submission_order=False)
        with test_case.execute(processing_service):
            await processing_service.wait_for_tasks()

        # Arrange/Act/Assert
        processing_service = AsyncIOProcessingService(force_async=False, enforce_submission_order=True)
        with test_case.execute(processing_service):
            await processing_service.wait_for_tasks()

        # Arrange/Act/Assert
        processing_service = AsyncIOProcessingService(force_async=True, enforce_submission_order=True)
        with test_case.execute(processing_service):
            await processing_service.wait_for_tasks()

    # =================================
    # Test Cases for force_async
    # =================================

    @pytest.mark.parametrize(
        ["force_async"],
        [
            (True,),
            (False,),
        ],
    )
    def test_submission_sync_with_force_async_flag(self, force_async: bool) -> None:
        # Arrange
        def assertion1() -> None:
            assert current_thread() is main_thread()

        async def assertion2() -> None:
            assert current_thread() is main_thread()

        # Act
        processing_service = AsyncIOProcessingService(force_async=force_async)
        processing_service.submit(assertion1)
        processing_service.submit(assertion2)

        # Act/Assert
        assert processing_service.task_count == 0

    # =================================

    async def test_submission_async_with_sync_callable_and_force_async_disabled(self) -> None:
        # Arrange
        def assertion() -> None:
            assert current_thread() is main_thread()

        # Act
        processing_service = AsyncIOProcessingService(force_async=False)
        processing_service.submit(assertion)

        # Act/Assert
        assert processing_service.task_count == 0

    # =================================

    async def test_submission_async_with_sync_callable_and_force_async_enabled(self) -> None:
        # Arrange
        def assertion() -> None:
            assert current_thread() is not main_thread()

        # Act
        processing_service = AsyncIOProcessingService(force_async=True)
        processing_service.submit(assertion)

        # Act/Assert
        assert processing_service.task_count == 1
        await processing_service.wait_for_tasks()

    # =================================

    @pytest.mark.parametrize(
        ["force_async"],
        [
            (True,),
            (False,),
        ],
    )
    async def test_submission_async_with_async_callable_and_force_async_flag(self, force_async: bool) -> None:
        # Arrange.
        async def assertion() -> None:
            # Assert that the current thread is the main thread in an async context.
            assert current_thread() is main_thread()

        # Act
        processing_service = AsyncIOProcessingService(force_async=force_async)
        processing_service.submit(assertion)

        # Assert
        assert processing_service.task_count == 1
        await processing_service.wait_for_tasks()

    # =================================
    # Test Cases for submission order
    # =================================

    @contextmanager
    def run_submission_order_tests(
        self, force_async: bool | None, enforce_submission_order: bool | None
    ) -> Generator[AsyncIOProcessingService, None, None]:
        # Arrange
        class ExecutionOrderTracker:
            def __init__(self) -> None:
                self._thread_lock: Lock = Lock()
                self._compile_time_ids: list[int] = []
                self._runtime_ids: list[int] = []

            def register_callback(self) -> int:
                with self._thread_lock:
                    callback_id: int = len(self._compile_time_ids)
                    self._compile_time_ids.append(callback_id)
                return callback_id

            def create_single_sync_callback(self, delay: float = 0) -> Callable[[], None]:
                callback_id: int = self.register_callback()

                def _main() -> None:
                    time.sleep(delay)
                    with self._thread_lock:
                        self._runtime_ids.append(callback_id)

                return _main

            def create_composed_sync_callback(
                self, service: AsyncIOProcessingService, delay: float = 0
            ) -> Callable[[], None]:
                callback_id1: int = self.register_callback()
                callback_id2: int = self.register_callback()
                callback_id3: int = self.register_callback()

                def _sync_callback() -> None:
                    time.sleep(delay)
                    with self._thread_lock:
                        self._runtime_ids.append(callback_id3)

                async def _async_callback() -> None:
                    await asyncio.sleep(delay)
                    with self._thread_lock:
                        self._runtime_ids.append(callback_id2)
                    service.submit(_sync_callback)

                def _main() -> None:
                    time.sleep(delay)
                    with self._thread_lock:
                        self._runtime_ids.append(callback_id1)
                    service.submit(_async_callback)

                return _main

            def create_single_async_callback(self, delay: float = 0) -> Callable[[], Awaitable[None]]:
                callback_id: int = self.register_callback()

                async def _amain() -> None:
                    await asyncio.sleep(delay)
                    with self._thread_lock:
                        self._runtime_ids.append(callback_id)

                return _amain

            def create_composed_async_callback(
                self, service: AsyncIOProcessingService, delay: float = 0
            ) -> Callable[[], Awaitable[None]]:
                callback_id1: int = self.register_callback()
                callback_id2: int = self.register_callback()
                callback_id3: int = self.register_callback()

                async def _async_callback() -> None:
                    await asyncio.sleep(delay)
                    with self._thread_lock:
                        self._runtime_ids.append(callback_id3)

                def _sync_callback() -> None:
                    time.sleep(delay)
                    with self._thread_lock:
                        self._runtime_ids.append(callback_id2)
                    service.submit(_async_callback)

                async def _amain() -> None:
                    await asyncio.sleep(delay)
                    with self._thread_lock:
                        self._runtime_ids.append(callback_id1)
                    service.submit(_sync_callback)

                return _amain

        kwargs: dict[str, Any] = {}
        if force_async is not None:
            kwargs["force_async"] = force_async
        if enforce_submission_order is not None:
            kwargs["enforce_submission_order"] = enforce_submission_order
        processing_service = AsyncIOProcessingService(**kwargs)

        tracker = ExecutionOrderTracker()
        callbacks: list[Callable[[], None | Awaitable[None]]] = [
            tracker.create_composed_async_callback(delay=0.0035, service=processing_service),
            tracker.create_single_async_callback(delay=0.0035),
            tracker.create_composed_sync_callback(delay=0.0025, service=processing_service),
            tracker.create_single_sync_callback(delay=0.0025),
            tracker.create_composed_async_callback(delay=0.0015, service=processing_service),
            tracker.create_single_async_callback(delay=0.0015),
            tracker.create_composed_sync_callback(delay=0.0005, service=processing_service),
            tracker.create_single_sync_callback(delay=0.0005),
            tracker.create_composed_async_callback(delay=0.0001, service=processing_service),
            tracker.create_single_async_callback(delay=0.0001),
            tracker.create_composed_sync_callback(delay=0, service=processing_service),
            tracker.create_single_sync_callback(delay=0),
        ]

        # Act
        for callback in callbacks:
            processing_service.submit(callback)
        yield processing_service

        # Asserts
        unique_compile_time_ids: set[int] = set(tracker._compile_time_ids)
        unique_runtime_ids: set[int] = set(tracker._runtime_ids)

        # Ensure there are no background tasks pending.
        assert processing_service.task_count == 0, "No background tasks expected."

        # Check that the number of unique IDs.
        assert len(unique_compile_time_ids) == len(unique_runtime_ids), "Unique ID count mismatch."

        # Verify that the sets of IDs are equal.
        assert unique_compile_time_ids == unique_runtime_ids, "Compile-time IDs differ from runtime IDs."

        # Submission order enforcement.
        if enforce_submission_order:
            assert tracker._compile_time_ids == tracker._runtime_ids, "Submission order not guaranteed."

    # =================================

    @pytest.mark.parametrize(
        ["force_async", "enforce_submission_order"],
        [
            (None, None),
            (False, False),
            (True, False),
            (False, True),
            (True, True),
        ],
    )
    def test_submission_order_in_sync_ctx(
        self, force_async: bool | None, enforce_submission_order: bool | None
    ) -> None:
        with self.run_submission_order_tests(force_async, enforce_submission_order):
            pass

    # =================================

    @pytest.mark.parametrize(
        ["force_async", "enforce_submission_order"],
        [
            (None, None),
            (False, False),
            (True, False),
            (False, True),
            (True, True),
        ],
    )
    async def test_submission_order_in_async_ctx(
        self, force_async: bool | None, enforce_submission_order: bool | None
    ) -> None:
        with self.run_submission_order_tests(force_async, enforce_submission_order) as processing_service:
            await processing_service.wait_for_tasks()

    # =================================
    # Test Cases for wait_for_tasks
    # =================================

    async def test_wait_for_tasks(self) -> None:
        # Arrange
        callback: CallableMock.Base = CallableMock.Async()
        processing_service = AsyncIOProcessingService()

        async def main_callback() -> None:
            await asyncio.sleep(0.0025)
            processing_service.submit(callback)

        # Act
        processing_service.submit(main_callback)

        with ThreadPoolExecutor() as executor:

            async def amain() -> None:
                # Arrange
                processing_service.submit(main_callback)

                # Act: Wait for all tasks in the thread's asyncio loop (1 task in thread, 1 in main).
                await processing_service.wait_for_tasks()

                # Assert
                assert callback.call_count == 1
                assert processing_service.task_count == 1

            executor.submit(asyncio.run, amain()).result()

        # Act: Wait for all tasks in the main asyncio loop (0 tasks in thread, 1 in main).
        await processing_service.wait_for_tasks()

        # Assert
        assert callback.call_count == 2
        assert processing_service.task_count == 0

    # =================================
    # Test Cases for all_tasks
    # =================================

    async def test_all_tasks(self) -> None:
        # Arrange
        tasks_lock: Lock = Lock()

        def simulate_task() -> None:
            with tasks_lock:
                time.sleep(0.0005)

        processing_service1: AsyncIOProcessingService = AsyncIOProcessingService(force_async=True)
        processing_service2: AsyncIOProcessingService = AsyncIOProcessingService(force_async=True)
        processing_service3: AsyncIOProcessingService = AsyncIOProcessingService(force_async=True)

        # Act/Assert
        assert processing_service1.task_count == processing_service2.task_count == processing_service3.task_count == 0
        assert len(AsyncIOProcessingService.all_tasks()) == 0

        # Act/Assert
        processing_service1.submit(simulate_task)
        assert processing_service1.task_count == 1
        assert processing_service2.task_count == processing_service3.task_count == 0
        assert len(AsyncIOProcessingService.all_tasks()) == 1

        # Act/Assert
        processing_service2.submit(simulate_task)
        processing_service3.submit(simulate_task)
        assert processing_service1.task_count == processing_service2.task_count == processing_service3.task_count == 1
        assert len(AsyncIOProcessingService.all_tasks()) == 3

        # Act/Assert
        await processing_service1.wait_for_tasks()
        assert processing_service1.task_count == 0
        assert processing_service2.task_count == processing_service3.task_count == 1
        assert len(AsyncIOProcessingService.all_tasks()) == 2

        # Act/Assert
        await asyncio.gather(*AsyncIOProcessingService.all_tasks())
        assert processing_service1.task_count == processing_service2.task_count == processing_service3.task_count == 0
        assert len(AsyncIOProcessingService.all_tasks()) == 0

    # =================================
    # Test Cases for guard decorator
    # =================================

    @pytest.mark.parametrize(
        ["callback", "exception"],
        [
            (0, PyventusException),
            (..., PyventusException),
            (None, PyventusException),
            (True, PyventusException),
            ("True", PyventusException),
            (DummyCallable.Invalid(), PyventusException),
            *[(cb, PyventusException) for cb in DummyCallable.Sync().ALL],
            *[(cb, PyventusException) for cb in DummyCallable.Sync.Generator().ALL],
            *[(cb, PyventusException) for cb in DummyCallable.Async.Generator().ALL],
        ],
    )
    def test_guard_decorator_with_invalid_input(self, callback: Any, exception: type[Exception]) -> None:
        # Arrange/Act/Assert
        with pytest.raises(exception):
            AsyncIOProcessingService.guard(callback)

    # =================================

    def test_guard_decorator(self) -> None:
        # Arrange
        callback: CallableMock.Base = CallableMock.Async()
        processing_service1: AsyncIOProcessingService = AsyncIOProcessingService()
        processing_service2: AsyncIOProcessingService = AsyncIOProcessingService(force_async=True)

        def sync_callback() -> None:
            time.sleep(0.0025)
            processing_service2.submit(callback)

        async def async_callback() -> None:
            await asyncio.sleep(0.0025)
            processing_service1.submit(callback)
            processing_service2.submit(sync_callback)

        # Act
        @AsyncIOProcessingService.guard
        async def amain() -> None:
            # Submit tasks before threading.
            processing_service2.submit(callback)
            processing_service1.submit(async_callback)

            # Test guard within a threaded context.
            with ThreadPoolExecutor() as executor:

                @AsyncIOProcessingService.guard
                async def threaded_amain() -> None:
                    processing_service2.submit(callback)
                    processing_service1.submit(async_callback)

                executor.submit(asyncio.run, threaded_amain()).result()

            # Submit tasks after threading.
            processing_service2.submit(sync_callback)

            # Assert: Verify thread assertions.
            assert callback.call_count == 3
            assert processing_service1.task_count == 1
            assert processing_service2.task_count == 2

        # Run the main function with the guard.
        asyncio.run(amain())

        # Assert: Verify final counts.
        assert callback.call_count == 7
        assert processing_service1.task_count == processing_service2.task_count == 0
