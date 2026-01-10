from concurrent.futures import Executor, ProcessPoolExecutor, ThreadPoolExecutor
from typing import Any

import pytest
from pyventus import PyventusException
from pyventus.core.processing.executor import ExecutorProcessingService
from typing_extensions import override

from ..processing_service_test import ProcessingServiceTest


class TestExecutorProcessingService(ProcessingServiceTest):
    # =================================
    # Test Cases for creation
    # =================================

    @pytest.mark.parametrize(
        ["executor"],
        [
            (ThreadPoolExecutor(),),
            (ProcessPoolExecutor(),),
        ],
    )
    def test_creation_with_valid_input(self, executor: Executor) -> None:
        # Arrange/Act
        processing_service = ExecutorProcessingService(executor=executor)

        # Assert
        assert processing_service is not None
        assert isinstance(processing_service, ExecutorProcessingService)

    # =================================

    @pytest.mark.parametrize(
        ["executor", "exception"],
        [
            (None, PyventusException),
            (True, PyventusException),
            (object(), PyventusException),
            (ThreadPoolExecutor, PyventusException),
        ],
    )
    def test_creation_with_invalid_input(self, executor: Any, exception: type[Exception]) -> None:
        # Arrange/Act/Assert
        with pytest.raises(exception):
            ExecutorProcessingService(executor=executor)

    # =================================
    # Test Cases for shutdown
    # =================================

    def test_shutdown(self) -> None:
        # Arrange
        executor = ThreadPoolExecutor()
        processing_service = ExecutorProcessingService(executor=executor)

        # Act
        processing_service.shutdown()

        # Assert
        assert executor._shutdown is True

    # =================================
    # Test Cases for shutdown by context
    # =================================

    def test_shutdown_by_context(self) -> None:
        # Arrange
        executor = ThreadPoolExecutor()

        # Act
        with ExecutorProcessingService(executor=executor):
            pass

        # Assert
        assert executor._shutdown is True

    # =================================
    # Test Cases for submission
    # =================================

    @override
    def run_submission_test_case_in_sync_ctx(self, test_case: ProcessingServiceTest.SubmissionTestCase) -> None:
        processing_service = ExecutorProcessingService(executor=ThreadPoolExecutor())
        with test_case.execute(processing_service):
            processing_service.shutdown()

    # =================================

    @override
    async def run_submission_test_case_in_async_ctx(self, test_case: ProcessingServiceTest.SubmissionTestCase) -> None:
        processing_service = ExecutorProcessingService(executor=ThreadPoolExecutor())
        with test_case.execute(processing_service):
            processing_service.shutdown()
