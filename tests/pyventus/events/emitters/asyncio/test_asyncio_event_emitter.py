from asyncio import run
from typing import Any

import pytest
from pyventus import PyventusException
from pyventus.events import AsyncIOEventEmitter, EventLinker

from ..event_emitter_test import EventEmitterTest


class TestAsyncIOEventEmitter(EventEmitterTest[AsyncIOEventEmitter]):
    def _create_event_emitter(self, event_linker: type[EventLinker]) -> AsyncIOEventEmitter:
        return AsyncIOEventEmitter(event_linker=event_linker)

    # =================================
    # Test Cases for creation
    # =================================

    def test_creation_with_valid_input(self) -> None:
        # Arrange, Act, Assert
        assert self._create_event_emitter(EventLinker) is not None

    # =================================

    @pytest.mark.parametrize(
        ["event_linker", "debug", "exception"],
        [
            (None, False, PyventusException),
            (type, False, PyventusException),
            (EventLinker, object(), PyventusException),
        ],
    )
    def test_creation_with_invalid_input(self, event_linker: Any, debug: Any, exception: type[Exception]) -> None:
        # Arrange, Act, Assert
        with pytest.raises(exception):
            AsyncIOEventEmitter(event_linker=event_linker, debug=debug)

    # =================================
    # Test Cases for emit()
    # =================================

    def test_emission_in_sync_context(self) -> None:
        with self.run_emissions_test(EventLinker) as event_emitter:
            run(event_emitter.wait_for_tasks())

    # =================================

    def test_emission_in_sync_context_with_custom_event_linker(self) -> None:
        class CustomEventLinker(EventLinker): ...

        with self.run_emissions_test(CustomEventLinker) as event_emitter:
            run(event_emitter.wait_for_tasks())

    # =================================

    @pytest.mark.asyncio
    async def test_emission_in_async_context(self) -> None:
        with self.run_emissions_test(EventLinker) as event_emitter:
            await event_emitter.wait_for_tasks()

    # =================================

    @pytest.mark.asyncio
    async def test_emission_in_async_context_with_custom_event_linker(self) -> None:
        class CustomEventLinker(EventLinker): ...

        with self.run_emissions_test(CustomEventLinker) as event_emitter:
            await event_emitter.wait_for_tasks()
