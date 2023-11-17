import asyncio
from asyncio import AbstractEventLoop, Future
from typing import Set, Type, Any, cast

from src.pyventus.core.constants import StdOutColors
from src.pyventus.emitters import EventEmitter, EmittableEventType
from src.pyventus.linkers import EventLinker
from src.pyventus.listeners import EventListener


class AsyncioEventEmitter(EventEmitter):
    """
    An event emitter class that integrates with the AsyncIO framework for event handling.

    This class extends the base EventEmitter class and provides additional functionality
    for executing event listener callbacks using the AsyncIO framework.

    In an asynchronous context, when the asyncio event loop is active, the event callbacks are
    scheduled and processed concurrently by the event loop. If no event loop is explicitly provided
    as the `asyncio_loop` parameter, the currently running event loop will be used. If the event loop
    is closed before all callbacks complete, all scheduled tasks will be canceled.

    In a synchronous context, the event callbacks are executed concurrently using the `asyncio.gather`
    function, which is then waited on by the asyncio loop until all callbacks complete. If no `asyncio_loop`
    is provided, a new event loop is created and closed within the `emit` function. While the callbacks
    run concurrently using `asyncio.gather`, the overall execution of tasks remains synchronous to
    maintain compatibility with both asynchronous event listener callbacks and synchronous
    program flow.
    """

    @property
    def background_futures(self) -> Set[Future]:
        """
        Retrieve the set of currently running background futures within the AsyncioEmitter instance.
        :return: A set of asyncio.Future objects representing the background
            futures that are currently running inside the AsyncioEmitter instance.
        """
        return set(self._background_futures)

    def __init__(
            self,
            event_linker: Type[EventLinker] = EventLinker,
            debug_mode: bool | None = None,
            asyncio_loop: AbstractEventLoop | None = None,
    ):
        """
        Initializes an instance of the `AsyncioEmitter` class.
        :param event_linker: Specifies the type of event linker to use for associating
            events with their respective event listeners. Defaults to `EventLinker`.
        :param debug_mode: Specifies the debug mode for the subclass logger.
            If `None`, it is determined based on the execution environment.
        :param asyncio_loop: The asyncio event loop to use for executing event listener
            callbacks. If None, the default event loop is used. Defaults to None.
        """
        # Call the parent class' __init__ method to set up the event linker
        super().__init__(event_linker=event_linker, debug_mode=debug_mode)

        # Initialize the asyncio event loop
        self._asyncio_loop: AbstractEventLoop | None = asyncio_loop

        # Initialize the set of background futures
        self._background_futures: Set[Future] = set()

    def emit(self, event: EmittableEventType, *args: Any, **kwargs: Any) -> None:
        """
        Emits an event and triggers the associated event listeners.

        In an asynchronous context, when the asyncio event loop is active, the event callbacks are
        scheduled and processed concurrently by the event loop. If no event loop is explicitly provided
        as the `asyncio_loop` parameter, the currently running event loop will be used. If the event loop
        is closed before all callbacks complete, all scheduled tasks will be canceled.

        In a synchronous context, the event callbacks are executed concurrently using the `asyncio.gather`
        function, which is then waited on by the asyncio loop until all callbacks complete. If no `asyncio_loop`
        is provided, a new event loop is created and closed within the `emit` function. While the callbacks
        run concurrently using `asyncio.gather`, the overall execution of tasks remains synchronous to
        maintain compatibility with both asynchronous event listener callbacks and synchronous
        program flow.

        :param event: The event to be emitted.
        :param args: Variable-length arguments to be passed to the event callbacks.
        :param kwargs: Arbitrary keyword arguments to be passed to the event callbacks.
        :return: None
        """
        # Retrieves the current event loop
        loop: AbstractEventLoop = self._asyncio_loop if self._asyncio_loop is not None else asyncio.get_event_loop()

        # Determines whether the current event loop is already running
        loop_is_running: bool = loop.is_running()

        # Log the execution context, if debug mode is enabled
        if self._logger.debug_enabled:
            self._logger.debug(action=f"Starting:", msg=f"In {'an [Async]' if loop_is_running else 'a [Sync]'} context")

        # Calls the emit method of the superclass
        super().emit(event, *args, **kwargs)

        # If the event loop is not running (synchronous context)
        if not loop_is_running:
            # While there are background futures remaining
            while self._background_futures:
                # Run the event callbacks concurrently until all futures complete
                loop.run_until_complete(asyncio.gather(*self._background_futures, return_exceptions=True))

            # If the asyncio loop was created internally, close it
            if self._asyncio_loop is None:
                loop.close()

    def _execute(self, *args: Any, event_listener: EventListener, **kwargs: Any) -> None:
        """
        Executes the callback function associated with an event listener asynchronously.

        This method executes the callback function associated with the given event listener asynchronously using
        the asyncio framework. The positional arguments provided as `*args` are passed to the callback function,
        along with any keyword arguments provided as `**kwargs`.

        :param args: The positional arguments to pass to the callback function.
        :param event_listener: The event listener whose callback function should be executed.
        :param kwargs: The keyword arguments to pass to the callback function.
        :return: None
        """
        # Execute the callback function asynchronously using asyncio.ensure_future()
        if self._asyncio_loop:
            future: Future = asyncio.ensure_future(event_listener(*args, **kwargs), loop=self._asyncio_loop)
        else:
            future: Future = asyncio.ensure_future(event_listener(*args, **kwargs))

        # Define a _done_callback to handle the completion of the Future
        def _done_callback(fut: Future):
            # Remove the Future from the set of background futures
            self._background_futures.remove(future)

            # If the Future was cancelled, return without further execution
            if fut.cancelled():
                return

            # Get the exception, if any, from the Future
            exception: Exception = cast(Exception, fut.exception())

            # If an exception occurred during execution, emit it as an event
            if exception:
                self.emit(exception)

        # Add the done_callback to the Future
        future.add_done_callback(_done_callback)

        # Add the Future to the set of background futures
        self._background_futures.add(future)

        # Log the execution of the listener, if debug mode is enabled
        if self._logger.debug_enabled:
            self._logger.debug(
                action="Running:  ",
                msg=f"[{event_listener}] "
                    f"{StdOutColors.PURPLE}*args:{StdOutColors.DEFAULT} {args} "
                    f"{StdOutColors.PURPLE}**kwargs:{StdOutColors.DEFAULT} {kwargs}"
            )
