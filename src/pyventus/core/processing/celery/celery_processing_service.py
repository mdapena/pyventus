from asyncio import run
from dataclasses import dataclass
from pickle import dumps, loads
from typing import Any, Final, cast

from typing_extensions import override

from ...exceptions import PyventusException, PyventusImportException
from ...loggers import StdOutLogger
from ...utils import attributes_repr, formatted_repr, is_callable_async, summarized_repr
from ..processing_service import ProcessingService, ProcessingServiceCallbackType

try:  # pragma: no cover
    from celery import Celery, shared_task
except ImportError:  # pragma: no cover
    raise PyventusImportException(import_name="celery", is_optional=True, is_dependency=True) from None


class CeleryProcessingService(ProcessingService):
    """
    A processing service that utilizes the `Celery` framework to handle the execution of calls.

    **Notes:**

    -   This service leverages the `Celery` framework to enqueue the provided callbacks into a distributed
        task system, which is monitored by multiple workers. Once enqueued, these callbacks are eligible
        for retrieval and processing by available workers, enabling a scalable and distributed approach
        to handling calls asynchronously.

    -   Synchronous callbacks are executed in a blocking manner inside the worker, while asynchronous
        callbacks are processed within a new asyncio event loop using the `asyncio.run()` function.
    """

    CELERY_TASK_NAME: Final[str] = "pyventus_task"
    """The name of the task in Celery."""

    @dataclass(slots=True, frozen=True)
    class CeleryPayload:
        """A data class representing the payload of the `CeleryProcessingService`."""

        callback: ProcessingServiceCallbackType
        args: tuple[Any, ...]
        kwargs: dict[str, Any]

    @classmethod
    def register(cls) -> None:
        """
        Register the service's task globally in `Celery`.

        **Notes:**

        -   This method should be invoked in the `Celery` worker script to ensure that the task is
            accessible to both the client and the worker. If this method is not called, a `KeyError`
            will be raised when attempting to submit a new callback.

        -   This method uses the `shared_task` functionality from the `Celery` framework to register
            the service's task, making it available independently of the `Celery` instance used.

        -   The registered task is a `Celery` task that will be used to process the execution
            of callbacks.

        :return: None.
        """

        def task(serialized_payload: bytes) -> None:
            """
            Celery task that processes the callbacks' execution with the given arguments.

            :param serialized_payload: The serialized data representing the callback and its arguments.
            :return: None.
            :raises PyventusException: If the serialized payload is invalid or cannot be deserialized.
            """
            # Validate that the serialized payload is provided.
            if not serialized_payload:  # pragma: no cover
                raise PyventusException("The 'serialized_payload' argument is required but was not received.")

            # Deserialize the payload to retrieve the original callback and its arguments.
            payload = cast(CeleryProcessingService.CeleryPayload, loads(serialized_payload))

            # Validate the deserialized payload to ensure it is of the expected type.
            if payload is None or not isinstance(payload, CeleryProcessingService.CeleryPayload):  # pragma: no cover
                raise PyventusException("Failed to deserialize the given payload.")

            # Check if the callback is asynchronous and execute accordingly.
            if is_callable_async(payload.callback):
                # Run the async callback in a new asyncio event loop.
                run(payload.callback(*payload.args, **payload.kwargs))
            else:
                # Run the sync callback directly with the provided arguments.
                payload.callback(*payload.args, **payload.kwargs)

        # Register the service's task as a shared task in Celery.
        shared_task(name=cls.CELERY_TASK_NAME)(task)

    # Attributes for the CeleryProcessingService
    __slots__ = ("__celery", "__queue")

    def __init__(self, celery: Celery, queue: str | None = None) -> None:
        """
        Initialize an instance of `CeleryProcessingService`.

        :param celery: The Celery object used to enqueue and process callbacks.
        :param queue: The name of the queue where callbacks will be enqueued. Defaults to
            None, which uses the `task_default_queue` from the Celery configuration.
        :raises PyventusException: If the Celery instance is invalid or if the
            queue name is set but empty.
        """
        # Validate the Celery instance.
        if celery is None or not isinstance(celery, Celery):
            raise PyventusException("The 'celery' argument must be an instance of the Celery class.")

        # Check if the Celery app configuration uses the 'auth' serializer.
        if celery.conf.task_serializer != "auth":
            StdOutLogger.warning(
                source=summarized_repr(self),
                action="Security Message:",
                msg=(
                    "To enhance security in message communication, it is recommended to employ the Celery 'auth' "
                    "serializer. While this service is serializer-agnostic, it relies on the pickling process to "
                    "convert callbacks and their arguments into transmittable data, making security a critical "
                    "consideration. Please refer to: https://docs.celeryq.dev/en/stable/userguide/security.html"
                ),
            )

        # Validate the queue name, if provided.
        if queue is not None and len(queue) == 0:
            raise PyventusException("The 'queue' argument cannot be empty.")

        # Assign the Celery instance and queue name.
        self.__celery: Celery = celery
        self.__queue: str = queue if queue else self.__celery.conf.task_default_queue

    def __repr__(self) -> str:
        """
        Retrieve a string representation of the instance.

        :return: A string representation of the instance.
        """
        return formatted_repr(
            instance=self,
            info=attributes_repr(
                celery=self.__celery,
                queue=self.__queue,
            ),
        )

    @override
    def submit(self, callback: ProcessingServiceCallbackType, *args: Any, **kwargs: Any) -> None:
        # Create the Celery payload to encapsulate the callback and its arguments.
        payload = CeleryProcessingService.CeleryPayload(callback=callback, args=args, kwargs=kwargs)

        # Serialize the payload object.
        serialized_payload: bytes = dumps(payload)

        # Send the serialized payload to Celery for asynchronous execution.
        self.__celery.send_task(
            name=self.__class__.CELERY_TASK_NAME,
            args=(serialized_payload,),
            queue=self.__queue,
        )
