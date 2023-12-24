from typing import Any, Type, Dict

from ...core.exceptions import PyventusException
from ...emitters import EventEmitter
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

    This class extends the base `EventEmitter` class and provides the functionality to enqueue
    event delegates using the [RQ package](https://python-rq.org/). Once enqueued, these event
    delegates are processed by RQ workers. This event emitter is particularly useful when
    dealing with events that require resource-intensive tasks like model optimization
    or video processing.

    For more information and code examples, please refer to the `RQEventEmitter` tutorials
    at: [https://mdapena.github.io/pyventus/tutorials/emitters/rq-event-emitter/](https://mdapena.github.io/pyventus/tutorials/emitters/rq-event-emitter/).
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

    def _process(self, delegate: EventEmitter.EventDelegate) -> None:
        # Enqueue the event delegate using the RQ method
        self._queue.enqueue(delegate)
