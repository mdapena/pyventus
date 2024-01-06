import pytest
from _pytest.python_api import raises
from celery import Celery

from pyventus import PyventusException, EventLinker
from pyventus.emitters.celery import CeleryEventEmitter
from ..event_emitter_test import EventEmitterTest
from ... import CeleryMock


class TestCeleryEventEmitter(EventEmitterTest):
    # --------------------
    # Creation
    # ----------

    def test_creation(
        self,
        clean_event_linker: bool,
        celery_queue: CeleryEventEmitter.Queue,
    ) -> None:
        event_emitter = CeleryEventEmitter(queue=celery_queue)
        assert event_emitter is not None

    def test_creation_with_invalid_params(
        self,
        clean_event_linker: bool,
    ) -> None:
        with raises(PyventusException):
            CeleryEventEmitter(queue=None)  # type: ignore

        with raises(PyventusException):
            CeleryEventEmitter.Queue(celery=None)  # type: ignore

        with raises(PyventusException):
            CeleryEventEmitter.Queue(celery=Celery())

        with raises(PyventusException):
            celery_app = CeleryMock()
            celery_app.conf.accept_content = ["application/json", "application/x-python-serialize"]
            CeleryEventEmitter.Queue(celery=celery_app, secret="")

    # --------------------
    # Sync Context
    # ----------

    def test_emission_in_sync_context(self, celery_queue: CeleryEventEmitter.Queue) -> None:
        event_emitter = CeleryEventEmitter(queue=celery_queue)
        with TestCeleryEventEmitter.run_emission_test(event_emitter=event_emitter):
            pass

    def test_emission_in_sync_context_with_custom_event_linker(self, celery_queue: CeleryEventEmitter.Queue) -> None:
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

    # --------------------
    # Extras
    # ----------

    def test_queue_payload(self):
        # Arrange | Act | Assert
        payload = CeleryEventEmitter.Queue._Payload.from_json(serialized_obj=b"object", obj_hash=b"hash")
        assert payload is not None

        # Arrange | Act | Assert
        with raises(PyventusException):
            CeleryEventEmitter.Queue._Payload.from_json(serialized_obj=b"object")

        # Arrange | Act | Assert
        with raises(PyventusException):
            CeleryEventEmitter.Queue._Payload.from_json(serialized_obj=b"object", obj_hash=b"hash", extra="extra")
