from asyncio import run
from concurrent.futures import Executor
from types import TracebackType
from typing import Any

from typing_extensions import Self, override

from ...exceptions import PyventusException
from ...utils import attributes_repr, formatted_repr, is_callable_async
from ..processing_service import ProcessingService, ProcessingServiceCallbackType


class ExecutorProcessingService(ProcessingService):
    """
    A processing service that utilizes the `concurrent.futures.Executor` to handle the execution of calls.

    **Notes:**

    -   This service uses the `concurrent.futures.Executor` for processing the callbacks' execution. It
        can work with either a `ThreadPoolExecutor` for thread-based execution or a `ProcessPoolExecutor`
        for process-based execution.

    -   Synchronous callbacks are executed in a blocking manner inside the executor, while asynchronous
        callbacks are processed within a new asyncio event loop using the `asyncio.run()` function.

    -   When using this service, it is important to properly manage the underlying `Executor`. Once
        there are no more calls to be processed through the given executor, it's important to invoke
        the `shutdown()` method to signal the executor to free any resources for pending futures. You
        can avoid the need to call this method explicitly by using the `with` statement, which
        automatically shuts down the `Executor`.
    """

    @staticmethod
    def _execute(callback: ProcessingServiceCallbackType, args: tuple[Any, ...], kwargs: dict[str, Any]) -> None:
        """
        Execute the provided callback with the given arguments.

        This method is intended to be used within the executor to execute the callback.

        :param callback: The callback to be executed.
        :param args: Positional arguments to be passed to the callback.
        :param kwargs: Keyword arguments to be passed to the callback.
        :return: None.
        """
        # Check if the callback is asynchronous and execute accordingly.
        if is_callable_async(callback):
            # Run the async callback in a new asyncio event loop.
            run(callback(*args, **kwargs))
        else:
            # Run the sync callback directly with the provided arguments.
            callback(*args, **kwargs)

    # Attributes for the ExecutorProcessingService.
    __slots__ = ("__executor",)

    def __init__(self, executor: Executor) -> None:
        """
        Initialize an instance of `ExecutorProcessingService`.

        :param executor: The executor object used to handle the callbacks' execution.
        :return: None.
        :raises PyventusException: If the executor is not provided or is not an instance of `Executor`.
        """
        # Validate the executor instance.
        if executor is None or not isinstance(executor, Executor):
            raise PyventusException("The 'executor' argument must be an instance of Executor.")

        # Store the executor instance.
        self.__executor: Executor = executor

    def __repr__(self) -> str:
        """
        Retrieve a string representation of the instance.

        :return: A string representation of the instance.
        """
        return formatted_repr(
            instance=self,
            info=attributes_repr(
                executor=self.__executor,
            ),
        )

    @override
    def submit(self, callback: ProcessingServiceCallbackType, *args: Any, **kwargs: Any) -> None:
        # Submit the callback to the executor along with its arguments.
        self.__executor.submit(self.__class__._execute, callback, args, kwargs)

    def shutdown(self, wait: bool = True, cancel_futures: bool = False) -> None:
        """
        Shut down the executor and release any resources it is using.

        :param wait: A boolean indicating whether to wait for the currently pending futures
            to complete before shutting down.
        :param cancel_futures: A boolean indicating whether to cancel any pending futures.
        :return: None.
        """
        self.__executor.shutdown(wait=wait, cancel_futures=cancel_futures)

    def __enter__(self) -> Self:
        """
        Return the current instance of `ExecutorProcessingService` for context management.

        :return: The current instance of `ExecutorProcessingService`.
        """
        return self

    def __exit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        """
        Clean up the executor resources when exiting the context.

        :param exc_type: The exception type, if any.
        :param exc_val: The exception value, if any.
        :param exc_tb: The traceback information, if any.
        :return: None.
        """
        self.shutdown(wait=True, cancel_futures=False)
