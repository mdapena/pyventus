from asyncio import Task, create_task, current_task, gather, get_running_loop, run, to_thread
from collections import deque
from collections.abc import Callable, Coroutine
from threading import Lock, local
from typing import Any, NamedTuple, ParamSpec, TypeVar

from typing_extensions import override

from ...exceptions import PyventusException
from ...utils import attributes_repr, formatted_repr, is_callable_async, is_callable_generator
from ..processing_service import ProcessingService, ProcessingServiceCallbackType

# Generic types for the guard decorator.
_GuardP = ParamSpec("_GuardP")
"""A generic type representing the names and types of the parameters of the callback provided in the guard decorator."""
_GuardR = TypeVar("_GuardR")
"""A generic type representing the return value of the callback provided in the guard decorator."""


class AsyncIOProcessingService(ProcessingService):
    """
    A processing service that utilizes the `AsyncIO` framework to handle the execution of calls.

    **Notes:**

    -   Synchronous callbacks are executed in a blocking manner if there is no active asyncio loop or
        if `force_async` is set to `False`. If `force_async` is set to `True` and an asyncio loop is
        active, these synchronous callbacks are converted to asynchronous using the `asyncio.to_thread()`
        function and are processed as background tasks within the existing asyncio loop.

    -   Asynchronous callbacks operate independently of the `force_async` parameter, as they are
        inherently asynchronous. However, their execution depends on the presence of an active asyncio
        loop. If a running asyncio loop exists, callbacks are scheduled and executed as background tasks
        within that loop. If no loop is active, a new asyncio loop is created and automatically closed
        once the callback is complete.

    -   When `enforce_submission_order` is set to `True`, new submissions are managed by a queue and
        processed sequentially within an asyncio loop. If no active asyncio loop is present, a new loop
        is initiated to handle the queue processing, and it remains open until all callbacks have been
        executed and the queue is empty, at which point it will be closed automatically. During queue
        processing, callbacks are executed as before, with the difference that they are always run
        within an existing asyncio loop and awaited (for async callbacks) instead of being run as
        background tasks.

    -   All active tasks from all instances can be retrieved through the `all_tasks()` method.
    """

    class _AsyncIOSubmission(NamedTuple):
        """A named tuple for storing relevant information related to an AsyncIO submission."""

        callback: ProcessingServiceCallbackType
        args: tuple[Any, ...]
        kwargs: dict[str, Any]

    class _AsyncIOThreadLocalCtx(local):
        """A thread-local subclass for managing AsyncIO-specific context information across different threads."""

        current_task: Task[Any] | None = None

    __thread_local_ctx: _AsyncIOThreadLocalCtx = _AsyncIOThreadLocalCtx()
    """A thread-local storage for managing AsyncIO-specific context information across different threads."""

    __global_thread_lock: Lock = Lock()
    """A global lock for synchronizing access to shared class-level resources."""

    __all_tasks: set[Task[Any]] = set()
    """A set of active background tasks managed across all instances."""

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

    @classmethod
    def all_tasks(cls) -> set[Task[Any]]:
        """
        Retrieve all active tasks from all instances.

        :return: A set of currently active tasks across all instances.
        """
        with cls.__global_thread_lock:
            return cls.__all_tasks.copy()

    @classmethod
    def guard(
        cls, cb: Callable[_GuardP, Coroutine[Any, Any, _GuardR]]
    ) -> Callable[_GuardP, Coroutine[Any, Any, _GuardR]]:
        """
        Ensure all active tasks are completed before resuming.

        This decorator prevents unfinished tasks from any instance of this class or its subclasses
        from remaining active when the function returns.

        :param cb: The coroutine callback to be guarded.
        :return: A wrapped function that waits for all active tasks to finish before returning control.
        :raises PyventusException: If the provided callback is not an async callable or is a generator.
        """

        async def wrapper(*args: _GuardP.args, **kwargs: _GuardP.kwargs) -> _GuardR:
            """
            Execute the callback and waits for all active tasks to finish before returning control.

            :param args: Positional arguments for the callback.
            :param kwargs: Keyword arguments for the callback.
            :return: The result of the callback after all tasks are complete.
            """
            result = await cb(*args, **kwargs)

            # Wait for all active tasks to complete.
            tasks: set[Task[Any]] = set()
            while True:
                with cls.__global_thread_lock:
                    if not cls.__all_tasks:
                        break

                    tasks = cls.__all_tasks.copy()
                    cls.__all_tasks.clear()

                await gather(*tasks)

            return result

        # Validate that the callback is an async function and not a generator
        if not is_callable_async(cb):
            raise PyventusException("The provided callback must be an async callable.")
        if is_callable_generator(cb):
            raise PyventusException("The provided callback cannot be a generator.")

        return wrapper

    # Attributes for the AsyncIOProcessingService
    __slots__ = ("__thread_lock", "__tasks", "__force_async", "__is_submission_queue_busy", "__submission_queue")

    def __init__(self, force_async: bool = False, enforce_submission_order: bool = False) -> None:
        """
        Initialize an instance of `AsyncIOProcessingService`.

        :param force_async: A boolean flag that determines whether to force all submitted
            callbacks to run asynchronously.
        :param enforce_submission_order: A boolean flag that determines whether to enforce the order
            of execution for submissions based on their arrival (FIFO: First In, First Out).
        :return: None
        """
        # Ensure that the 'force_async' and 'enforce_submission_order' parameters are of boolean type.
        if not isinstance(force_async, bool):
            raise PyventusException("The 'force_async' argument must be a boolean value.")
        if not isinstance(enforce_submission_order, bool):
            raise PyventusException("The 'enforce_submission_order' argument must be a boolean value.")

        # Create a thread lock to manage concurrent access to shared resources.
        self.__thread_lock: Lock = Lock()

        # Initialize a set to keep track of active background tasks.
        self.__tasks: set[Task[Any]] = set()

        # Store the value of the force_async parameter.
        self.__force_async: bool = force_async

        # Define a flag to indicate whether the submission queue is currently being processed.
        self.__is_submission_queue_busy: bool = False

        # Create a FIFO queue to maintain the order of submissions if execution order is required.
        self.__submission_queue: deque[AsyncIOProcessingService._AsyncIOSubmission] | None = (
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
                thread_lock=self.__thread_lock,
                tasks=self.__tasks,
                force_async=self.__force_async,
                is_submission_queue_busy=self.__is_submission_queue_busy,
                submission_queue=self.__submission_queue,
            ),
        )

    @property
    def _thread_lock(self) -> Lock:
        """
        Retrieve the thread lock instance.

        :return: The thread lock instance used to ensure thread-safe operations.
        """
        return self.__thread_lock

    @property
    def _tasks(self) -> set[Task[Any]]:
        """
        Retrieve the set of currently active background tasks.

        :return: A set containing the active background tasks.
        """
        return self.__tasks

    @property
    def _is_submission_queue_busy(self) -> bool:
        """
        Determine whether the submission queue is busy.

        :return: `True` if the submission queue is busy; otherwise, `False`.
        """
        return self.__is_submission_queue_busy

    @property
    def _submission_queue(self) -> deque[_AsyncIOSubmission] | None:
        """
        Retrieve the submission queue used for enforcing submission order.

        :return: The submission queue used for enforcing submission order,
            or None if submission order enforcement is not enabled.
        """
        return self.__submission_queue

    @property
    def task_name(self) -> str:
        """
        Return the name used for all background tasks created by this instance.

        :return: A task name as a string.
        """
        return f"{self.__class__.__name__}_task_{id(self)}"

    @property
    def task_count(self) -> int:
        """
        Retrieve the count of currently active background tasks.

        :return: The number of active background tasks.
        """
        with self.__thread_lock:
            return len(self.__tasks)

    @property
    def force_async(self) -> bool:
        """
        Determine whether all submitted callbacks are forced to run asynchronously.

        :return: `True` if all submitted callbacks are forced to run asynchronously; otherwise, `False`.
        """
        return self.__force_async

    @property
    def enforce_submission_order(self) -> bool:
        """
        Determine whether submission order enforcement is enabled.

        :return: `True` if submission order enforcement is enabled; otherwise, `False`.
        """
        return self.__submission_queue is not None

    def _with_thread_local_ctx(self, main: Callable[[], None]) -> Callable[[], None]:
        """
        Wrap the specified function to run in a thread-local AsyncIO context.

        :param main: The main function to be executed within the thread-local AsyncIO context.
        :return: A wrapper function that executes the main function in the thread-local AsyncIO
            context, handling initialization and cleanup.
        """
        # Get the class type to access class-level variables.
        cls: type[AsyncIOProcessingService] = type(self)

        # Get the current task for the thread context.
        cur_task: Task[Any] | None = current_task()

        def wrapper() -> None:
            try:
                # Set the thread-local context variables.
                cls.__thread_local_ctx.current_task = cur_task

                # Execute the main function.
                main()
            finally:
                # Clear the thread-local context variables
                # in case the current thread is reused.
                cls.__thread_local_ctx.current_task = None

        # Return the wrapped function.
        return wrapper

    def _remove_task(self, task: Task[Any]) -> None:
        """
        Remove a background task from the local and global tracking sets.

        :param task: The background task to be removed from the local and global sets.
        :return: None.
        """
        # Get the class type to access class-level variables.
        cls: type[AsyncIOProcessingService] = type(self)

        # Acquire locks for thread safety and remove the task.
        with self.__thread_lock, cls.__global_thread_lock:
            cls.__all_tasks.discard(task)
            self.__tasks.discard(task)

    def _add_task(self, task: Task[Any]) -> None:
        """
        Add a background task to the local and global tracking sets.

        :param task: The background task to be added to the local and global sets.
        :return: None.
        """
        # Get the class type to access class-level variables.
        cls: type[AsyncIOProcessingService] = type(self)

        # Acquire locks for thread safety and add the task.
        with self.__thread_lock, cls.__global_thread_lock:
            cls.__all_tasks.add(task)
            self.__tasks.add(task)

    def _schedule_task(self, coroutine: Coroutine[Any, Any, Any]) -> None:
        """
        Schedule a coroutine as a background task and track its execution until completion.

        :param coroutine: The coroutine to be scheduled as a background task.
        :return: None.
        """
        # Create and schedule the coroutine as a background Task.
        task: Task[Any] = create_task(coroutine, name=self.task_name)

        # Register the cleanup callback to remove the task
        # from the local and global tracking sets upon completion.
        task.add_done_callback(self._remove_task)

        # Add the task to both the local and global tracking sets.
        self._add_task(task)

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
            with self.__thread_lock:
                if not self.__submission_queue:
                    self.__is_submission_queue_busy = False  # Mark processing as complete.
                    break

                # Retrieve the next submission from the front of the queue.
                submission = self.__submission_queue.popleft()

            # Execute the submission's callback accordingly.
            if is_callable_async(submission.callback):
                await submission.callback(*submission.args, **submission.kwargs)
            elif self.__force_async:
                await to_thread(
                    self._with_thread_local_ctx(
                        main=lambda: submission.callback(*submission.args, **submission.kwargs),  # noqa: B023
                    )
                )
            else:
                submission.callback(*submission.args, **submission.kwargs)

    @override
    def submit(self, callback: ProcessingServiceCallbackType, *args: Any, **kwargs: Any) -> None:
        # Get the class type to access class-level methods.
        cls: type[AsyncIOProcessingService] = type(self)

        # Check if there is an active asyncio event loop.
        is_loop_running: bool = cls.is_loop_running()

        if not self.enforce_submission_order:
            # If submission order is not required, execute the callback
            # according to its definition and the current context (sync/async).
            if is_callable_async(callback):
                if is_loop_running:
                    self._schedule_task(callback(*args, **kwargs))
                else:
                    run(cls.guard(callback)(*args, **kwargs))  # Use guard to prevent unfinished tasks.
            elif self.__force_async and is_loop_running:
                self._schedule_task(to_thread(callback, *args, **kwargs))
            else:
                callback(*args, **kwargs)
        else:
            # If submission order must be enforced, manage the callback execution
            # based on the current context (sync/async) and the state of the queue.
            with self.__thread_lock:
                was_submission_queue_busy: bool = self.__is_submission_queue_busy

                # Add the current callback to the queue if there is a previous async execution (indicated by a
                # processing queue) or if the current context is async (indicated by an active asyncio loop), to
                # ensure the execution order is preserved. If there is no indication of previous or current async
                # execution, the context is synchronous, and the order of execution is inherently guaranteed.
                if was_submission_queue_busy or is_loop_running:
                    self.__is_submission_queue_busy = True
                    cur_task: Task[Any] | None = (
                        current_task()  # From running loop if active.
                        if is_loop_running  # Determine the current task based on execution context.
                        else cls.__thread_local_ctx.current_task  # Fallback to thread-local context if no loop.
                    )

                    # Checks if the current task's name matches the task_name of this instance. If they
                    # match, the submission originates from an inner callback execution. To maintain the
                    # execution order, it should be prepended, as it forms part of the current item being
                    # processed in the queue and must run before subsequent submissions.
                    if cur_task is not None and cur_task.get_name() == self.task_name:
                        self.__submission_queue.appendleft(  # type: ignore[union-attr]
                            AsyncIOProcessingService._AsyncIOSubmission(
                                callback=callback,
                                args=args,
                                kwargs=kwargs,
                            )
                        )
                    else:
                        self.__submission_queue.append(  # type: ignore[union-attr]
                            AsyncIOProcessingService._AsyncIOSubmission(
                                callback=callback,
                                args=args,
                                kwargs=kwargs,
                            )
                        )

            if not was_submission_queue_busy:
                if is_loop_running:
                    # Start processing the queue if it isn't already active and an event loop is running.
                    self._schedule_task(self._process_submission_queue())
                else:
                    # In a synchronous context, where there is no active queue or event loop, execute the callback
                    # in a blocking manner according to its type, as the order of execution is guaranteed.
                    if is_callable_async(callback):
                        run(cls.guard(callback)(*args, **kwargs))  # Use guard to prevent unfinished tasks.
                    else:
                        callback(*args, **kwargs)

    async def wait_for_tasks(self) -> None:
        """
        Wait for all background tasks associated with the current service to complete.

        This method ensures that any ongoing tasks are finished before proceeding.

        :return: None.
        """
        # Process all active background tasks until none remain.
        while True:
            with self.__thread_lock:
                # Exit if there are no active tasks.
                if not self.__tasks:
                    break

                # Copy current tasks and clear the registry.
                tasks: set[Task[Any]] = self.__tasks.copy()
                self.__tasks.clear()

            # Await the completion of all tasks.
            await gather(*tasks)
