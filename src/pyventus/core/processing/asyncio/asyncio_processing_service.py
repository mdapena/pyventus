from asyncio import Task, create_task, gather, get_running_loop, run
from typing import Any

from typing_extensions import override

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
    """

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
    __slots__ = ("__background_tasks",)

    def __init__(self) -> None:
        """
        Initialize an instance of `AsyncIOProcessingService`.

        :return: None.
        """
        # Initialize the set of background tasks
        self.__background_tasks: set[Task[Any]] = set()

    def __repr__(self) -> str:
        """
        Retrieve a string representation of the instance.

        :return: A string representation of the instance.
        """
        return formatted_repr(
            instance=self,
            info=attributes_repr(
                background_tasks=self.__background_tasks,
            ),
        )

    @override
    def submit(self, callback: ProcessingServiceCallbackType, *args: Any, **kwargs: Any) -> None:
        # Check if the callback is asynchronous and execute accordingly.
        if is_callable_async(callback):
            # Check if there is an active event loop.
            loop_running: bool = AsyncIOProcessingService.is_loop_running()

            if loop_running:
                # Schedule the callback in the running loop as a background task.
                task: Task[Any] = create_task(callback(*args, **kwargs))

                # Add a callback to remove the Task from the set of background tasks upon completion.
                task.add_done_callback(self.__background_tasks.discard)

                # Add the Task to the set of background tasks.
                self.__background_tasks.add(task)
            else:
                # Execute the callback in a blocking manner if no event loop is active.
                run(callback(*args, **kwargs))
        else:
            # Execute the callback directly if it is not an asynchronous call.
            callback(*args, **kwargs)

    async def wait_for_tasks(self) -> None:
        """
        Wait for all background tasks associated with the current service to complete.

        This method ensures that any ongoing tasks are finished before proceeding.

        :return: None.
        """
        # Retrieve the current set of background tasks and clear the registry.
        tasks: set[Task[Any]] = self.__background_tasks.copy()
        self.__background_tasks.clear()

        # Await the completion of all background tasks.
        await gather(*tasks)
