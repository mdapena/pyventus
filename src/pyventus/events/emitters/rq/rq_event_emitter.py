from typing import Any

from typing_extensions import override

from ....core.exceptions import PyventusException
from ....core.utils import attributes_repr, formatted_repr
from ...linkers import EventLinker
from ..event_emitter import EventEmitter

try:  # pragma: no cover
    from rq import Queue
except ImportError:  # pragma: no cover
    raise PyventusException(
        "Optional dependency 'rq' not found."
        "\nPlease install it using 'pip install pyventus[rq]' to use this event emitter."
    ) from None


class RQEventEmitter(EventEmitter):
    """
    An event emitter subclass that uses the Redis Queue system to handle the execution of event emissions.

    **Notes:**

    -   This class uses a Redis Queue instance to enqueue event emissions, which are subsequently executed
        by Redis Queue workers. This approach provides a scalable and distributed method for handling the
        execution of event emissions.

    ---
    Read more in the
    [Pyventus docs for RQ Event Emitter](https://mdapena.github.io/pyventus/tutorials/emitters/rq/).
    """

    def __init__(
        self,
        queue: Queue,
        options: dict[str, Any] | None = None,
        event_linker: type[EventLinker] = EventLinker,
        debug: bool | None = None,
    ) -> None:
        """
        Initialize an instance of `RQEventEmitter`.

        :param queue: The Redis queue for enqueuing event emissions.
        :param options: Additional options for the RQ package enqueueing method.
            Defaults to an empty dictionary.
        :param event_linker: Specifies the type of event linker used to manage and access
            events along with their corresponding subscribers. Defaults to `EventLinker`.
        :param debug: Specifies the debug mode for the logger. If `None`, it is
            determined based on the execution environment.
        """
        # Call the parent class' __init__ method
        super().__init__(event_linker=event_linker, debug=debug)

        # Validate the queue argument
        if queue is None:
            raise PyventusException("The 'queue' argument cannot be None.")
        if not isinstance(queue, Queue):
            raise PyventusException("The 'queue' argument must be an instance of the Queue class.")

        # Store the Redis queue and RQ options
        self._queue: Queue = queue
        self._options: dict[str, Any] = options if options is not None else {}

    @override
    def __repr__(self) -> str:  # pragma: no cover
        return formatted_repr(
            instance=self,
            info=(
                attributes_repr(
                    queue=self._queue,
                    options=self._options,
                )
                + f", {super().__repr__()}"
            ),
        )

    @override
    def _process(self, event_emission: EventEmitter.EventEmission) -> None:
        # Add the event emission to the Redis Queue
        self._queue.enqueue(event_emission, **self._options)
