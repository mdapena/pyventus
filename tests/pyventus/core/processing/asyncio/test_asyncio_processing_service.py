from typing import Any

from pyventus.core.processing.asyncio import AsyncIOProcessingService
from typing_extensions import override

from .....fixtures import CallableMock
from ..processing_service_test import ProcessingServiceTest


class TestAsyncIOProcessingService(ProcessingServiceTest):
    # =================================
    # Test Cases for creation
    # =================================

    def test_creation(self) -> None:
        # Arrange/Act
        processing_service = AsyncIOProcessingService()

        # Assert
        assert processing_service is not None
        assert isinstance(processing_service, AsyncIOProcessingService)

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
    # Test Cases for submission
    # =================================

    @override
    def handle_submission_in_sync_context(
        self, callback: CallableMock.Base, args: tuple[Any, ...], kwargs: dict[str, Any]
    ) -> None:
        # Arrange
        processing_service = AsyncIOProcessingService()

        # Act
        processing_service.submit(callback, *args, **kwargs)

    # =================================

    @override
    async def handle_submission_in_async_context(
        self, callback: CallableMock.Base, args: tuple[Any, ...], kwargs: dict[str, Any]
    ) -> None:
        # Arrange
        processing_service = AsyncIOProcessingService()

        # Act
        processing_service.submit(callback, *args, **kwargs)
        await processing_service.wait_for_tasks()
