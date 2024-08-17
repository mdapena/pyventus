from concurrent.futures import Executor, ProcessPoolExecutor, ThreadPoolExecutor
from typing import Any, Type

import pytest

from pyventus import PyventusException
from pyventus.events import EventLinker, ExecutorEventEmitter

from ..event_emitter_test import EventEmitterTest


class TestExecutorEventEmitter(EventEmitterTest[ExecutorEventEmitter]):

    def _create_event_emitter(self, event_linker: Type[EventLinker]) -> ExecutorEventEmitter:
        return ExecutorEventEmitter(executor=ThreadPoolExecutor(), event_linker=event_linker)

    # ==========================
    # Test Cases for creation
    # ==========================

    @pytest.mark.parametrize(
        ["executor"],
        [(ThreadPoolExecutor(),), (ProcessPoolExecutor(),)],
    )
    def test_creation_with_valid_input(self, executor: Executor) -> None:
        # Arrange, Act, Assert
        assert ExecutorEventEmitter(executor=executor) is not None

    # ==========================

    @pytest.mark.parametrize(
        ["executor", "event_linker", "debug", "exception"],
        [
            (None, EventLinker, False, PyventusException),
            (True, EventLinker, False, PyventusException),
            (object(), EventLinker, False, PyventusException),
            (ThreadPoolExecutor(), None, False, PyventusException),
            (ThreadPoolExecutor(), type, False, PyventusException),
            (ThreadPoolExecutor(), EventLinker, object(), PyventusException),
        ],
    )
    def test_creation_with_invalid_input(
        self, executor: Any, event_linker: Any, debug: Any, exception: Type[Exception]
    ) -> None:
        # Arrange, Act, Assert
        with pytest.raises(exception):
            ExecutorEventEmitter(executor=executor, event_linker=event_linker, debug=debug)

    # ==========================
    # Test Cases for emit()
    # ==========================

    def test_emission_in_sync_context(self) -> None:
        with self.run_emissions_test(EventLinker) as event_emitter:
            with event_emitter:  # Testing context manager
                pass

    # ==========================

    def test_emission_in_sync_context_with_custom_event_linker(self) -> None:

        class CustomEventLinker(EventLinker): ...

        with self.run_emissions_test(CustomEventLinker) as event_emitter:
            event_emitter.shutdown(wait=True)

    # ==========================

    @pytest.mark.asyncio
    async def test_emission_in_async_context(self) -> None:
        with self.run_emissions_test(EventLinker) as event_emitter:
            with event_emitter:  # Testing context manager
                pass

    # ==========================

    @pytest.mark.asyncio
    async def test_emission_in_async_context_with_custom_event_linker(self) -> None:

        class CustomEventLinker(EventLinker): ...

        with self.run_emissions_test(CustomEventLinker) as event_emitter:
            event_emitter.shutdown(wait=True)
