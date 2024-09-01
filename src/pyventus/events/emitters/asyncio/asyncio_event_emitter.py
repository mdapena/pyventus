from asyncio import Task, create_task, gather, run

from typing_extensions import override

from ....core.utils import attributes_repr, formatted_repr, is_loop_running
from ...linkers import EventLinker
from ..event_emitter import EventEmitter


class AsyncIOEventEmitter(EventEmitter):
    """
    An event emitter subclass that utilizes the AsyncIO framework to handle the execution of event emissions.

    **Notes:**

    -   When used in an asynchronous context where an event loop is already running, the event emission is
        scheduled and processed on that existing loop. If the event loop is closed before all callbacks
        complete, any remaining scheduled callbacks will be canceled.

    -   When used in a synchronous context where no event loop is active, a new event loop is started and
        subsequently closed by the `asyncio.run()` method. Within this loop, the event emission is executed.
        The loop then waits for all scheduled tasks to finish before closing.

    ---
    Read more in the
    [Pyventus docs for AsyncIO Event Emitter](https://mdapena.github.io/pyventus/tutorials/emitters/asyncio/).
    """

    def __init__(self, event_linker: type[EventLinker] = EventLinker, debug: bool | None = None) -> None:
        """
        Initialize an instance of `AsyncIOEventEmitter`.

        :param event_linker: Specifies the type of event linker used to manage and access
            events along with their corresponding subscribers. Defaults to `EventLinker`.
        :param debug: Specifies the debug mode for the logger. If `None`, it is
            determined based on the execution environment.
        """
        # Call the parent class' __init__ method
        super().__init__(event_linker=event_linker, debug=debug)

        # Initialize the set of background futures
        self._background_tasks: set[Task[None]] = set()

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
        # Check if there is an active event loop
        loop_running: bool = is_loop_running()

        if loop_running:
            # Schedule the event emission in the running loop as a background task
            task: Task[None] = create_task(event_emission())

            # Remove the Task from the set of background futures after completion
            task.add_done_callback(self._background_tasks.remove)

            # Add the Future to the set of background futures
            self._background_tasks.add(task)
        else:
            # Run the event emission in a blocking manner
            run(event_emission())

    async def wait_for_tasks(self) -> None:
        """
        Wait for all background tasks associated with the emitter to complete.

        It ensures that any ongoing tasks are finished before proceeding.

        :return: None.
        """
        # Retrieve the current set of background tasks and clear the registry
        tasks: set[Task[None]] = self._background_tasks.copy()
        self._background_tasks.clear()

        # Await the completion of all background tasks
        await gather(*tasks)
