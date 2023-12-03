import asyncio
from asyncio import Future
from concurrent.futures import Executor, ThreadPoolExecutor
from types import TracebackType
from typing import Any, Type, cast, List

from src.pyventus.core.constants import StdOutColors
from src.pyventus.emitters import EventEmitter, EmittableEventType
from src.pyventus.linkers import EventLinker
from src.pyventus.listeners import EventListener


class ExecutorEventEmitter(EventEmitter):
    """
    An event emitter that executes event listener callbacks concurrently using an `Executor`.

    This class utilizes the `concurrent.futures` Executor base class to handle asynchronous
    execution of event listener callbacks. It can work with either `ThreadPoolExecutor` for
    thread-based execution or `ProcessPoolExecutor` for process-based execution.

    By inheriting from `EventEmitter` and utilizing the `Executor` interface, this class
    provides a consistent way to emit events and execute listeners concurrently in either
    threads or processes. This allows choosing the optimal execution approach based on
    application requirements.

    **Note:** When used, all listener callbacks, including those that arise during emission,
    will be executed concurrently via the underlying `Executor`.

    **Important:** It is important to properly manage the underlying `Executor` when using
    this event emitter. Once finished emitting events, call the `shutdown()` method to
    signal the executor to free any resources for pending futures.

    You can avoid having to call this method explicitly if you use the `with` statement,
    which will shut down the `Executor` (waiting as if `Executor.shutdown()` were called
    with `wait` set to `True`).

    **Example:** You can use this event emitter in both synchronous and asynchronous
    contexts.

    ```Python
    import asyncio

    from pyventus import ExecutorEventEmitter, EventLinker


    @EventLinker.on('StringEvent')
    async def event_callback():
        await asyncio.sleep(1)
        print("Event received!")


    def main():
        with ExecutorEventEmitter() as event_emitter:
            event_emitter.emit('StringEvent')
            event_emitter.emit('StringEvent')


    main()
    ```

    ```Python
    import asyncio

    from pyventus import ExecutorEventEmitter, EventLinker


    @EventLinker.on('StringEvent')
    async def event_callback():
        await asyncio.sleep(1)
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
        :param executor: The executor object used for executing event listener callbacks.
            Defaults to `ThreadPoolExecutor()`.
        :param event_linker: Specifies the type of event linker to use for associating
            events with their respective event listeners. Defaults to `EventLinker`.
        :param debug_mode: Specifies the debug mode for the subclass logger. If `None`,
            it is determined based on the execution environment.
        """
        # Call the parent class' __init__ method to set up the event linker
        super().__init__(event_linker=event_linker, debug_mode=debug_mode)

        # Set the executor object reference
        self._executor: Executor = executor

    def __enter__(self) -> 'ExecutorEventEmitter':
        """
        Returns the instance of `ExecutorEventEmitter` for context management.
        :return: The instance of `ExecutorEventEmitter`.
        """
        return self

    def __exit__(self, exc_type: Type[BaseException], exc_value: BaseException, traceback: TracebackType) -> bool:
        """
        Cleans up the executor resources when exiting the context.
        :param exc_type: The exception type, if any.
        :param exc_value: The exception value, if any.
        :param traceback: The traceback information, if any.
        :return: A boolean indicating whether to propagate any exception or not.
        """
        self.shutdown(wait=True)
        return False

    def shutdown(self, wait: bool = True, cancel_futures: bool = False) -> None:
        """
        Shuts down the executor and frees any resources it is using.
        :param wait: A boolean indicating whether to wait for the currently pending futures
            to complete before shutting down.
        :param cancel_futures: A boolean indicating whether to cancel any pending futures.
        :return: None
        """
        self._executor.shutdown(wait=wait, cancel_futures=cancel_futures)

    def emit(self, event: EmittableEventType, *args: Any, **kwargs: Any) -> None:
        # Wraps the actual emit in an async task that is submitted to the
        # executor. This ensures listeners are executed concurrently.
        # Any exceptions are gathered before returning.

        # Store reference to superclass' emit method
        super_ref: EventEmitter = super()

        async def _inner_callback():
            """ Inner callback function submitted to executor. """

            # Emit event using superclass method
            super_ref.emit(event, *args, **kwargs)

            # Gather completion of all tasks except this one
            await asyncio.gather(
                *asyncio.all_tasks().difference({asyncio.current_task()}),
                return_exceptions=True
            )

        # Submit inner callback to executor
        self._executor.submit(asyncio.run, _inner_callback())

    def _execute(self, event_listeners: List[EventListener], *args: Any, **kwargs: Any) -> None:
        # Store super's emit method for handling exceptions
        super_ref: EventEmitter = super()

        def _done_callback(fut: Future):
            # Check if future was cancelled
            if fut.cancelled():
                return

            # Get exception if any
            exception: Exception = cast(Exception, fut.exception())

            # No exception, return
            if not exception:
                return

            # Check args to see if event was already an Exception
            self._logger.error(
                action="Exception:",
                msg=f"[{event_listener}] {StdOutColors.RED}Errors:{StdOutColors.DEFAULT} {exception}"
            )

            if len(args) == 0 or not issubclass(args[0].__class__, Exception):
                # If the event was not already an exception, emit a new exception event.
                # We use the super method to emit the exception event because we are
                # already in the context of the executor, and there is no need to
                # submit the emit method to the executor again.
                super_ref.emit(exception)
            else:
                # Log the recursive exception with error level
                self._logger.error(action="Recursive Exception:", msg=f"Propagating...")

                # Propagate recursive exception
                raise exception

        for event_listener in event_listeners:
            # Schedule the event listener callback in the running loop as a future
            future: Future = asyncio.ensure_future(event_listener(*args, **kwargs))
            future.add_done_callback(_done_callback)

            # Log the execution of the listener, if debug mode is enabled
            if self._logger.debug_enabled:
                self._logger.debug(
                    action="Executing:",
                    msg=f"[{event_listener}] "
                        f"{StdOutColors.PURPLE}*args:{StdOutColors.DEFAULT} {args} "
                        f"{StdOutColors.PURPLE}**kwargs:{StdOutColors.DEFAULT} {kwargs}"
                )
