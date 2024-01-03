from typing import Type, Callable

from ..event_emitter import EventEmitter
from ...core.exceptions import PyventusException
from ...linkers import EventLinker

try:  # pragma: no cover
    from fastapi import BackgroundTasks
except ImportError:  # pragma: no cover
    raise PyventusException(
        "Optional dependency 'fastapi' not found."
        "\nPlease install it using 'pip install pyventus[fastapi]' to use this event emitter."
    )


class FastAPIEventEmitter(EventEmitter):
    """
    A class that enables event handling in [FastAPI](https://fastapi.tiangolo.com/) using its powerful
    [BackgroundTasks](https://fastapi.tiangolo.com/reference/background/) system.

    This class extends the base `EventEmitter` class and leverages the FastAPI's BackgroundTasks feature to
    process event emissions asynchronously. It provides a convenient way to incorporate event-driven
    functionality into FastAPI applications.

    This class provides a powerful mechanism for implementing asynchronous and decoupled operations,
    such as asynchronously sending emails in an event-driven manner. It opens up possibilities for
    building scalable and responsive FastAPI applications.

    For more information and code examples, please refer to the `FastAPIEventEmitter` tutorials at:
    [https://mdapena.github.io/pyventus/tutorials/emitters/fastapi/](https://mdapena.github.io/pyventus/tutorials/emitters/fastapi/).
    """

    @classmethod
    def options(
        cls, event_linker: Type[EventLinker] = EventLinker, debug: bool | None = None
    ) -> Callable[[BackgroundTasks], "FastAPIEventEmitter"]:
        """
        Returns a decorator that allows configuring the `FastAPIEventEmitter` class when
        using the `Depends` method of `FastAPI`.
        :param event_linker: Specifies the type of event linker to use for associating
            events with their respective event handlers. Defaults to `EventLinker`.
        :param debug: Specifies the debug mode for the logger. If `None`, it is
            determined based on the execution environment.
        :return: A decorator that can be used with the `Depends` method.
        """

        def wrapper(background_tasks: BackgroundTasks) -> "FastAPIEventEmitter":
            """
            Decorator wrapper function that configures the `FastAPIEventEmitter` class with the provided options.
            :param background_tasks: The FastAPI `BackgroundTasks` object used to process event emissions.
            :return: An instance of `FastAPIEventEmitter` configured with the specified options.
            """
            return cls(background_tasks=background_tasks, event_linker=event_linker, debug=debug)

        return wrapper

    def __init__(
        self,
        background_tasks: BackgroundTasks,
        event_linker: Type[EventLinker] = EventLinker,
        debug: bool | None = None,
    ):
        """
        Initializes the `FastAPIEventEmitter`.
        :param background_tasks: The FastAPI `BackgroundTasks` object used to process event emissions.
        :param event_linker: Specifies the type of event linker to use for associating
            events with their respective event handlers. Defaults to `EventLinker`.
        :param debug: Specifies the debug mode for the logger. If `None`, it is
            determined based on the execution environment.
        """
        # Call the parent class' __init__ method to set up the event linker
        super().__init__(event_linker=event_linker, debug=debug)

        # Check if the provided background_tasks object is valid
        if background_tasks is None or not isinstance(background_tasks, BackgroundTasks):
            raise PyventusException("The 'background_tasks' argument must be a valid FastAPI BackgroundTask instance.")

        # Set the background tasks
        self._background_tasks: BackgroundTasks = background_tasks

    def _process(self, event_emission: EventEmitter.EventEmission) -> None:
        # Submit the event emission to the background tasks
        self._background_tasks.add_task(event_emission)
