import asyncio
from asyncio import Future
from typing import Set, Type

from ...emitters import EventEmitter
from ...linkers import EventLinker


class AsyncIOEventEmitter(EventEmitter):
    """
    A class that inherits from `EventEmitter` and uses the `AsyncIO` framework to handle
    the execution of the event handlers.

    **Asynchronous Execution**: In an asynchronous context where an event loop is already
    running, the event task is scheduled and processed on that existing loop. If the
    event loop is closed before all callbacks complete, any remaining scheduled
    callback will be canceled.

    **Synchronous Execution**: In a synchronous context where no event loop is active, a new event
    loop is started and subsequently closed by the `asyncio.run()` method. Within this loop, it
    executes the event task. The loop then waits for all scheduled callbacks to finish before
    closing. This preserves synchronous execution while still gaining the benefits of the
    concurrent execution.

    For more information and code examples, please refer to the `AsyncIOEventEmitter`
    tutorials at: [https://mdapena.github.io/pyventus/tutorials/emitters/asyncio-event-emitter/](https://mdapena.github.io/pyventus/tutorials/emitters/asyncio-event-emitter/).
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
            events with their respective event handlers. Defaults to `EventLinker`.
        :param debug_mode: Specifies the debug mode for the subclass logger. If `None`,
            it is determined based on the execution environment.
        """
        # Call the parent class' __init__ method to set up the event linker
        super().__init__(event_linker=event_linker, debug_mode=debug_mode)

        # Initialize the set of background futures
        self._background_futures: Set[Future] = set()  # type: ignore

    def _process(self, task: EventEmitter.EventTask) -> None:
        # Check if AsyncIO event loop is running
        is_loop_running: bool = self.__is_loop_running

        # Log the execution context, if debug mode is enabled
        if self._logger.debug_enabled:  # pragma: no cover
            self._logger.debug(action=f"Running:", msg=f"{'Async' if is_loop_running else 'Sync'} context")

        if is_loop_running:
            # Schedule the event task in the running loop as a future
            future = asyncio.ensure_future(task())

            # Remove the Future from the set of background futures after completion
            future.add_done_callback(self._background_futures.remove)

            # Add the Future to the set of background futures
            self._background_futures.add(future)
        else:
            # Run the event task in a synchronous manner
            asyncio.run(task())
