import asyncio
from typing import Any

import pytest
from fastapi import BackgroundTasks, Depends, FastAPI
from fastapi.testclient import TestClient
from pyventus import PyventusException
from pyventus.core.processing.fastapi import FastAPIProcessingService
from starlette.status import HTTP_200_OK
from typing_extensions import override

from ..processing_service_test import ProcessingServiceTest


class TestFastAPIProcessingService(ProcessingServiceTest):
    # =================================
    # Test Cases for creation
    # =================================

    def test_creation_with_valid_input(self) -> None:
        # Arrange/Act
        processing_service = FastAPIProcessingService(background_tasks=BackgroundTasks())

        # Assert
        assert processing_service is not None
        assert isinstance(processing_service, FastAPIProcessingService)

    # =================================

    def test_creation_with_fastapi_depends(self) -> None:
        # Arrange
        client = TestClient(FastAPI())

        # Act/Assert
        @client.app.get("/")  # type: ignore[attr-defined,untyped-decorator]
        def api(
            processing_service: FastAPIProcessingService = Depends(FastAPIProcessingService),  # noqa: B008
        ) -> None:
            assert processing_service is not None
            assert isinstance(processing_service, FastAPIProcessingService)

        res = client.get("/")
        assert res.status_code == HTTP_200_OK

    # =================================

    @pytest.mark.parametrize(
        ["background_tasks", "exception"],
        [
            (None, PyventusException),
            (True, PyventusException),
            (object(), PyventusException),
            (BackgroundTasks, PyventusException),
        ],
    )
    def test_creation_with_invalid_input(self, background_tasks: Any, exception: type[Exception]) -> None:
        # Arrange/Act/Assert
        with pytest.raises(exception):
            FastAPIProcessingService(background_tasks=background_tasks)

    # =================================
    # Test Cases for submission
    # =================================

    @override
    def run_submission_test_case_in_sync_ctx(self, test_case: ProcessingServiceTest.SubmissionTestCase) -> None:
        client = TestClient(FastAPI())

        @client.app.get("/")  # type: ignore[attr-defined,untyped-decorator]
        def api(background_tasks: BackgroundTasks) -> None:
            processing_service = FastAPIProcessingService(background_tasks=background_tasks)
            with test_case.execute(processing_service):
                asyncio.run(background_tasks())

        res = client.get("/")
        assert res.status_code == HTTP_200_OK

    # =================================

    @override
    async def run_submission_test_case_in_async_ctx(self, test_case: ProcessingServiceTest.SubmissionTestCase) -> None:
        client = TestClient(FastAPI())

        @client.app.get("/")  # type: ignore[attr-defined,untyped-decorator]
        async def api(background_tasks: BackgroundTasks) -> None:
            processing_service = FastAPIProcessingService(background_tasks=background_tasks)
            with test_case.execute(processing_service):
                await background_tasks()

        res = client.get("/")
        assert res.status_code == HTTP_200_OK
