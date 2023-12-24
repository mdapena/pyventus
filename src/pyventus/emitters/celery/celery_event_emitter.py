from typing import Type

from .celery_event_task_executor import CeleryEventTaskExecutor
from ..event_emitter import EventEmitter
from ...core.exceptions import PyventusException
from ...linkers import EventLinker


class CeleryEventEmitter(EventEmitter):
    """
    A class that enables event handling using the powerful Celery distributed task queue system.

    This class extends the base `EventEmitter` class and provides the functionality to enqueue
    event handlers using `Celery`. Once enqueued, these event handlers are processed asynchronously
    by `Celery` workers. The `CeleryEventEmitter` is particularly useful when dealing with events that
    require resource-intensive tasks.

    The `CeleryEventEmitter` works by utilizing the provided `CeleryEvenTaskExecutor` instance to
    enqueue the event task for asynchronous processing.

    For more information and code examples, please refer to the `CeleryEventEmitter` tutorials at:
    [https://mdapena.github.io/pyventus/tutorials/emitters/celery-event-emitter/](https://mdapena.github.io/pyventus/tutorials/emitters/celery-event-emitter/).
    """

    def __init__(
        self,
        executor: CeleryEventTaskExecutor,
        event_linker: Type[EventLinker] = EventLinker,
        debug: bool | None = None,
    ):
        """
        Initializes an instance of the `CeleryEventEmitter` class.
        :param executor: The celery event task executor used to process the event task.
        :param event_linker: Specifies the type of event linker to use for associating
            events with their respective event handlers. Defaults to `EventLinker`.
        :param debug: Specifies the debug mode for the subclass logger. If `None`,
            it is determined based on the execution environment.
        """
        # Call the parent class' __init__ method to set up the event linker
        super().__init__(event_linker=event_linker, debug=debug)

        # Validate the executor argument
        if executor is None:
            raise PyventusException("The 'executor' argument cannot be None")

        # Store the CeleryEventTaskExecutor instance
        self._executor: CeleryEventTaskExecutor = executor
        """The CeleryEventTaskExecutor instance used to process the event execution."""

    def _process(self, task: EventEmitter.EventTask) -> None:
        # Enqueue the event task in Celery
        self._executor.enqueue(task=task)
