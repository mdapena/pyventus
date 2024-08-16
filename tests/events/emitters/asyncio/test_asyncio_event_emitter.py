from asyncio import run
from typing import Type

import pytest

from pyventus import PyventusException
from pyventus.events import AsyncIOEventEmitter, EventLinker

from ..event_emitter_test import EventEmitterTest


class TestAsyncIOEventEmitter(EventEmitterTest[AsyncIOEventEmitter]):

    def create_event_emitter(self, event_linker: Type[EventLinker]) -> AsyncIOEventEmitter:
        return AsyncIOEventEmitter(event_linker=event_linker)

    # ==========================

    def test_creation_with_invalid_input(self) -> None:
        with pytest.raises(PyventusException):
            self.create_event_emitter(event_linker=None)
        with pytest.raises(PyventusException):
            self.create_event_emitter(event_linker=type(True))

    # ==========================

    def test_emission_in_sync_context(self) -> None:
        with self.event_emitter_test(EventLinker) as event_emitter:
            run(event_emitter.wait_for_tasks())

    # ==========================

    def test_emission_in_sync_context_with_custom_event_linker(self) -> None:
        class CustomEventLinker(EventLinker): ...

        with self.event_emitter_test(CustomEventLinker) as event_emitter:
            run(event_emitter.wait_for_tasks())

    # ==========================

    @pytest.mark.asyncio
    async def test_emission_in_async_context(self) -> None:
        with self.event_emitter_test(EventLinker) as event_emitter:
            await event_emitter.wait_for_tasks()

    # ==========================

    @pytest.mark.asyncio
    async def test_emission_in_async_context_with_custom_event_linker(self) -> None:
        class CustomEventLinker(EventLinker): ...

        with self.event_emitter_test(CustomEventLinker) as event_emitter:
            await event_emitter.wait_for_tasks()
