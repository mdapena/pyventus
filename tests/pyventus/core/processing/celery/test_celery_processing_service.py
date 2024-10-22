from concurrent.futures import ThreadPoolExecutor
from typing import Any
from unittest.mock import patch

import pytest
from celery import Celery
from pyventus import PyventusException
from typing_extensions import override

from .....fixtures import CallableMock
from ..processing_service_test import ProcessingServiceTest


class CeleryMock(Celery):  # type: ignore[misc]
    """
    A mock implementation of the Celery class for testing purposes.

    This class simulates the behavior of a Celery worker, allowing for the
    testing of task submissions without requiring a real Celery backend. It
    provides a way to invoke tasks by name with the given arguments.
    """

    def send_task(self, *args: Any, **kwargs: Any) -> None:
        """Simulate sending a task to the Celery worker."""

        # Use a new thread to separate the execution of the task from the current test thread.
        with ThreadPoolExecutor() as executor:
            fut = executor.submit(self.tasks[kwargs["name"]], *kwargs["args"])

        # Retrieve the results and raise
        # any exceptions that occurred.
        fut.result()


class TestCeleryProcessingService(ProcessingServiceTest):
    # =================================
    # Test Cases for creation
    # =================================

    @pytest.mark.parametrize(
        ["celery", "queue"],
        [
            (CeleryMock(), None),
            (CeleryMock(), "Queue"),
        ],
    )
    def test_creation_with_valid_input(self, celery: Celery, queue: str) -> None:
        from pyventus.core.processing.celery import CeleryProcessingService

        # Arrange/Act
        processing_service = CeleryProcessingService(celery=celery, queue=queue)

        # Assert
        assert processing_service is not None
        assert isinstance(processing_service, CeleryProcessingService)

    # =================================

    @pytest.mark.parametrize(
        ["celery", "queue", "exception"],
        [
            (None, None, PyventusException),
            (True, None, PyventusException),
            (object(), None, PyventusException),
            (CeleryMock, None, PyventusException),
            (CeleryMock(), "", PyventusException),
        ],
    )
    def test_creation_with_invalid_input(self, celery: Any, queue: str | None, exception: type[Exception]) -> None:
        from pyventus.core.processing.celery import CeleryProcessingService

        # Arrange/Act/Assert
        with pytest.raises(exception):
            CeleryProcessingService(celery=celery, queue=queue)

    # =================================
    # Test Cases for task registration
    # =================================

    def test_task_registration(self) -> None:
        from pyventus.core.processing.celery import CeleryProcessingService

        # Arrange/Act
        CeleryProcessingService.register()

        # Assert
        assert CeleryProcessingService.CELERY_TASK_NAME in CeleryMock().tasks

    # =================================
    # Test Cases for submission
    # =================================

    @override
    def handle_submission_in_sync_context(
        self, callback: CallableMock.Base, args: tuple[Any, ...], kwargs: dict[str, Any]
    ) -> None:
        # Use patching to override the behavior of pickle.dumps and pickle.loads.
        # This ensures that objects are not serialized or deserialized during testing,
        # allowing access to callback metrics for assertions such as call count and others.
        with (
            patch("pickle.dumps", new=lambda obj: obj),
            patch("pickle.loads", new=lambda obj: obj),
        ):
            from pyventus.core.processing.celery import CeleryProcessingService

            # Arrange: Register the service task and create a new Celery processing service.
            CeleryProcessingService.register()
            processing_service = CeleryProcessingService(celery=CeleryMock())

            # Act: Submit the callback to the processing service with the provided arguments.
            processing_service.submit(callback, *args, **kwargs)

    # =================================

    @override
    async def handle_submission_in_async_context(
        self, callback: CallableMock.Base, args: tuple[Any, ...], kwargs: dict[str, Any]
    ) -> None:
        # Use patching to override the behavior of pickle.dumps and pickle.loads.
        # This ensures that objects are not serialized or deserialized during testing,
        # allowing access to callback metrics for assertions such as call count and others.
        with (
            patch("pickle.dumps", new=lambda obj: obj),
            patch("pickle.loads", new=lambda obj: obj),
        ):
            from pyventus.core.processing.celery import CeleryProcessingService

            # Arrange: Register the service task and create a new Celery processing service.
            CeleryProcessingService.register()
            processing_service = CeleryProcessingService(celery=CeleryMock())

            # Submit the callback to the processing service with the provided arguments.
            processing_service.submit(callback, *args, **kwargs)
