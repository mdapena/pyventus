import asyncio

import pytest
from _pytest.python_api import raises

from src.pyventus import EventLinker
from src.pyventus.core.exceptions import PyventusException
from src.pyventus.emitters.asyncio import AsyncIOEventEmitter
from tests.emitters.event_emitter_test import EventEmitterTest


class TestAsyncIOEventEmitter(EventEmitterTest):

    @staticmethod
    async def __run_until_complete():
        """ Waits for all AsyncIO pending task to complete """
        await asyncio.gather(*asyncio.all_tasks().difference({asyncio.current_task()}), return_exceptions=True)

    # --------------------
    # Creation
    # ----------

    def test_creation(self, clean_event_linker: bool):
        event_emitter = AsyncIOEventEmitter()
        assert event_emitter is not None

    def test_creation_with_invalid_params(self, clean_event_linker: bool):
        with raises(PyventusException):
            AsyncIOEventEmitter(event_linker=None)  # type: ignore

    # --------------------
    # Sync Context
    # ----------

    def test_emission_in_sync_context(self):
        event_emitter = AsyncIOEventEmitter()
        with TestAsyncIOEventEmitter.run_emission_test(event_emitter=event_emitter):
            pass

    def test_emission_in_sync_context_with_custom_event_linker(self):
        class CustomEventLinker(EventLinker):
            pass

        event_emitter = AsyncIOEventEmitter(event_linker=CustomEventLinker)
        with TestAsyncIOEventEmitter.run_emission_test(event_emitter=event_emitter, event_linker=CustomEventLinker):
            pass

    # --------------------
    # Async Context
    # ----------

    @pytest.mark.asyncio
    async def test_emission_in_async_context(self):
        event_emitter = AsyncIOEventEmitter()
        with TestAsyncIOEventEmitter.run_emission_test(event_emitter=event_emitter):
            await TestAsyncIOEventEmitter.__run_until_complete()

    @pytest.mark.asyncio
    async def test_emission_in_async_context_with_custom_event_linker(self):
        class CustomEventLinker(EventLinker):
            pass

        event_emitter = AsyncIOEventEmitter(event_linker=CustomEventLinker)
        with TestAsyncIOEventEmitter.run_emission_test(event_emitter=event_emitter, event_linker=CustomEventLinker):
            await TestAsyncIOEventEmitter.__run_until_complete()
