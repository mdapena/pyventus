import asyncio
from asyncio import Future
from typing import Set, Type, Any, cast

from src.pyventus.core.constants import StdOutColors
from src.pyventus.emitters import EventEmitter, EmittableEventType
from src.pyventus.linkers import EventLinker
from src.pyventus.listeners import EventListener


class AsyncioEventEmitter(EventEmitter):
    """
    A class that enables event handling with the AsyncIO framework.

    This class extends the base EventEmitter class and adds functionality to execute event listener callbacks
    using the AsyncIO framework.

    **Asynchronous Execution**: In an asynchronous context where an event loop is already running, the event
    callbacks are scheduled and processed concurrently on that existing loop. If the event loop is closed
    before all callbacks complete, any remaining scheduled tasks will be canceled.

    **Synchronous Execution**: In a synchronous context where no event loop is active, a new event loop is
    started and subsequently closed by using `asyncio.run()`. Within this event loop, an async method is
    executed, which utilizes the `asyncio.gather` function to execute event callbacks concurrently. The
    asyncio loop waits for the completion of all scheduled callbacks from the initial event emission,
    even if new exception events are subsequently emitted. This ensures that the overall execution
    remains synchronous.

    **Examples**:
    .. code-block:: python

    # Asynchronous Execution.
    async def async_context(event_emitter: EventEmitter = AsyncioEventEmitter()) -> None:
        # The event listeners are handled by the already running 
        # asyncio event loop, and the execution does not block.
        event_emitter.emit(Event())

    # Synchronous Execution.
    def sync_context(event_emitter: EventEmitter = AsyncioEventEmitter()) -> None:
        # The event listeners are handled in a new asyncio event 
        # loop, but it blocks execution until all tasks complete.
        event_emitter.emit(Event())
    """

    @property
    def background_futures(self) -> Set[Future]:
        """
        Retrieve the set of currently running background futures within the `AsyncioEventEmitter` instance.
        :return: A set of asyncio.Future objects representing the background
            futures that are currently running inside the `AsyncioEventEmitter` instance.
        """
        return self._background_futures

    @property
    def __is_loop_running(self) -> bool:
        """
        Check if an asyncio event loop is currently running.

        This method checks if there is a current asyncio event loop running by calling `asyncio.get_running_loop()`.
        If no exception is raised, it means there is a running loop and `True` is returned. If a `RuntimeError` is
        raised, it means there is no running loop and `False` is returned.

        :return: `True` if there is a current running event loop, `False` otherwise
        """
        try:
            asyncio.get_running_loop()
            return True
        except RuntimeError:
            return False

    def __init__(self, event_linker: Type[EventLinker] = EventLinker, debug_mode: bool | None = None):
        """
        Initializes an instance of the `AsyncioEventEmitter` class.
        :param event_linker: Specifies the type of event linker to use for associating
            events with their respective event listeners. Defaults to `EventLinker`.
        :param debug_mode: Specifies the debug mode for the subclass logger.
            If `None`, it is determined based on the execution environment.
        """
        # Call the parent class' __init__ method to set up the event linker
        super().__init__(event_linker=event_linker, debug_mode=debug_mode)

        # Initialize the set of background futures
        self._background_futures: Set[Future] = set()

    def emit(self, event: EmittableEventType, *args: Any, **kwargs: Any) -> None:
        """
        Emits an event while supporting both synchronous and asynchronous event listeners using AsyncIO framework.

        **Asynchronous Execution**: In an asynchronous context where an event loop is already running, the event
        callbacks are scheduled and processed concurrently on that existing loop. If the event loop is closed
        before all callbacks complete, any remaining scheduled tasks will be canceled.

        **Synchronous Execution**: In a synchronous context where no event loop is active, a new event loop is
        started and subsequently closed by using `asyncio.run()`. Within this event loop, an async method is
        executed, which utilizes the `asyncio.gather` function to execute event callbacks concurrently. The
        asyncio loop waits for the completion of all scheduled callbacks from the initial event emission,
        even if new exception events are subsequently emitted. This ensures that the overall execution
        remains synchronous.

        :param event: The event to be emitted.
        :param args: Variable-length arguments to be passed to the event callbacks.
        :param kwargs: Arbitrary keyword arguments to be passed to the event callbacks.
        :return: None
        """
        # Check if asyncio event loop is running
        is_loop_running: bool = self.__is_loop_running

        # Log the execution context, if debug mode is enabled
        if self._logger.debug_enabled:
            self._logger.debug(action=f"Running:", msg=f"In {'an [Async]' if is_loop_running else 'a [Sync]'} context")

        # Store reference to superclass
        super_ref: EventEmitter = super()

        if is_loop_running:
            # In async context, emit event directly since loop is already running
            super_ref.emit(event, *args, **kwargs)
        else:
            # Execute emit in async function since loop needs to be started
            async def _inner_callback():
                # Calls the emit method of the superclass
                super_ref.emit(event, *args, **kwargs)

                # Wait for any outstanding background tasks to complete
                while self._background_futures:
                    # In sync context, run concurrently using asyncio.gather
                    await asyncio.gather(*self._background_futures, return_exceptions=True)

            # Run inner callback function to start event loop
            asyncio.run(_inner_callback())

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
                action="Executing:",
                msg=f"[{event_listener}] "
                    f"{StdOutColors.PURPLE}*args:{StdOutColors.DEFAULT} {args} "
                    f"{StdOutColors.PURPLE}**kwargs:{StdOutColors.DEFAULT} {kwargs}"
            )
