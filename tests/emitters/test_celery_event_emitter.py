import pytest
from _pytest.python_api import raises

from pyventus import PyventusException, EventLinker
from pyventus.emitters.celery import CeleryEventEmitter
from tests import EventEmitterTest


class TestCeleryEventEmitter(EventEmitterTest):
    # --------------------
    # Creation
    # ----------

    def test_creation(self, clean_event_linker: bool, celery_queue: CeleryEventEmitter.Queue) -> None:
        event_emitter = CeleryEventEmitter(queue=celery_queue)
        assert event_emitter is not None

    def test_creation_with_invalid_params(self, clean_event_linker: bool) -> None:
        with raises(PyventusException):
            CeleryEventEmitter(queue=None)  # type: ignore

    # --------------------
    # Sync Context
    # ----------

    def test_emission_in_sync_context(self, clean_event_linker: bool, celery_queue: CeleryEventEmitter.Queue) -> None:
        event_emitter = CeleryEventEmitter(queue=celery_queue)
        with TestCeleryEventEmitter.run_emission_test(event_emitter=event_emitter):
            pass

    def test_emission_in_sync_context_with_custom_event_linker(
        self, clean_event_linker: bool, celery_queue: CeleryEventEmitter.Queue
    ) -> None:
        class CustomEventLinker(EventLinker):
            pass

        event_emitter = CeleryEventEmitter(queue=celery_queue, event_linker=CustomEventLinker)
        with TestCeleryEventEmitter.run_emission_test(event_emitter=event_emitter, event_linker=CustomEventLinker):
            pass

    # --------------------
    # Async Context
    # ----------

    @pytest.mark.asyncio
    async def test_emission_in_async_context(self) -> None:
        pytest.skip(
            "Celery package doesn't support async tests yet, but works fine in async contexts outside of testing."
        )

    @pytest.mark.asyncio
    async def test_emission_in_async_context_with_custom_event_linker(self) -> None:
        pytest.skip(
            "Celery package doesn't support async tests yet, but works fine in async contexts outside of testing."
        )
