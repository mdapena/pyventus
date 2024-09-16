from typing import Any

import pytest
from fakeredis import FakeStrictRedis
from pyventus import PyventusException
from pyventus.core.processing.redis import RedisProcessingService
from pyventus.core.utils import is_callable_async
from rq import Queue
from typing_extensions import override

from .....fixtures import CallableMock
from ..processing_service_test import ProcessingServiceTest


class TestRedisProcessingService(ProcessingServiceTest):
    # =================================
    # Test Cases for creation
    # =================================

    @pytest.mark.parametrize(
        ["queue", "options"],
        [
            (Queue(connection=FakeStrictRedis(), is_async=False), None),
            (Queue(connection=FakeStrictRedis(), is_async=False), {"ttl": 30}),
        ],
    )
    def test_creation_with_valid_input(self, queue: Queue, options: dict[str, Any]) -> None:
        # Arrange/Act
        processing_service = RedisProcessingService(queue=queue, options=options)

        # Assert
        assert processing_service is not None
        assert isinstance(processing_service, RedisProcessingService)

    # =================================

    @pytest.mark.parametrize(
        ["queue", "options", "exception"],
        [
            (None, None, PyventusException),
            (True, None, PyventusException),
            (object(), None, PyventusException),
            (Queue, None, PyventusException),
        ],
    )
    def test_creation_with_invalid_input(self, queue: Any, options: dict[str, Any], exception: type[Exception]) -> None:
        # Arrange/Act/Assert
        with pytest.raises(exception):
            RedisProcessingService(queue=queue, options=options)

    # =================================
    # Test Cases for submission
    # =================================

    @override
    def handle_submission_in_sync_context(
        self, callback: CallableMock.Base, args: tuple[Any, ...], kwargs: dict[str, Any]
    ) -> None:
        # Arrange
        processing_service = RedisProcessingService(queue=Queue(connection=FakeStrictRedis(), is_async=False))

        # Act
        processing_service.submit(callback, *args, **kwargs)

    # =================================

    @override
    async def handle_submission_in_async_context(
        self, callback: CallableMock.Base, args: tuple[Any, ...], kwargs: dict[str, Any]
    ) -> None:
        # Skip the test if the callback is async, as RQ cannot
        # execute async callbacks in an async context during testing.
        if is_callable_async(callback):
            pytest.skip("During testing, the RQ package cannot execute async callbacks in an async context.")

        # Arrange
        processing_service = RedisProcessingService(queue=Queue(connection=FakeStrictRedis(), is_async=False))

        # Act
        processing_service.submit(callback, *args, **kwargs)
