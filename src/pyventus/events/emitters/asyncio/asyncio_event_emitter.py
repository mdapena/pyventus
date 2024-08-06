import asyncio
from asyncio import Future
from typing import Set, Type

from ..event_emitter import EventEmitter
from ...linkers import EventLinker


class AsyncIOEventEmitter(EventEmitter):
    """
    An event emitter subclass that utilizes the AsyncIO framework to handle
    the execution of event emissions.

    **Notes:**

    -   When used in an asynchronous context where an event loop is already running,
        the event emission is scheduled and processed on that existing loop. If the
        event loop is closed before all callbacks complete, any remaining scheduled
        callbacks will be canceled.

    -   When used in a synchronous context where no event loop is active, a new event
        loop is started and subsequently closed by the `asyncio.run()` method. Within
        this loop, the event emission is executed. The loop then waits for all
        scheduled tasks to finish before closing.

    ---
    Read more in the
    [Pyventus docs for AsyncIO Event Emitter](https://mdapena.github.io/pyventus/tutorials/emitters/asyncio/).
    """

    @property
    def __is_loop_running(self) -> bool:
        """
        Check if there is currently an active AsyncIO event loop.
        :return: `True` if an event loop is running, `False` otherwise.
        """
        try:
            asyncio.get_running_loop()
            return True
        except RuntimeError:
            return False

    def __init__(self, event_linker: Type[EventLinker] = EventLinker, debug: bool | None = None) -> None:
        """
        Initialize an instance of `AsyncIOEventEmitter`.
        :param event_linker: Specifies the type of event linker used to manage and access
            events along with their corresponding event handlers. Defaults to `EventLinker`.
        :param debug: Specifies the debug mode for the logger. If `None`, it is
            determined based on the execution environment.
        """
        # Call the parent class' __init__ method
        super().__init__(event_linker=event_linker, debug=debug)

        # Initialize the set of background futures
        self._background_futures: Set[Future] = set()  # type: ignore[type-arg]

    def _process(self, event_emission: EventEmitter.EventEmission) -> None:
        # Check if there is an active event loop
        is_loop_running: bool = self.__is_loop_running

        if is_loop_running:
            # Schedule the event emission in the running loop as a future
            future = asyncio.ensure_future(event_emission())

            # Remove the Future from the set of background futures after completion
            future.add_done_callback(self._background_futures.remove)

            # Add the Future to the set of background futures
            self._background_futures.add(future)
        else:
            # Run the event emission in a blocking manner
            asyncio.run(event_emission())
