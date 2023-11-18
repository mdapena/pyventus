from typing import Any, Type, Dict

from src.pyventus.core.exceptions import PyventusException

try:  # pragma: no cover
    from rq import Queue, Callback
except ImportError:  # pragma: no cover
    raise PyventusException(
        "Optional dependency 'rq' not found."
        "\nPlease install it using 'pip install pyventus[rq]' to use this event emitter."
    )

from src.pyventus.core.constants import StdOutColors
from src.pyventus.emitters import EventEmitter
from src.pyventus.linkers import EventLinker
from src.pyventus.listeners import EventListener


class RqEventEmitter(EventEmitter):
    """
    A class that enables event handling using the powerful Redis Queue (RQ)
    pub/sub and worker system.

    This class extends the base EventEmitter class and provides functionality to
    enqueue event listener callbacks using the `rq` package.

     **Event Queueing**: The `emit` method enqueues event listener callbacks using
     the RQ package. The callbacks are executed asynchronously by RQ workers.
    """

    def __init__(
            self,
            rq_queue: Queue,
            rq_result_ttl: int | None = None,
            rq_on_failure: Callback | None = None,
            rq_options: Dict[str, Any] | None = None,
            event_linker: Type[EventLinker] = EventLinker,
            debug_mode: bool | None = None,
    ):
        """
        Initializes an instance of the `RqEventEmitter` class.
        :param rq_queue: The Redis queue for enqueuing event listeners.
        :param rq_result_ttl: Specifies how long (in seconds) successful jobs and their results
            are kept. Expired jobs will be automatically deleted. Defaults to 500 seconds.
        :param rq_on_failure: The callback function to be executed on job failure. Defaults to None.
        :param rq_options: Additional options for the RQ package enqueueing method. Defaults to an empty dictionary.
        :param event_linker: Specifies the type of event linker to use for associating
            events with their respective event listeners. Defaults to `EventLinker`.
        :param debug_mode: Specifies the debug mode for the subclass logger.
            If `None`, it is determined based on the execution environment.
        """
        # Call the parent class' __init__ method to set up the event linker
        super().__init__(event_linker=event_linker, debug_mode=debug_mode)

        # Validate the rq_queue argument
        if rq_queue is None or not isinstance(rq_queue, Queue):
            raise PyventusException("The 'rq_queue' argument must be a valid (RQ) queue.")

        # Store the RQ queue and options
        self._rq_queue: Queue = rq_queue
        """ The Redis queue for enqueuing event listeners. """

        self._rq_options: Dict[str, Any] = rq_options if rq_options is not None else {}
        """ Additional options for the RQ package enqueueing method. """

        # Set the result TTL and on_failure callback in the RQ options
        self._rq_options['result_ttl'] = rq_result_ttl
        self._rq_options['on_failure'] = rq_on_failure

    def _execute(self, *args: Any, event_listener: EventListener, **kwargs: Any) -> None:
        """
        Enqueues the event listener callback using Redis Queue.

        This method enqueues the event listener callback using the provided RQ queue.
        The positional arguments provided as `*args` are passed to the callback function,
        along with any keyword arguments provided as `**kwargs`.

        :param args: Positional arguments to pass to the callback function.
        :param event_listener: The event listener callback function.
        :param kwargs: Keyword arguments to pass to the callback function.
        :return: None
        """
        # Log the execution of the listener, if debug mode is enabled
        if self._logger.debug_enabled:
            self._logger.debug(
                action="Enqueueing:",
                msg=f"[{event_listener}] "
                    f"{StdOutColors.PURPLE}*args:{StdOutColors.DEFAULT} {args} "
                    f"{StdOutColors.PURPLE}**kwargs:{StdOutColors.DEFAULT} {kwargs}"
                    f"{StdOutColors.PURPLE}RQ options:{StdOutColors.DEFAULT} {self._rq_options}"
            )

        # Enqueue the event listener callback using the RQ queue
        self._rq_queue.enqueue(event_listener, *args, **self._rq_options, **kwargs)
