from abc import ABC, abstractmethod
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any

import pytest
from pyventus.core.processing.processing_service import ProcessingService

from ....fixtures import CallableMock


class ProcessingServiceTest(ABC):
    """Abstract base class for testing processing services."""

    @dataclass(slots=True, frozen=True)
    class SubmissionTestCase:
        """A test case for validating the execution of callbacks in the submission process."""

        callback_type: type[CallableMock.Base]
        args: tuple[Any, ...]
        kwargs: dict[str, Any]

        @contextmanager
        def execute(self, processing_service: ProcessingService) -> Generator[None, None, None]:
            """
            Execute the test case using the specified processing service.

            This method validates that the `submit` method of the processing service calls each
            callback exactly once, using the specified arguments.

            :param processing_service: The processing service used to handle the submission.
            :yield: Control returns to the main code execution, allowing for any additional processing.
            """
            # Arrange: Instantiate multiple callback instances for testing.
            callback1: CallableMock.Base = self.callback_type()
            callback2: CallableMock.Base = self.callback_type()
            callback3: CallableMock.Base = self.callback_type()

            # Act: Submit each callback with the provided arguments.
            processing_service.submit(callback1, *self.args, **self.kwargs)
            processing_service.submit(callback2, *self.args, **self.kwargs)
            processing_service.submit(callback3, *self.args, **self.kwargs)
            yield None  # Yield control for any additional processing.

            # Assert: Verify that each callback was called exactly once with the specified arguments.
            assert callback1.call_count == callback2.call_count == callback3.call_count == 1
            assert callback1.last_args == callback2.last_args == callback3.last_args == self.args
            assert callback1.last_kwargs == callback2.last_kwargs == callback3.last_kwargs == self.kwargs

    @abstractmethod
    def run_submission_test_case_in_sync_ctx(self, test_case: SubmissionTestCase) -> None:
        """
        Abstract method that performs the execution of the submission test case in a synchronous context.

        This method must be implemented by subclasses and should include the creation of the processing service
        used in the execution of the submission test case. Additionally, it must handle any requirements to process
        the submission before returning from the execution context.

        :param test_case: The submission test case to be executed.
        :return: None.
        """
        pass

    @abstractmethod
    async def run_submission_test_case_in_async_ctx(self, test_case: SubmissionTestCase) -> None:
        """
        Abstract method that performs the execution of the submission test case in an asynchronous context.

        This method must be implemented by subclasses and should include the creation of the processing service
        used during the execution of the submission test case. Additionally, it must address any requirements
        to process the submission before returning from the execution context.

        :param test_case: The submission test case to be executed.
        :return: None.
        """
        pass

    @pytest.mark.parametrize(
        ["test_case"],
        [
            (
                SubmissionTestCase(
                    callback_type=CallableMock.Sync,
                    args=(),
                    kwargs={},
                ),
            ),
            (
                SubmissionTestCase(
                    callback_type=CallableMock.Sync,
                    args=("string", 0),
                    kwargs={},
                ),
            ),
            (
                SubmissionTestCase(
                    callback_type=CallableMock.Sync,
                    args=(),
                    kwargs={"string": ...},
                ),
            ),
            (
                SubmissionTestCase(
                    callback_type=CallableMock.Sync,
                    args=("string", 0),
                    kwargs={"string": ...},
                ),
            ),
            (
                SubmissionTestCase(
                    callback_type=CallableMock.Async,
                    args=(),
                    kwargs={},
                ),
            ),
            (
                SubmissionTestCase(
                    callback_type=CallableMock.Async,
                    args=("string", 0),
                    kwargs={},
                ),
            ),
            (
                SubmissionTestCase(
                    callback_type=CallableMock.Async,
                    args=(),
                    kwargs={"string": ...},
                ),
            ),
            (
                SubmissionTestCase(
                    callback_type=CallableMock.Async,
                    args=("string", 0),
                    kwargs={"string": ...},
                ),
            ),
        ],
    )
    def test_submission_in_sync_context(self, test_case: SubmissionTestCase) -> None:
        """
        Test the submission process in a synchronous context.

        This test verifies the behavior of the `submit` method of the processing service against multiple
        scenarios, ensuring that various callback types and argument combinations are handled correctly.

        :param test_case: The test case containing different scenarios for testing the submission process.
        :return: None.
        """
        self.run_submission_test_case_in_sync_ctx(test_case)

    @pytest.mark.parametrize(
        ["test_case"],
        [
            (
                SubmissionTestCase(
                    callback_type=CallableMock.Sync,
                    args=(),
                    kwargs={},
                ),
            ),
            (
                SubmissionTestCase(
                    callback_type=CallableMock.Sync,
                    args=("string", 0),
                    kwargs={},
                ),
            ),
            (
                SubmissionTestCase(
                    callback_type=CallableMock.Sync,
                    args=(),
                    kwargs={"string": ...},
                ),
            ),
            (
                SubmissionTestCase(
                    callback_type=CallableMock.Sync,
                    args=("string", 0),
                    kwargs={"string": ...},
                ),
            ),
            (
                SubmissionTestCase(
                    callback_type=CallableMock.Async,
                    args=(),
                    kwargs={},
                ),
            ),
            (
                SubmissionTestCase(
                    callback_type=CallableMock.Async,
                    args=("string", 0),
                    kwargs={},
                ),
            ),
            (
                SubmissionTestCase(
                    callback_type=CallableMock.Async,
                    args=(),
                    kwargs={"string": ...},
                ),
            ),
            (
                SubmissionTestCase(
                    callback_type=CallableMock.Async,
                    args=("string", 0),
                    kwargs={"string": ...},
                ),
            ),
        ],
    )
    async def test_submission_in_async_context(self, test_case: SubmissionTestCase) -> None:
        """
        Test the submission process in an asynchronous context.

        This test verifies the behavior of the `submit` method of the processing service against multiple
        scenarios, ensuring that various callback types and argument combinations are handled correctly
        in an asynchronous context.

        :param test_case: The test case containing different scenarios for testing the submission process.
        :return: None.
        """
        await self.run_submission_test_case_in_async_ctx(test_case)
