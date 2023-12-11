import asyncio
from concurrent.futures import Executor, ThreadPoolExecutor
from types import TracebackType
from typing import Any, Type, List

from ...core.exceptions import PyventusException
from ...emitters import EventEmitter
from ...handlers import EventHandler
from ...linkers import EventLinker


class ExecutorEventEmitter(EventEmitter):
    """
    An event emitter that executes event handlers concurrently using an `Executor`.

    This class utilizes the `concurrent.futures` Executor base class to handle asynchronous
    execution of event handlers. It can work with either `ThreadPoolExecutor` for thread-based
    execution or `ProcessPoolExecutor` for process-based execution.

    By inheriting from `EventEmitter` and utilizing the `Executor` interface, this class
    provides a consistent way to emit events and execute handlers concurrently in either
    threads or processes. This allows choosing the optimal execution approach based on
    application needs.

    **Note:** It is important to properly manage the underlying `Executor` when using
    this event emitter. Once finished emitting events, call the `shutdown()` method to
    signal the executor to free any resources for pending futures.

    - You can avoid having to call this method explicitly if you use the `with` statement,
      which will shut down the `Executor` (waiting as if `Executor.shutdown()` were called
      with `wait` set to `True`).

    **Example:** You can use this event emitter in both synchronous and asynchronous
    contexts.

    ```Python
    from pyventus import ExecutorEventEmitter, EventLinker


    @EventLinker.on('StringEvent')
    async def event_callback():
        print("Event received!")


    def main():
        with ExecutorEventEmitter() as event_emitter:
            event_emitter.emit('StringEvent')
            event_emitter.emit('StringEvent')


    main()
    ```

    ```Python
    from pyventus import ExecutorEventEmitter, EventLinker


    @EventLinker.on('StringEvent')
    async def event_callback():
        print("Event received!")


    async def main():
        with ExecutorEventEmitter() as event_emitter:
            event_emitter.emit('StringEvent')
            event_emitter.emit('StringEvent')


    asyncio.run(main())
    ```
    """

    def __init__(
        self,
        executor: Executor = ThreadPoolExecutor(),
        event_linker: Type[EventLinker] = EventLinker,
        debug_mode: bool | None = None,
    ):
        """
        Initializes an instance of the `ExecutorEventEmitter` class.
        :param executor: The executor object used for executing event handlers. Defaults
            to `ThreadPoolExecutor()`.
        :param event_linker: Specifies the type of event linker to use for associating
            events with their respective event handlers. Defaults to `EventLinker`.
        :param debug_mode: Specifies the debug mode for the subclass logger. If `None`,
            it is determined based on the execution environment.
        """
        # Call the parent class' __init__ method to set up the event linker
        super().__init__(event_linker=event_linker, debug_mode=debug_mode)

        # Validate the executor argument
        if executor is None or not issubclass(executor.__class__, Executor):
            raise PyventusException("The 'executor' argument must be a valid executor.")

        # Set the executor object reference
        self._executor: Executor = executor

    def __enter__(self) -> "ExecutorEventEmitter":
        """
        Returns the instance of `ExecutorEventEmitter` for context management.
        :return: The instance of `ExecutorEventEmitter`.
        """
        return self

    def __exit__(
        self, exc_type: Type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        """
        Cleans up the executor resources when exiting the context.
        :param exc_type: The exception type, if any.
        :param exc_val: The exception value, if any.
        :param exc_tb: The traceback information, if any.
        :return: A boolean indicating whether to propagate any exception or not.
        """
        self.shutdown(wait=True)

    def shutdown(self, wait: bool = True, cancel_futures: bool = False) -> None:
        """
        Shuts down the executor and frees any resources it is using.
        :param wait: A boolean indicating whether to wait for the currently pending futures
            to complete before shutting down.
        :param cancel_futures: A boolean indicating whether to cancel any pending futures.
        :return: None
        """
        self._executor.shutdown(wait=wait, cancel_futures=cancel_futures)

    def _execute(self, event_handlers: List[EventHandler], /, *args: Any, **kwargs: Any) -> None:
        # Run the event handlers
        # concurrently in the executor
        self._executor.submit(ExecutorEventEmitter.__execution_callback, event_handlers, *args, **kwargs)

    @staticmethod
    def __execution_callback(event_handlers: List[EventHandler], /, *args: Any, **kwargs: Any) -> None:
        """
        Executes a list of event handlers concurrently using `asyncio.gather()`.
        This method serves as a callback to be passed to the executor.
        :param event_handlers: A list of event handlers.
        :param args: Positional arguments.
        :param kwargs: Keyword arguments.
        :return: None
        """

        async def _inner_callback() -> None:
            """Inner callback to be submitted to `asyncio.run()`."""

            await asyncio.gather(*[event_handler(*args, **kwargs) for event_handler in event_handlers])

        asyncio.run(_inner_callback())
