import asyncio
from asyncio import Future
from typing import Set, Type, Any, cast, List

from src.pyventus.core.constants import StdOutColors
from src.pyventus.emitters import EventEmitter
from src.pyventus.linkers import EventLinker
from src.pyventus.listeners import EventListener


class AsyncIOEventEmitter(EventEmitter):
    """
    A class that inherits from `EventEmitter` and uses the `AsyncIO` framework to handle
    the execution of the event listener callbacks.

    **Asynchronous Execution**: In an asynchronous context where an event loop is already
    running, the event callbacks are scheduled and processed concurrently on that existing
    loop. If the event loop is closed before all callbacks complete, any remaining scheduled
    tasks will be canceled.

    **Synchronous Execution**: In a synchronous context where no event loop is active, a new
    event loop is started and subsequently closed by the `asyncio.run()` method. Within this
    loop, it concurrently executes the event listener callbacks using the `asyncio.gather()`
    method. The loop then waits for all scheduled callbacks to finish before closing. This
    preserves synchronous execution while still gaining the benefits of the concurrent
    execution.

    **Examples**:

    ```Python
    # Asynchronous Execution.
    async def async_context(event_emitter: EventEmitter = AsyncIOEventEmitter()) -> None:
        # The event listeners are handled by the already running 
        # asyncio event loop, and the execution does not block.
        event_emitter.emit(Event())
    ```

    ```Python
    # Synchronous Execution.
    def sync_context(event_emitter: EventEmitter = AsyncIOEventEmitter()) -> None:
        # The event listeners are handled in a new asyncio event
        # loop, but it blocks execution until all tasks complete.
        event_emitter.emit(Event())
    ```
    """

    @property
    def __is_loop_running(self) -> bool:
        """
        Check if an asyncio event loop is currently running.

        This method checks if there is a current asyncio event loop running by calling
        `asyncio.get_running_loop()`.If no exception is raised, it means there is a
        running loop and `True` is returned. If a `RuntimeError` is  raised, it
        means there is no running loop and `False` is returned.

        :return: `True` if there is a current running event loop, `False` otherwise
        """
        try:
            asyncio.get_running_loop()
            return True
        except RuntimeError:
            return False

    def __init__(self, event_linker: Type[EventLinker] = EventLinker, debug_mode: bool | None = None):
        """
        Initializes an instance of the `AsyncIOEventEmitter` class.
        :param event_linker: Specifies the type of event linker to use for associating
            events with their respective event listeners. Defaults to `EventLinker`.
        :param debug_mode: Specifies the debug mode for the subclass logger. If `None`,
            it is determined based on the execution environment.
        """
        # Call the parent class' __init__ method to set up the event linker
        super().__init__(event_linker=event_linker, debug_mode=debug_mode)

        # Initialize the set of background futures
        self._background_futures: Set[Future] = set()

    def _execute(self, event_listeners: List[EventListener], *args: Any, **kwargs: Any) -> None:
        """
        Executes the callback function of each event listener asynchronously using the
        `AsyncIO` framework. The positional arguments provided as `*args` are passed to
        the callback function, along with any keyword arguments provided as `**kwargs`.

        :param event_listeners: List of event listeners to be executed.
        :param args: Positional arguments to pass to the callback functions.
        :param kwargs: Keyword arguments to pass to the callback functions.
        :return: None
        """
        # Check if AsyncIO event loop is running
        is_loop_running: bool = self.__is_loop_running

        # Log the execution context, if debug mode is enabled
        if self._logger.debug_enabled:
            self._logger.debug(action=f"Running:", msg=f"{'Async' if is_loop_running else 'Sync'} context")

        if is_loop_running:
            # Schedule the event listener callbacks
            self.__ensure_futures(event_listeners, *args, **kwargs)
        else:
            async def _inner_callback():
                self.__ensure_futures(event_listeners, *args, **kwargs)

                await asyncio.gather(
                    *asyncio.all_tasks().difference({asyncio.current_task()}),
                    return_exceptions=True
                )

            # Run the event listener callbacks concurrently in a synchronous manner
            asyncio.run(_inner_callback())

    def __ensure_futures(self, event_listeners: List[EventListener], *args: Any, **kwargs: Any) -> None:
        """
        Schedules the event listener callbacks in the running loop as a future.

        :param event_listeners: List of event listeners to be executed.
        :param args: Positional arguments to pass to the callback functions.
        :param kwargs: Keyword arguments to pass to the callback functions.
        :return: None
        """

        def _done_callback(fut: Future):
            # Remove the Future from the set of background futures
            self._background_futures.remove(fut)

            # If the Future was cancelled, return without further execution
            if fut.cancelled():
                return

            # Get the exception, if any, from the Future
            exception: Exception = cast(Exception, fut.exception())

            # If an exception occurred during execution, emit it as an event
            if exception:
                # Log the exception with error level
                self._logger.error(
                    action="Exception:",
                    msg=f"[{event_listener}] {StdOutColors.RED}Errors:{StdOutColors.DEFAULT} {exception}"
                )

                if len(args) == 0 or not issubclass(args[0].__class__, Exception):
                    # Emit the exception as an event if the previous arguments were not exceptions
                    self.emit(exception)
                else:
                    # Log the recursive exception with error level
                    self._logger.error(
                        action="Recursive Exception:",
                        msg=f"An error occurred while handling a previous exception. Propagating the exception...",
                    )

                    # Propagate recursive exception
                    raise exception

        for event_listener in event_listeners:
            # Schedule the event listener callback in the running loop as a future
            future: Future = asyncio.ensure_future(event_listener(*args, **kwargs))
            future.add_done_callback(_done_callback)

            # Add the Future to the set of background futures
            self._background_futures.add(future)

            # Log the execution of the listener, if debug mode is enabled
            if self._logger.debug_enabled:
                self._logger.debug(
                    action="Executing:",
                    msg=f"[{event_listener}] "
                        f"{StdOutColors.PURPLE}*args:{StdOutColors.DEFAULT} {args} "
                        f"{StdOutColors.PURPLE}**kwargs:{StdOutColors.DEFAULT} {kwargs}"
                )
