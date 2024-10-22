from typing import Any

from typing_extensions import override

from ...exceptions import PyventusException, PyventusImportException
from ...utils import attributes_repr, formatted_repr
from ..processing_service import ProcessingService, ProcessingServiceCallbackType

try:  # pragma: no cover
    from rq import Queue
except ImportError:  # pragma: no cover
    raise PyventusImportException(import_name="rq", is_optional=True, is_dependency=True) from None


class RedisProcessingService(ProcessingService):
    """
    A processing service that utilizes the `Redis Queue` framework to handle the execution of calls.

    **Notes:**

    -   This service leverages the `RQ` Python package to enqueue the provided callbacks into a Redis
        distributed task system, which is monitored by multiple workers. Once enqueued, these callbacks
        are eligible for retrieval and processing by available workers, enabling a scalable and
        distributed approach to handling calls asynchronously.

    -   Synchronous callbacks are executed in a blocking manner inside the worker, while asynchronous
        callbacks are processed within a new asyncio event loop using the `asyncio.run()` function.
    """

    # Attributes for the RedisProcessingService
    __slots__ = ("__queue", "__options")

    def __init__(self, queue: Queue, options: dict[str, Any] | None = None) -> None:
        """
        Initialize an instance of `RedisProcessingService`.

        :param queue: The Redis queue used to enqueue and process callbacks.
        :param options: Additional options for the RQ package enqueueing method.
            Defaults to None (an empty dictionary).
        :return: None.
        :raises PyventusException: If the 'queue' argument is None or not an instance
            of the `Queue` class.
        """
        # Validate the queue instance.
        if queue is None or not isinstance(queue, Queue):
            raise PyventusException("The 'queue' argument must be an instance of the Queue class.")

        # Store the Redis queue and RQ options
        self.__queue: Queue = queue
        self.__options: dict[str, Any] = options if options else {}

    def __repr__(self) -> str:
        """
        Retrieve a string representation of the instance.

        :return: A string representation of the instance.
        """
        return formatted_repr(
            instance=self,
            info=attributes_repr(
                queue=self.__queue,
                options=self.__options,
            ),
        )

    @override
    def submit(self, callback: ProcessingServiceCallbackType, *args: Any, **kwargs: Any) -> None:
        # Send the callback and its arguments to Redis for asynchronous execution.
        self.__queue.enqueue(callback, *args, **kwargs, **self.__options)
