import asyncio
import time
from collections import deque
from collections.abc import Awaitable, Callable, Generator
from contextlib import contextmanager
from threading import Lock, current_thread, main_thread
from typing import Any

import pytest
from pyventus.core.exceptions.pyventus_exception import PyventusException
from pyventus.core.processing.asyncio import AsyncIOProcessingService
from typing_extensions import override

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
    # Test Cases for ordered submissions
    # =================================

    @contextmanager
    def run_ordered_submission_tests(
        self, force_async: bool | None, enforce_submission_order: bool | None
    ) -> Generator[AsyncIOProcessingService, None, None]:
        # Arrange
        class ExecutionOrderTracker:
            def __init__(self) -> None:
                self._thread_lock: Lock = Lock()
                self._compile_time_ids: list[int] = []
                self._runtime_ids: list[int] = []

            def create_synchronous_callback(self, delay: float = 0) -> Callable[[], None]:
                with self._thread_lock:
                    callback_id: int = len(self._compile_time_ids)
                    self._compile_time_ids.append(callback_id)

                def _synchronous_callback() -> None:
                    time.sleep(delay)
                    with self._thread_lock:
                        self._runtime_ids.append(callback_id)

                return _synchronous_callback

            def create_asynchronous_callback(self, delay: float = 0) -> Callable[[], Awaitable[None]]:
                with self._thread_lock:
                    callback_id: int = len(self._compile_time_ids)
                    self._compile_time_ids.append(callback_id)

                async def _asynchronous_callback() -> None:
                    await asyncio.sleep(delay)
                    with self._thread_lock:
                        self._runtime_ids.append(callback_id)

                return _asynchronous_callback

        tracker = ExecutionOrderTracker()
        callbacks: list[Callable[[], None | Awaitable[None]]] = [
            tracker.create_asynchronous_callback(delay=0.0025),
            tracker.create_synchronous_callback(delay=0.0025),
            tracker.create_asynchronous_callback(delay=0.0015),
            tracker.create_synchronous_callback(delay=0.0015),
            tracker.create_asynchronous_callback(delay=0.0005),
            tracker.create_synchronous_callback(delay=0.0005),
        ]

        kwargs: dict[str, Any] = {}
        if force_async is not None:
            kwargs["force_async"] = force_async
        if enforce_submission_order is not None:
            kwargs["enforce_submission_order"] = enforce_submission_order
        processing_service = AsyncIOProcessingService(**kwargs)

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
    def test_ordered_submissions_in_sync_ctx(
        self, force_async: bool | None, enforce_submission_order: bool | None
    ) -> None:
        with self.run_ordered_submission_tests(force_async, enforce_submission_order):
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
    async def test_ordered_submissions_in_async_ctx(
        self, force_async: bool | None, enforce_submission_order: bool | None
    ) -> None:
        with self.run_ordered_submission_tests(force_async, enforce_submission_order) as procesing_service:
            await procesing_service.wait_for_tasks()
