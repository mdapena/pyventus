from typing import Any, Type, Dict, List

from ...core.constants import StdOutColors
from ...core.exceptions import PyventusException
from ...emitters import EventEmitter
from ...handlers import EventHandler
from ...linkers import EventLinker

try:  # pragma: no cover
    from rq import Queue, Callback
except ImportError:  # pragma: no cover
    raise PyventusException(
        "Optional dependency 'rq' not found."
        "\nPlease install it using 'pip install pyventus[rq]' to use this event emitter."
    )


class RQEventEmitter(EventEmitter):
    """
    A class that enables event handling using the powerful Redis Queue (RQ) pub/sub and
    worker system.

    This class extends the base `EventEmitter` class and provides functionality to enqueue
    event handlers using the `RQ` package.

    **Event Handler Queueing**: The `emit` method enqueues event handlers using the RQ
    package. The callbacks are executed by RQ workers.
    """

    def __init__(
        self,
        queue: Queue,
        options: Dict[str, Any] | None = None,
        event_linker: Type[EventLinker] = EventLinker,
        debug_mode: bool | None = None,
    ):
        """
        Initializes an instance of the `RQEventEmitter` class.
        :param queue: The Redis queue for enqueuing event handlers.
        :param options: Additional options for the RQ package enqueueing method.
            Defaults to an empty dictionary.
        :param event_linker: Specifies the type of event linker to use for associating
            events with their respective event handlers. Defaults to `EventLinker`.
        :param debug_mode: Specifies the debug mode for the subclass logger. If `None`,
            it is determined based on the execution environment.
        """
        # Call the parent class' __init__ method to set up the event linker
        super().__init__(event_linker=event_linker, debug_mode=debug_mode)

        # Validate the queue argument
        if queue is None or not isinstance(queue, Queue):
            raise PyventusException("The 'queue' argument must be a valid (RQ) queue.")

        # Store the RQ queue and options
        self._queue: Queue = queue
        """ The Redis queue for enqueuing event handlers. """

        self._options: Dict[str, Any] = options if options is not None else {}
        """ Additional options for the RQ package enqueueing method. """

    def _execute(self, event_handlers: List[EventHandler], /, *args: Any, **kwargs: Any) -> None:
        # Log the execution of the handlers, if debug mode is enabled
        if self._logger.debug_enabled:
            self._logger.debug(
                action="Enqueueing:",
                msg=f"[{event_handlers}] "
                f"{StdOutColors.PURPLE}*args:{StdOutColors.DEFAULT} {args} "
                f"{StdOutColors.PURPLE}**kwargs:{StdOutColors.DEFAULT} {kwargs}"
                f"{StdOutColors.PURPLE}RQ options:{StdOutColors.DEFAULT} {self._options}",
            )

        # Enqueue the event handlers using the RQ batch method
        self._queue.enqueue_many(
            [Queue.prepare_data(event_handler, args, kwargs, **self._options) for event_handler in event_handlers]
        )
