from abc import ABC, abstractmethod
from typing import Any

import pytest

from ....fixtures import CallableMock


class ProcessingServiceTest(ABC):
    """Abstract base class for testing processing services."""

    @abstractmethod
    def handle_submission_in_sync_context(
        self, callback: CallableMock.Base, args: tuple[Any, ...], kwargs: dict[str, Any]
    ) -> None:
        """
        Abstract method to process a callback submission in a synchronous context.

        This method should be implemented by subclasses to instantiate the processing
        service, submit the provided callback with the specified arguments, and ensure
        that the callback execution is complete before returning.

        :param callback: The callback to be submitted for execution.
        :param args: Positional arguments to be passed to the callback.
        :param kwargs: Keyword arguments to be passed to the callback.
        :return: None.
        """
        pass

    @abstractmethod
    async def handle_submission_in_async_context(
        self, callback: CallableMock.Base, args: tuple[Any, ...], kwargs: dict[str, Any]
    ) -> None:
        """
        Abstract method to process a callback submission in an asynchronous context.

        This method should be implemented by subclasses to instantiate the processing
        service, submit the provided callback with the specified arguments, and ensure
        that the callback execution is complete before returning.

        :param callback: The callback to be submitted for execution.
        :param args: Positional arguments to be passed to the callback.
        :param kwargs: Keyword arguments to be passed to the callback.
        :return: None.
        """
        pass

    @pytest.mark.parametrize(
        ["callback_type", "args", "kwargs"],
        [
            (CallableMock.Sync, (), {}),
            (CallableMock.Sync, ("str", 0), {}),
            (CallableMock.Sync, (), {"str": ...}),
            (CallableMock.Sync, ("str", 0), {"str": ...}),
            (CallableMock.Async, (), {}),
            (CallableMock.Async, ("str", 0), {}),
            (CallableMock.Async, (), {"str": ...}),
            (CallableMock.Async, ("str", 0), {"str": ...}),
        ],
    )
    def test_submission_in_sync_context(
        self, callback_type: type[CallableMock.Base], args: tuple[Any, ...], kwargs: dict[str, Any]
    ) -> None:
        """
        Test the submission of a callback in a synchronous context.

        This test verifies that the provided callback is submitted correctly to the
        processing service and that it is executed with the expected arguments.
        It checks that the callback is called exactly once and that the arguments
        passed to the callback match the expected values.

        :param callback_type: The callback type to be instantiated and submitted for execution.
        :param args: Positional arguments to be passed to the callback.
        :param kwargs: Keyword arguments to be passed to the callback.
        :return: None.
        """
        # Arrange/Act: Instantiate the callback and submit it with the provided arguments in a sync context.
        callback: CallableMock.Base = callback_type()
        self.handle_submission_in_sync_context(callback=callback, args=args, kwargs=kwargs)

        # Assert: Verify that the callback was called exactly once with the specified arguments.
        assert callback.call_count == 1, f"Callback was not called exactly once ({callback.call_count} == 1)."
        assert callback.last_args == args, f"Expected args {args}, but got {callback.last_args}."
        assert callback.last_kwargs == kwargs, f"Expected kwargs {kwargs}, but got {callback.last_kwargs}."

    @pytest.mark.parametrize(
        ["callback_type", "args", "kwargs"],
        [
            (CallableMock.Sync, (), {}),
            (CallableMock.Sync, ("str", 0), {}),
            (CallableMock.Sync, (), {"str": ...}),
            (CallableMock.Sync, ("str", 0), {"str": ...}),
            (CallableMock.Async, (), {}),
            (CallableMock.Async, ("str", 0), {}),
            (CallableMock.Async, (), {"str": ...}),
            (CallableMock.Async, ("str", 0), {"str": ...}),
        ],
    )
    async def test_submission_in_async_context(
        self, callback_type: type[CallableMock.Base], args: tuple[Any, ...], kwargs: dict[str, Any]
    ) -> None:
        """
        Test the submission of a callback in an asynchronous context.

        This test verifies that the provided callback is submitted correctly to the
        processing service and that it is executed with the expected arguments when
        called from an asynchronous context. It checks that the callback is called
        exactly once and that the arguments passed to the callback match the
        expected values.

        :param callback_type: The callback type to be instantiated and submitted for execution.
        :param args: Positional arguments to be passed to the callback.
        :param kwargs: Keyword arguments to be passed to the callback.
        :return: None.
        """
        # Arrange/Act: Instantiate the callback and submit it with the provided arguments in an async context.
        callback: CallableMock.Base = callback_type()
        await self.handle_submission_in_async_context(callback=callback, args=args, kwargs=kwargs)

        # Assert: Verify that the callback was called exactly once with the specified arguments.
        assert callback.call_count == 1, f"Callback was not called exactly once ({callback.call_count} == 1)."
        assert callback.last_args == args, f"Expected args {args}, but got {callback.last_args}."
        assert callback.last_kwargs == kwargs, f"Expected kwargs {kwargs}, but got {callback.last_kwargs}."
