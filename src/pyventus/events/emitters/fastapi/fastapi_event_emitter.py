from typing import Callable, Type, override

from ....core.exceptions import PyventusException
from ...linkers import EventLinker
from ..event_emitter import EventEmitter

try:  # pragma: no cover
    from fastapi import BackgroundTasks
except ImportError:  # pragma: no cover
    raise PyventusException(
        "Optional dependency 'fastapi' not found."
        "\nPlease install it using 'pip install pyventus[fastapi]' to use this event emitter."
    )


class FastAPIEventEmitter(EventEmitter):
    """
    An event emitter subclass that utilizes FastAPI's BackgroundTasks system
    to handle the execution of event emissions.

    **Notes:**

    -   It provides a convenient way to incorporate event-driven functionality
        into FastAPI apps.
    -   This class offers a powerful mechanism for implementing asynchronous
        and decoupled operations in FastAPI, such as asynchronously sending
        emails in an event-driven manner.

    ---
    Read more in the
    [Pyventus docs for FastAPI Event Emitter](https://mdapena.github.io/pyventus/tutorials/emitters/fastapi/).
    """

    @classmethod
    def options(
        cls, event_linker: Type[EventLinker] = EventLinker, debug: bool | None = None
    ) -> Callable[[BackgroundTasks], "FastAPIEventEmitter"]:
        """
        Returns a decorator that allows you to configure the `FastAPIEventEmitter` class
        when using FastAPI's `Depends` method.
        :param event_linker: Specifies the type of event linker used to manage and access
            events along with their corresponding event handlers. Defaults to `EventLinker`.
        :param debug: Specifies the debug mode for the logger. If `None`, it is
            determined based on the execution environment.
        :return: A decorator that can be used with the `Depends` method.
        """

        def wrapper(background_tasks: BackgroundTasks) -> "FastAPIEventEmitter":
            """
            A decorator wrapper function that configures the `FastAPIEventEmitter` class with
            the provided options.
            :param background_tasks: The FastAPI `BackgroundTasks` object used to handle
                the execution of event emissions.
            :return: An instance of `FastAPIEventEmitter` configured with the specified options.
            """
            return cls(background_tasks=background_tasks, event_linker=event_linker, debug=debug)

        return wrapper

    def __init__(
        self,
        background_tasks: BackgroundTasks,
        event_linker: Type[EventLinker] = EventLinker,
        debug: bool | None = None,
    ) -> None:
        """
        Initialize an instance of `FastAPIEventEmitter`.
        :param background_tasks: The FastAPI `BackgroundTasks` object used to handle
            the execution of event emissions.
        :param event_linker: Specifies the type of event linker to use for associating
            events with their respective event handlers. Defaults to `EventLinker`.
        :param debug: Specifies the debug mode for the logger. If `None`, it is
            determined based on the execution environment.
        """
        # Call the parent class' __init__ method
        super().__init__(event_linker=event_linker, debug=debug)

        # Check if the provided background_tasks object is valid
        if background_tasks is None:
            raise PyventusException("The 'background_tasks' argument cannot be None.")
        if not isinstance(background_tasks, BackgroundTasks):
            raise PyventusException("The 'background_tasks' argument must be an instance of the BackgroundTasks class.")

        # Set the background tasks
        self._background_tasks: BackgroundTasks = background_tasks

    @override
    def _process(self, event_emission: EventEmitter.EventEmission) -> None:
        # Submit the event emission to the background tasks
        self._background_tasks.add_task(event_emission)
