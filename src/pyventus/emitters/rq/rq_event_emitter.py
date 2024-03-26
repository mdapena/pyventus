from typing import Any, Type, Dict

from ..event_emitter import EventEmitter
from ...core.exceptions import PyventusException
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
    An event emitter subclass that utilizes the Redis Queue system to handle the
    execution of event emissions.

    **Notes:**

    -   This class uses a Redis Queue instance to enqueue event emissions, which are
        subsequently executed by Redis Queue workers. This approach provides a scalable
        and distributed method for handling the execution of event emissions.

    ---
    Read more in the
    [Pyventus docs for RQ Event Emitter](https://mdapena.github.io/pyventus/tutorials/emitters/rq/).
    """

    def __init__(
        self,
        queue: Queue,
        options: Dict[str, Any] | None = None,
        event_linker: Type[EventLinker] = EventLinker,
        debug: bool | None = None,
    ) -> None:
        """
        Initialize an instance of `RQEventEmitter`.
        :param queue: The Redis queue for enqueuing event handlers.
        :param options: Additional options for the RQ package enqueueing method.
            Defaults to an empty dictionary.
        :param event_linker: Specifies the type of event linker to use for associating
            events with their respective event handlers. Defaults to `EventLinker`.
        :param debug: Specifies the debug mode for the logger. If `None`, it is
            determined based on the execution environment.
        """
        # Call the parent class' __init__ method
        super().__init__(event_linker=event_linker, debug=debug)

        # Validate the queue argument
        if queue is None or not isinstance(queue, Queue):
            raise PyventusException("The 'queue' argument must be a valid (RQ) queue.")

        # Store the Redis queue and RQ options
        self._queue: Queue = queue
        self._options: Dict[str, Any] = options if options is not None else {}

    def _process(self, event_emission: EventEmitter.EventEmission) -> None:
        # Add the event emission to the Redis Queue
        self._queue.enqueue(event_emission, **self._options)
