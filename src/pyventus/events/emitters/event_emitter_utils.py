from collections.abc import Callable, Generator
from concurrent.futures import Executor, ThreadPoolExecutor
from contextlib import contextmanager
from typing import Any

from ..linkers import EventLinker
from .event_emitter import EventEmitter


def AsyncIOEventEmitter(  # noqa: N802
    event_linker: type[EventLinker] = EventLinker,
    debug: bool | None = None,
) -> EventEmitter:
    """
    Create an `EventEmitter` instance configured with the `AsyncIOProcessingService`.

    :param event_linker: Specifies the type of event linker used to manage and access events along with their
        corresponding subscribers. Defaults to `EventLinker`.
    :param debug: Specifies the debug mode for the logger. If `None`, it is determined based on the
        execution environment.
    :return: An instance of `EventEmitter` configured with the `AsyncIOProcessingService`.
    """
    from ...core.processing.asyncio import AsyncIOProcessingService

    processing_service = AsyncIOProcessingService()

    return EventEmitter(
        event_processor=processing_service,
        event_linker=event_linker,
        debug=debug,
    )


def CeleryEventEmitter(  # noqa: N802
    celery: Any,
    queue: str | None = None,
    event_linker: type[EventLinker] = EventLinker,
    debug: bool | None = None,
) -> EventEmitter:
    """
    Create an `EventEmitter` instance configured with the `CeleryProcessingService`.

    :param celery: The Celery object used to enqueue and process event emissions.
    :param queue: The name of the queue where the event emission will be enqueued.
        Defaults to None, which uses the task_default_queue from the Celery configuration.
    :param event_linker: Specifies the type of event linker used to manage and access events along with their
        corresponding subscribers. Defaults to `EventLinker`.
    :param debug: Specifies the debug mode for the logger. If `None`, it is determined based on the
        execution environment.
    :return: An instance of `EventEmitter` configured with the `CeleryProcessingService`.
    """
    from ...core.processing.celery import CeleryProcessingService

    processing_service = CeleryProcessingService(celery=celery, queue=queue)

    return EventEmitter(
        event_processor=processing_service,
        event_linker=event_linker,
        debug=debug,
    )


def ExecutorEventEmitter(  # noqa: N802
    executor: Executor,
    event_linker: type[EventLinker] = EventLinker,
    debug: bool | None = None,
) -> EventEmitter:
    """
    Create an `EventEmitter` instance configured with the `ExecutorProcessingService`.

    :param executor: The executor object used to handle the execution of event emissions.
    :param event_linker: Specifies the type of event linker used to manage and access events along with their
        corresponding subscribers. Defaults to `EventLinker`.
    :param debug: Specifies the debug mode for the logger. If `None`, it is determined based on the
        execution environment.
    :return: An instance of `EventEmitter` configured with the `ExecutorProcessingService`.
    """
    from ...core.processing.executor import ExecutorProcessingService

    processing_service = ExecutorProcessingService(executor=executor)

    return EventEmitter(
        event_processor=processing_service,
        event_linker=event_linker,
        debug=debug,
    )


@contextmanager
def ExecutorEventEmitterCtx(  # noqa: N802
    executor: Executor | None = None,
    event_linker: type[EventLinker] = EventLinker,
    debug: bool | None = None,
) -> Generator[EventEmitter, None, None]:
    """
    Context manager that creates an `EventEmitter` instance configured with the `ExecutorProcessingService`.

    This context manager yields an `EventEmitter` instance, which can be used within a `with` statement.
    Upon exiting the context, the processing service is properly shut down.

    :param executor: The executor object used to handle the execution of event emissions. If `None`,
        a `ThreadPoolExecutor` with default settings will be created.
    :param event_linker: Specifies the type of event linker used to manage and access events along with their
        corresponding subscribers. Defaults to `EventLinker`.
    :param debug: Specifies the debug mode for the logger. If `None`, it is determined based on the
        execution environment.
    :return: An instance of `EventEmitter` configured with the `ExecutorProcessingService`.
    """
    from ...core.processing.executor import ExecutorProcessingService

    processing_service = ExecutorProcessingService(executor=(executor if executor else ThreadPoolExecutor()))

    yield EventEmitter(
        event_processor=processing_service,
        event_linker=event_linker,
        debug=debug,
    )

    processing_service.shutdown()


def FastAPIEventEmitter(  # noqa: N802
    event_linker: type[EventLinker] = EventLinker,
    debug: bool | None = None,
) -> Callable[[Any], EventEmitter]:
    """
    Create an `EventEmitter` instance configured with the `FastAPIProcessingService`.

    This function is compatible with FastAPI's dependency injection system and should be
    used with the `Depends` method to automatically provide the `BackgroundTasks` instance.

    :param event_linker: Specifies the type of event linker used to manage and access events along with their
        corresponding subscribers. Defaults to `EventLinker`.
    :param debug: Specifies the debug mode for the logger. If `None`, it is determined based on the
        execution environment.
    :return: An instance of `EventEmitter` configured with the `FastAPIProcessingService`.
    """
    from fastapi import BackgroundTasks

    from ...core.processing.fastapi import FastAPIProcessingService

    def create_event_emitter(background_tasks: BackgroundTasks) -> EventEmitter:
        """
        Create and return an `EventEmitter` instance using the provided `BackgroundTasks`.

        :param background_tasks: The FastAPI `BackgroundTasks` object used to handle the execution of event emissions.
        :return: An instance of `EventEmitter` configured with the `FastAPIProcessingService`.
        """
        processing_service = FastAPIProcessingService(background_tasks=background_tasks)

        return EventEmitter(
            event_processor=processing_service,
            event_linker=event_linker,
            debug=debug,
        )

    return create_event_emitter


def RedisEventEmitter(  # noqa: N802
    queue: Any,
    options: dict[str, Any] | None = None,
    event_linker: type[EventLinker] = EventLinker,
    debug: bool | None = None,
) -> EventEmitter:
    """
    Create an `EventEmitter` instance configured with the `RedisProcessingService`.

    :param queue: The Redis queue object used to enqueue and process event emissions.
    :param options: Additional options for the RQ package enqueueing method. Defaults to None (an empty dictionary).
    :param event_linker: Specifies the type of event linker used to manage and access events along with their
        corresponding subscribers. Defaults to `EventLinker`.
    :param debug: Specifies the debug mode for the logger. If `None`, it is determined based on the
        execution environment.
    :return: An instance of `EventEmitter` configured with the `RedisProcessingService`.
    """
    from ...core.processing.redis import RedisProcessingService

    processing_service = RedisProcessingService(queue=queue, options=options)

    return EventEmitter(
        event_processor=processing_service,
        event_linker=event_linker,
        debug=debug,
    )
