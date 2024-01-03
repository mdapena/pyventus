import asyncio
from concurrent.futures import Executor, ThreadPoolExecutor
from types import TracebackType
from typing import Type

from ..event_emitter import EventEmitter
from ...core.exceptions import PyventusException
from ...linkers import EventLinker


class ExecutorEventEmitter(EventEmitter):
    """
    An event emitter that executes event handlers using an `Executor`.

    This class utilizes the `concurrent.futures` Executor base class to handle asynchronous
    execution of event emissions. It can work with either `ThreadPoolExecutor` for thread-based
    execution or `ProcessPoolExecutor` for process-based execution.

    By inheriting from `EventEmitter` and utilizing the `Executor` interface, this class
    provides a consistent way to emit events and execute handlers asynchronously in either
    threads or processes. This allows choosing the optimal execution approach based on
    application needs.

    **Note:** It is important to properly manage the underlying `Executor` when using
    this event emitter. Once finished emitting events, call the `shutdown()` method to
    signal the executor to free any resources for pending futures.

    - You can avoid having to call this method explicitly if you use the `with` statement,
      which will shut down the `Executor` (waiting as if `Executor.shutdown()` were called
      with `wait` set to `True`).

    For more information and code examples, please refer to the `ExecutorEventEmitter`
    tutorials at: [https://mdapena.github.io/pyventus/tutorials/emitters/executor/](https://mdapena.github.io/pyventus/tutorials/emitters/executor/).
    """

    def __init__(
        self,
        executor: Executor = ThreadPoolExecutor(),
        event_linker: Type[EventLinker] = EventLinker,
        debug: bool | None = None,
    ):
        """
        Initializes an instance of the `ExecutorEventEmitter` class.
        :param executor: The executor object used for executing event handlers. Defaults
            to `ThreadPoolExecutor()`.
        :param event_linker: Specifies the type of event linker to use for associating
            events with their respective event handlers. Defaults to `EventLinker`.
        :param debug: Specifies the debug mode for the logger. If `None`, it is
            determined based on the execution environment.
        """
        # Call the parent class' __init__ method to set up the event linker
        super().__init__(event_linker=event_linker, debug=debug)

        # Validate the executor argument
        if executor is None or not issubclass(executor.__class__, Executor):
            raise PyventusException("The 'executor' argument must be a valid executor.")

        # Set the executor object reference
        self._executor: Executor = executor

    def __enter__(self) -> "ExecutorEventEmitter":
        """
        Returns the instance of `ExecutorEventEmitter` for context management.
        :return: The instance of `ExecutorEventEmitter`.
        """
        return self

    def __exit__(
        self, exc_type: Type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        """
        Cleans up the executor resources when exiting the context.
        :param exc_type: The exception type, if any.
        :param exc_val: The exception value, if any.
        :param exc_tb: The traceback information, if any.
        :return: A boolean indicating whether to propagate any exception or not.
        """
        self.shutdown(wait=True)

    def shutdown(self, wait: bool = True, cancel_futures: bool = False) -> None:
        """
        Shuts down the executor and frees any resources it is using.
        :param wait: A boolean indicating whether to wait for the currently pending futures
            to complete before shutting down.
        :param cancel_futures: A boolean indicating whether to cancel any pending futures.
        :return: None
        """
        self._executor.shutdown(wait=wait, cancel_futures=cancel_futures)

    def _process(self, event_emission: EventEmitter.EventEmission) -> None:
        # Submit the event emission to the execution callback
        self._executor.submit(ExecutorEventEmitter._execution_callback, event_emission)

    @staticmethod
    def _execution_callback(event_emission: EventEmitter.EventEmission) -> None:
        """
        This method serves as a callback to be passed to the executor.
        :param event_emission: The event emission to be executed.
        :return: None
        """
        asyncio.run(event_emission())
