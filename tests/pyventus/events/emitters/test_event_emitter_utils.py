from pyventus.events import (
    AsyncIOEventEmitter,
    CeleryEventEmitter,
    EventEmitter,
    EventLinker,
    ExecutorEventEmitter,
    ExecutorEventEmitterCtx,
    FastAPIEventEmitter,
)

from ....utils import get_private_attr


class TestEventEmitterUtils:
    # =================================
    # Test Cases for AsyncIOEventEmitter
    # =================================

    def test_AsyncIOEventEmitter(self) -> None:  # noqa: N802
        from pyventus.core.processing.asyncio import AsyncIOProcessingService

        # Arrange
        class IsolatedEventLinker(EventLinker): ...

        # Act
        event_emitter = AsyncIOEventEmitter(event_linker=IsolatedEventLinker, debug=True)
        event_processor = get_private_attr(event_emitter, "__event_processor")
        event_linker = get_private_attr(event_emitter, "__event_linker")
        logger = get_private_attr(event_emitter, "__logger")

        # Assert creation and properties
        assert event_emitter is not None
        assert isinstance(event_emitter, EventEmitter)
        assert isinstance(event_processor, AsyncIOProcessingService)
        assert event_linker is IsolatedEventLinker
        assert logger.debug_enabled is True

    # =================================
    # Test Cases for CeleryEventEmitter
    # =================================

    def test_CeleryEventEmitter(self) -> None:  # noqa: N802
        from celery import Celery
        from pyventus.core.processing.celery import CeleryProcessingService

        # Arrange
        class IsolatedEventLinker(EventLinker): ...

        celery = Celery()
        queue = "Queue"

        # Act
        event_emitter = CeleryEventEmitter(celery=celery, queue=queue, event_linker=IsolatedEventLinker, debug=True)
        event_processor = get_private_attr(event_emitter, "__event_processor")
        event_linker = get_private_attr(event_emitter, "__event_linker")
        logger = get_private_attr(event_emitter, "__logger")

        # Assert creation and properties
        assert event_emitter is not None
        assert isinstance(event_emitter, EventEmitter)
        assert isinstance(event_processor, CeleryProcessingService)
        assert get_private_attr(event_processor, "__celery") is celery
        assert get_private_attr(event_processor, "__queue") is queue
        assert event_linker is IsolatedEventLinker
        assert logger.debug_enabled is True

    # =================================
    # Test Cases for ExecutorEventEmitter
    # =================================

    def test_ExecutorEventEmitter(self) -> None:  # noqa: N802
        from concurrent.futures import ThreadPoolExecutor

        from pyventus.core.processing.executor import ExecutorProcessingService

        # Arrange
        class IsolatedEventLinker(EventLinker): ...

        executor = ThreadPoolExecutor()

        # Act
        event_emitter = ExecutorEventEmitter(executor=executor, event_linker=IsolatedEventLinker, debug=True)
        event_processor = get_private_attr(event_emitter, "__event_processor")
        event_linker = get_private_attr(event_emitter, "__event_linker")
        logger = get_private_attr(event_emitter, "__logger")

        # Assert creation and properties
        assert event_emitter is not None
        assert isinstance(event_emitter, EventEmitter)
        assert isinstance(event_processor, ExecutorProcessingService)
        assert get_private_attr(event_processor, "__executor") is executor
        assert event_linker is IsolatedEventLinker
        assert logger.debug_enabled is True
        assert executor._shutdown is False

    # =================================
    # Test Cases for ExecutorEventEmitterCtx
    # =================================

    def test_ExecutorEventEmitterCtx(self) -> None:  # noqa: N802
        from concurrent.futures import ThreadPoolExecutor

        from pyventus.core.processing.executor import ExecutorProcessingService

        # Arrange
        class IsolatedEventLinker(EventLinker): ...

        executor = ThreadPoolExecutor()

        # Act
        with ExecutorEventEmitterCtx(executor=executor, event_linker=IsolatedEventLinker, debug=True) as event_emitter:
            event_processor = get_private_attr(event_emitter, "__event_processor")
            event_linker = get_private_attr(event_emitter, "__event_linker")
            logger = get_private_attr(event_emitter, "__logger")

        # Assert creation and properties
        assert event_emitter is not None
        assert isinstance(event_emitter, EventEmitter)
        assert isinstance(event_processor, ExecutorProcessingService)
        assert get_private_attr(event_processor, "__executor") is executor
        assert event_linker is IsolatedEventLinker
        assert logger.debug_enabled is True
        assert executor._shutdown is True

    # =================================
    # Test Cases for FastAPIEventEmitter
    # =================================

    def test_FastAPIEventEmitter(self) -> None:  # noqa: N802
        from fastapi import BackgroundTasks, Depends, FastAPI
        from fastapi.testclient import TestClient
        from pyventus.core.processing.fastapi import FastAPIProcessingService
        from starlette.status import HTTP_200_OK

        # Arrange
        class IsolatedEventLinker(EventLinker): ...

        client = TestClient(FastAPI())

        # Act
        @client.app.get("/")  # type: ignore[attr-defined, misc]
        def api(
            background_tasks: BackgroundTasks,
            event_emitter: EventEmitter = Depends(FastAPIEventEmitter(IsolatedEventLinker, True)),  # noqa: B008
        ) -> None:
            event_processor = get_private_attr(event_emitter, "__event_processor")
            event_linker = get_private_attr(event_emitter, "__event_linker")
            logger = get_private_attr(event_emitter, "__logger")

            # Assert creation and properties
            assert event_emitter is not None
            assert isinstance(event_emitter, EventEmitter)
            assert isinstance(event_processor, FastAPIProcessingService)
            assert get_private_attr(event_processor, "__background_tasks") is background_tasks
            assert event_linker is IsolatedEventLinker
            assert logger.debug_enabled is True

        assert client.get("/").status_code == HTTP_200_OK

    # =================================
    # Test Cases for RedisEventEmitter
    # =================================

    def test_RedisEventEmitter(self) -> None:  # noqa: N802
        from fakeredis import FakeStrictRedis
        from pyventus.core.processing.redis import RedisProcessingService
        from pyventus.events import RedisEventEmitter
        from rq import Queue

        # Arrange
        class IsolatedEventLinker(EventLinker): ...

        queue = Queue(connection=FakeStrictRedis(), is_async=False)
        options = {"ttl": 1}

        # Act
        event_emitter = RedisEventEmitter(queue=queue, options=options, event_linker=IsolatedEventLinker, debug=True)
        event_processor = get_private_attr(event_emitter, "__event_processor")
        event_linker = get_private_attr(event_emitter, "__event_linker")
        logger = get_private_attr(event_emitter, "__logger")

        # Assert creation and properties
        assert event_emitter is not None
        assert isinstance(event_emitter, EventEmitter)
        assert isinstance(event_processor, RedisProcessingService)
        assert get_private_attr(event_processor, "__queue") is queue
        assert get_private_attr(event_processor, "__options") is options
        assert event_linker is IsolatedEventLinker
        assert logger.debug_enabled is True
