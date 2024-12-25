from collections.abc import AsyncGenerator, Awaitable, Callable, Generator
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from types import TracebackType
from typing import Any, Generic, TypeAlias, TypeVar

from typing_extensions import Self, override

from ...core.exceptions import PyventusException
from ...core.processing.asyncio import AsyncIOProcessingService
from ...core.utils import CallableWrapper, attributes_repr, formatted_repr
from .observable import Completed, Observable

_OutT = TypeVar("_OutT", covariant=True)
"""A generic type representing the value that will be streamed through the ObservableTask."""

ObservableTaskCallbackReturnType: TypeAlias = (
    _OutT | Awaitable[_OutT] | Generator[_OutT, None, None] | AsyncGenerator[_OutT, None]
)
"""Type alias for the return type of the ObservableTask's callback."""

ObservableTaskCallbackType: TypeAlias = Callable[..., ObservableTaskCallbackReturnType[_OutT]]
"""Type alias for the ObservableTask's callback."""


class ObservableTask(Generic[_OutT], Observable[_OutT]):
    """
    An observable subclass that encapsulates a unit of work and offers a mechanism for streaming its results reactively.

    **Notes:**

    -   The `ObservableTask` class facilitates deferred execution of tasks, allowing subscribers to receive results
        incrementally as they become available.

    -   This class supports the encapsulation of tasks that can be either standard functions or methods, as well as
        generator functions.

    -   Results are streamed to subscribers in a lazy manner, meaning they are produced on demand rather than all
        at once.
    """

    # Attributes for the ObservableTask
    __slots__ = ("__callback", "__args", "__kwargs", "__processing_service")

    def __init__(
        self,
        callback: ObservableTaskCallbackType[_OutT],
        args: tuple[Any, ...] | None = None,
        kwargs: dict[str, Any] | None = None,
        debug: bool | None = None,
    ) -> None:
        """
        Initialize an instance of `ObservableTask`.

        :param callback: The callback to be encapsulated and made observable.
        :param args: Positional arguments to be passed to the callback.
        :param kwargs: Keyword arguments to be passed to the callback.
        :param debug: Specifies the debug mode for the logger. If `None`,
            the mode is determined based on the execution environment.
        """
        # Initialize the base Observable class with the given debug value.
        super().__init__(debug=debug)

        # Validate the args argument.
        if args and not isinstance(args, tuple):
            raise PyventusException("The 'args' argument must be a tuple.")

        # Validate the kwargs argument.
        if kwargs and not isinstance(kwargs, dict):
            raise PyventusException("The 'kwargs' argument must be a dictionary.")

        # Wrap and set the callback along with its arguments.
        self.__callback = CallableWrapper[..., _OutT](callback, force_async=False)
        self.__args: tuple[Any, ...] = args if args else ()
        self.__kwargs: dict[str, Any] = kwargs if kwargs else {}

        # Set up an AsyncIO processing service for handling the callback execution.
        self.__processing_service: AsyncIOProcessingService = AsyncIOProcessingService()

    @override
    def __repr__(self) -> str:
        return formatted_repr(
            instance=self,
            info=(
                attributes_repr(
                    callback=self.__callback,
                    args=self.__args,
                    kwargs=self.__kwargs,
                    processing_service=self.__processing_service,
                )
                + f", {super().__repr__()}"
            ),
        )

    async def __execute(self) -> None:
        """
        Execute the main callback and emit results to subscribers.

        This method invokes the callback of the ObservableTask with
        the provided arguments and emits results to subscribers in
        a lazy-push manner.

        :return: None.
        """
        try:
            if self.__callback.is_generator:
                # Stream values from the generator callback and emit each value to subscribers.
                async for g_value in self.__callback.stream(*self.__args, **self.__kwargs):
                    await self._emit_next(value=g_value)
            else:
                # Execute the regular callback and emit the result to subscribers.
                r_value: _OutT = await self.__callback.execute(*self.__args, **self.__kwargs)
                await self._emit_next(value=r_value)

                # Indicate that the callback execution is complete.
                raise Completed from None
        except Observable.Completed:
            # Notify subscribers that the observable
            # has completed emitting values.
            await self._emit_complete()
        except Exception as exception:
            # Notify subscribers of any errors
            # encountered during execution.
            await self._emit_error(exception)

    async def wait_for_tasks(self) -> None:
        """
        Wait for all background tasks associated with the `ObservableTask` to complete.

        It ensures that any ongoing tasks are finished before proceeding.

        :return: None.
        """
        # Await the completion of all background tasks.
        await self.__processing_service.wait_for_tasks()

    @contextmanager
    def to_thread(
        self, executor: ThreadPoolExecutor | None = None, shutdown: bool = False
    ) -> Generator[Self, None, None]:
        """
        Configure the execution context block for processing the `ObservableTask` using a thread-based executor.

        This method allows the `ObservableTask` to be executed in a separate thread, utilizing the specified
        executor. Upon exiting the context, the observable task is executed within the provided executor.

        :param executor: An optional `ThreadPoolExecutor` instance for executing the `ObservableTask`.
            If `None`, a new `ThreadPoolExecutor` with default settings will be created and automatically
            shut down after execution.
        :param shutdown: A flag indicating whether to shut down the specified executor upon exiting the
            context. If the executor is `None`, the new executor will always be shut down when the
            context is exited.
        :return: The current ObservableTask instance.
        """
        # Yield the current ObservableTask
        # instance for use within the context.
        yield self

        if executor:
            # Execute the observable task using the provided executor.
            self(executor=executor)

            # Shut down the provided executor if the shutdown flag is set to True.
            if shutdown:
                executor.shutdown()
        else:
            # Create a new ThreadPoolExecutor, execute the observable task
            # within that new thread, and shut it down after execution.
            new_executor = ThreadPoolExecutor()
            self(executor=new_executor)
            new_executor.shutdown()

    def __enter__(self: Self) -> Self:
        """
        Enter the execution context of the observable task.

        This method facilitates interaction with the observable task object
        and ensures that the task is executed upon exiting the context block.

        :return: The observable task instance.
        """
        return self

    def __exit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        """
        Exit the execution context of the observable task.

        This method triggers the execution of the observable task
        upon exiting the context block.

        :param exc_type: The type of the raised exception, if any.
        :param exc_val: The raised exception object, if any.
        :param exc_tb: The traceback information, if any.
        :return: None.
        """
        # Execute the observable task.
        self(executor=None)

    def __call__(self, executor: ThreadPoolExecutor | None = None) -> None:
        """
        Execute the current `ObservableTask`.

        **Notes:**

        -   When a thread-based executor is provided, the execution of
            the `ObservableTask` is submitted to that thread.

        -   If no executor is provided, the execution is submitted to
            the AsyncIO processing service of the current `ObservableTask`
            instance.

        -   The execution behavior within the AsyncIO processing service
            depends on whether an AsyncIO event loop is running. For more
            information, refer to the `AsyncIOProcessingService`.

        :param executor: An optional thread-based executor instance for
            processing the `ObservableTask`'s execution.
        :return: None.
        """
        if executor is None:
            # Submit the ObservableTask's execution to the AsyncIO processing service.
            self.__processing_service.submit(self.__execute)
        else:
            # Ensure the provided executor is a ThreadPoolExecutor instance.
            if not isinstance(executor, ThreadPoolExecutor):
                raise PyventusException("The 'executor' argument must be an instance of ThreadPoolExecutor.")

            # Submit the ObservableTask's execution to the specified thread-based executor.
            executor.submit(self.__processing_service.submit, self.__execute)
