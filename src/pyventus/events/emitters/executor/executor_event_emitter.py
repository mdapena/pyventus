from asyncio import run
from concurrent.futures import Executor, ThreadPoolExecutor
from types import TracebackType

from typing_extensions import override

from ....core.exceptions import PyventusException
from ....core.utils import attributes_repr, formatted_repr
from ...linkers import EventLinker
from ..event_emitter import EventEmitter


class ExecutorEventEmitter(EventEmitter):
    """
    An event emitter subclass that uses the `concurrent.futures` Executor to handle the execution of event emissions.

    **Notes:**

    -   This class can work with either `ThreadPoolExecutor` for thread-based execution or `ProcessPoolExecutor`
        for process-based execution.

    -   When using this event emitter, it is important to properly manage the underlying `Executor`. Once you
        have finished emitting events, call the `shutdown()` method to signal the executor to free any resources
        for pending futures. You can avoid the need to call this method explicitly by using the `with` statement,
        which will automatically shut down the `Executor` (waiting as if `Executor.shutdown()` were called
        with `wait` set to `True`).

    ---
    Read more in the
    [Pyventus docs for Executor Event Emitter](https://mdapena.github.io/pyventus/tutorials/emitters/executor/).
    """

    @staticmethod
    def _execute_event_emission(event_emission: EventEmitter.EventEmission) -> None:
        """
        Execute the event emission.

        :param event_emission: The event emission to be executed.
        :return: None.
        """
        run(event_emission())

    def __init__(
        self,
        executor: Executor | None = None,
        event_linker: type[EventLinker] = EventLinker,
        debug: bool | None = None,
    ) -> None:
        """
        Initialize an instance of `ExecutorEventEmitter`.

        :param executor: The executor object used to handle the execution of event
            emissions. If `None`, a `ThreadPoolExecutor` with default settings will be created.
        :param event_linker: Specifies the type of event linker used to manage and access
            events along with their corresponding subscribers. Defaults to `EventLinker`.
        :param debug: Specifies the debug mode for the logger. If `None`, it is
            determined based on the execution environment.
        """
        # Call the parent class' __init__ method
        super().__init__(event_linker=event_linker, debug=debug)

        # Validate the executor argument
        if executor and not isinstance(executor, Executor):
            raise PyventusException("The 'executor' argument must be an instance of the Executor class.")

        # Use the provided executor or create a default ThreadPoolExecutor if None is given
        self._executor: Executor = executor if executor else ThreadPoolExecutor()

    @override
    def __repr__(self) -> str:  # pragma: no cover
        return formatted_repr(
            instance=self,
            info=(
                attributes_repr(
                    executor=self._executor,
                )
                + f", {super().__repr__()}"
            ),
        )

    @override
    def _process(self, event_emission: EventEmitter.EventEmission) -> None:
        # Submit the event emission to the executor
        self._executor.submit(ExecutorEventEmitter._execute_event_emission, event_emission)

    def shutdown(self, wait: bool = True, cancel_futures: bool = False) -> None:
        """
        Shut down the executor and release any resources it is using.

        :param wait: A boolean indicating whether to wait for the currently pending futures
            to complete before shutting down.
        :param cancel_futures: A boolean indicating whether to cancel any pending futures.
        :return: None.
        """
        self._executor.shutdown(wait=wait, cancel_futures=cancel_futures)

    def __enter__(self) -> "ExecutorEventEmitter":
        """
        Return the current instance of `ExecutorEventEmitter` for context management.

        :return: The current instance of `ExecutorEventEmitter`.
        """
        return self

    def __exit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        """
        Clean up the executor resources when exiting the context.

        :param exc_type: The exception type, if any.
        :param exc_val: The exception value, if any.
        :param exc_tb: The traceback information, if any.
        :return: None.
        """
        self.shutdown(wait=True)
