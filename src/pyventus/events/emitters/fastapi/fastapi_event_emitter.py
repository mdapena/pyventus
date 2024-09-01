from collections.abc import Callable

from typing_extensions import override

from ....core.exceptions import PyventusException
from ....core.utils import attributes_repr, formatted_repr
from ...linkers import EventLinker
from ..event_emitter import EventEmitter

try:  # pragma: no cover
    from fastapi import BackgroundTasks
except ImportError:  # pragma: no cover
    raise PyventusException(
        "Optional dependency 'fastapi' not found."
        "\nPlease install it using 'pip install pyventus[fastapi]' to use this event emitter."
    ) from None


class FastAPIEventEmitter(EventEmitter):
    """
    An event emitter subclass that utilizes FastAPI's BackgroundTasks to handle the execution of event emissions.

    **Notes:**

    -   It provides a convenient way to incorporate event-driven functionality into FastAPI apps.

    -   This class offers a powerful mechanism for implementing asynchronous and decoupled operations
        in FastAPI, such as asynchronously sending emails in an event-driven manner.

    ---
    Read more in the
    [Pyventus docs for FastAPI Event Emitter](https://mdapena.github.io/pyventus/tutorials/emitters/fastapi/).
    """

    @classmethod
    def options(
        cls, event_linker: type[EventLinker] = EventLinker, debug: bool | None = None
    ) -> Callable[[BackgroundTasks], "FastAPIEventEmitter"]:
        """
        Return a decorator for configuring the `FastAPIEventEmitter` class with FastAPI's `Depends`.

        :param event_linker: Specifies the type of event linker used to manage and access
            events along with their corresponding subscribers. Defaults to `EventLinker`.
        :param debug: Specifies the debug mode for the logger. If `None`, it is
            determined based on the execution environment.
        :return: A decorator that can be used with the `Depends` method.
        """

        def wrapper(background_tasks: BackgroundTasks) -> "FastAPIEventEmitter":
            """
            Configure the `FastAPIEventEmitter` class with the specified options.

            :param background_tasks: The FastAPI `BackgroundTasks` object used to handle
                the execution of event emissions.
            :return: An instance of `FastAPIEventEmitter` configured with the specified options.
            """
            return cls(background_tasks=background_tasks, event_linker=event_linker, debug=debug)

        return wrapper

    def __init__(
        self,
        background_tasks: BackgroundTasks,
        event_linker: type[EventLinker] = EventLinker,
        debug: bool | None = None,
    ) -> None:
        """
        Initialize an instance of `FastAPIEventEmitter`.

        :param background_tasks: The FastAPI `BackgroundTasks` object used to handle
            the execution of event emissions.
        :param event_linker: Specifies the type of event linker used to manage and access
            events along with their corresponding subscribers. Defaults to `EventLinker`.
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
    def __repr__(self) -> str:  # pragma: no cover
        return formatted_repr(
            instance=self,
            info=(
                attributes_repr(
                    background_tasks=self._background_tasks,
                )
                + f", {super().__repr__()}"
            ),
        )

    @override
    def _process(self, event_emission: EventEmitter.EventEmission) -> None:
        # Submit the event emission to the background tasks
        self._background_tasks.add_task(event_emission)
