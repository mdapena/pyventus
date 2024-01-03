import pytest
from _pytest.python_api import raises
from rq import Queue

from pyventus import EventLinker, PyventusException
from pyventus.emitters.rq import RQEventEmitter
from ..event_emitter_test import EventEmitterTest


class TestRQEventEmitter(EventEmitterTest):
    # --------------------
    # Creation
    # ----------

    def test_creation(self, clean_event_linker: bool, rq_queue: Queue):
        # Arrange, Act and Assert
        event_emitter = RQEventEmitter(queue=rq_queue)
        assert event_emitter is not None

    def test_creation_with_invalid_params(self, clean_event_linker: bool):
        # Arrange, Act and Assert
        with raises(PyventusException):
            RQEventEmitter(queue=None)  # type: ignore

    # --------------------
    # Sync Context
    # ----------

    def test_emission_in_sync_context(self, rq_queue: Queue):
        event_emitter = RQEventEmitter(queue=rq_queue)
        with TestRQEventEmitter.run_emission_test(event_emitter=event_emitter):
            pass

    def test_emission_in_sync_context_with_custom_event_linker(self, rq_queue: Queue):
        class CustomEventLinker(EventLinker):
            pass

        event_emitter = RQEventEmitter(queue=rq_queue, event_linker=CustomEventLinker)
        with TestRQEventEmitter.run_emission_test(event_emitter=event_emitter, event_linker=CustomEventLinker):
            pass

    # --------------------
    # Async Context
    # ----------

    @pytest.mark.asyncio
    async def test_emission_in_async_context(self):
        pytest.skip("RQ package doesn't support async tests yet, but works fine in async contexts outside of testing.")

    @pytest.mark.asyncio
    async def test_emission_in_async_context_with_custom_event_linker(self):
        pytest.skip("RQ package doesn't support async tests yet, but works fine in async contexts outside of testing.")
