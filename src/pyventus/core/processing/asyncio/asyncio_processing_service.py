from asyncio import Task, create_task, gather, get_running_loop, run
from collections import deque
from collections.abc import Coroutine
from threading import Lock
from typing import Any, NamedTuple

from typing_extensions import override

from ...exceptions import PyventusException
from ...utils import attributes_repr, formatted_repr, is_callable_async
from ..processing_service import ProcessingService, ProcessingServiceCallbackType


class AsyncIOProcessingService(ProcessingService):
    """
    A processing service that utilizes the `AsyncIO` framework to handle the execution of calls.

    **Notes:**

    -   When the provided callback is a synchronous call, it will be executed in a blocking manner, regardless
        of whether an event loop is active. However, if the synchronous callback involves I/O or non-CPU-bound
        operations, it can be offloaded to a thread pool using `asyncio.to_thread()` from the `AsyncIO` framework.

    -   When the provided callback is an asynchronous call and is submitted in a context where an event loop is
        already running, the callback is scheduled and processed on that existing loop. If the event loop exits
        before all calls are completed, any remaining scheduled calls will be canceled.

    -   When the provided callback is an asynchronous call and is submitted in a context where no event loop is
        active, a new event loop is started and subsequently closed by the `asyncio.run()` method. Within this
        loop, the callback is executed, and the loop waits for all scheduled tasks to finish before closing.

    -   When `enforce_submission_order` is `True`, new submissions are managed by a queue and processed
        sequentially within an asyncio loop. If there is no active asyncio loop available, a new loop is
        generated specifically to handle the queue processing. This newly created loop will remain open until
        all callbacks have been executed and the queue is empty, at which point it will be automatically closed.
        Synchronous callbacks are enqueued and executed directly in a blocking manner, while asynchronous callbacks
        are also queued, executed immediately, and awaited to preserve the correct order of execution.
    """

    class _AsyncIOSubmission(NamedTuple):
        """A named tuple for storing relevant information related to an AsyncIO submission."""

        callback: ProcessingServiceCallbackType
        args: tuple[Any, ...]
        kwargs: dict[str, Any]

    @staticmethod
    def is_loop_running() -> bool:
        """
        Determine whether there is currently an active `AsyncIO` event loop.

        :return: `True` if an event loop is running; `False` otherwise.
        """
        try:
            get_running_loop()
            return True
        except RuntimeError:
            return False

    # Attributes for the AsyncIOProcessingService
    __slots__ = ("_thread_lock", "_background_tasks", "_is_submission_queue_busy", "_submission_queue")

    def __init__(self, enforce_submission_order: bool = False) -> None:
        """
        Initialize an instance of `AsyncIOProcessingService`.

        :param force_submission_order: A boolean flag that determines whether to enforce the order
            of execution for submissions based on their arrival (FIFO: First In, First Out).
        :return: None
        """
        # Ensure the 'enforce_submission_order' parameter is a boolean
        if not isinstance(enforce_submission_order, bool):
            raise PyventusException("The 'enforce_submission_order' argument must be a boolean value.")

        # Create a thread lock to manage concurrent access to shared resources.
        self._thread_lock: Lock = Lock()

        # Initialize a set to keep track of active background tasks.
        self._background_tasks: set[Task[Any]] = set()

        # Define a flag to indicate whether the submission queue is currently being processed.
        self._is_submission_queue_busy: bool = False

        # Create a FIFO queue to maintain the order of submissions if execution order is enforced.
        self._submission_queue: deque[AsyncIOProcessingService._AsyncIOSubmission] | None = (
            deque[AsyncIOProcessingService._AsyncIOSubmission]() if enforce_submission_order else None
        )

    def __repr__(self) -> str:
        """
        Retrieve a string representation of the instance.

        :return: A string representation of the instance.
        """
        return formatted_repr(
            instance=self,
            info=attributes_repr(
                thread_lock=self._thread_lock,
                background_tasks=self._background_tasks,
                is_submission_queue_busy=self._is_submission_queue_busy,
                submission_queue=self._submission_queue,
            ),
        )

    def _remove_background_task(self, task: Task[Any]) -> None:
        """
        Remove a background task from the tracking set.

        :param task: The background task to remove from the set.
        :return: None.
        """
        with self._thread_lock:
            self._background_tasks.discard(task)

    def _schedule_background_task(self, coroutine: Coroutine[Any, Any, Any]) -> None:
        """
        Schedule a coroutine as a background `Task` and track its execution until completion.

        :param coroutine: The coroutine to be scheduled as a background Task.
        :return: None.
        """
        # Create and schedule the coroutine as a background Task.
        task: Task[Any] = create_task(coroutine)

        # Register the cleanup callback to remove the Task
        # from the set of background tasks upon completion.
        task.add_done_callback(self._remove_background_task)

        # Add the Task to the set of active background
        # tasks under lock for thread-safety.
        with self._thread_lock:
            self._background_tasks.add(task)

    async def _process_submission_queue(self) -> None:
        """
        Process each AsyncIO submission in the queue in FIFO order.

        :return: None.
        """
        # Initialize a variable to hold the current submission being processed.
        submission: AsyncIOProcessingService._AsyncIOSubmission | None = None

        # Pop and process submissions with thread
        # safety until the queue is empty.
        while True:
            with self._thread_lock:
                if not self._submission_queue:
                    self._is_submission_queue_busy = False  # Mark processing as complete.
                    break

                # Retrieve the next submission from the front of the queue.
                submission = self._submission_queue.popleft()

            # Execute the submission's callback accordingly.
            if is_callable_async(submission.callback):
                await submission.callback(*submission.args, **submission.kwargs)
            else:
                submission.callback(*submission.args, **submission.kwargs)

    @override
    def submit(self, callback: ProcessingServiceCallbackType, *args: Any, **kwargs: Any) -> None:
        # Check if there is an active asyncio event loop.
        is_loop_running: bool = AsyncIOProcessingService.is_loop_running()

        # Process the callback based on whether a submission queue exists,
        # which determines if the order of execution should be enforced.
        if self._submission_queue is None:
            # If enforcing the order of execution is not required, process the
            # callback according to its definition and the current context.
            if is_callable_async(callback):
                if is_loop_running:
                    self._schedule_background_task(callback(*args, **kwargs))
                else:
                    run(callback(*args, **kwargs))
            else:
                callback(*args, **kwargs)
        else:
            # If the order of execution should be enforced, use the submission
            # queue to manage the submission order and its processing.
            with self._thread_lock:
                was_submission_queue_busy: bool = self._is_submission_queue_busy
                self._is_submission_queue_busy = True
                self._submission_queue.append(
                    AsyncIOProcessingService._AsyncIOSubmission(
                        callback=callback,
                        args=args,
                        kwargs=kwargs,
                    )
                )

            # Start processing the queue if it wasn't already active.
            if not was_submission_queue_busy:
                if is_loop_running:
                    self._schedule_background_task(self._process_submission_queue())
                else:
                    run(self._process_submission_queue())

    async def wait_for_tasks(self) -> None:
        """
        Wait for all background tasks associated with the current service to complete.

        This method ensures that any ongoing tasks are finished before proceeding.

        :return: None.
        """
        # Retrieve the current set of background tasks and clear the registry.
        with self._thread_lock:
            tasks: set[Task[Any]] = self._background_tasks.copy()
            self._background_tasks.clear()

        # Await the completion of all background tasks.
        await gather(*tasks)
