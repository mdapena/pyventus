from typing import Any, Type

import pytest

from pyventus import PyventusException
from pyventus.events import EventLinker
from pyventus.events.emitters.celery import CeleryEventEmitter

from ..event_emitter_test import EventEmitterTest
from .test_celery_event_emitter_queue import create_celery_queue_mock


class TestCeleryEventEmitter(EventEmitterTest[CeleryEventEmitter]):

    def _create_event_emitter(self, event_linker: Type[EventLinker]) -> CeleryEventEmitter:
        return CeleryEventEmitter(queue=create_celery_queue_mock(), event_linker=event_linker)

    # ==========================
    # Test Cases for creation
    # ==========================

    def test_creation_with_valid_input(self) -> None:
        # Arrange, Act, Assert
        assert self._create_event_emitter(EventLinker) is not None

    # ==========================

    @pytest.mark.parametrize(
        ["queue", "event_linker", "debug", "exception"],
        [
            (None, EventLinker, False, PyventusException),
            (True, EventLinker, False, PyventusException),
            (object(), EventLinker, False, PyventusException),
            (create_celery_queue_mock(), None, False, PyventusException),
            (create_celery_queue_mock(), type, False, PyventusException),
            (create_celery_queue_mock(), EventLinker, object(), PyventusException),
        ],
    )
    def test_creation_with_invalid_input(
        self, queue: CeleryEventEmitter.Queue, event_linker: Any, debug: Any, exception: Type[Exception]
    ) -> None:
        # Arrange, Act, Assert
        with pytest.raises(exception):
            CeleryEventEmitter(queue=queue, event_linker=event_linker, debug=debug)

    # ==========================
    # Test Cases for emit()
    # ==========================

    def test_emission_in_sync_context(self) -> None:
        with self.run_emissions_test(EventLinker) as event_emitter:
            pass

    # ==========================

    def test_emission_in_sync_context_with_custom_event_linker(self) -> None:

        class CustomEventLinker(EventLinker): ...

        with self.run_emissions_test(CustomEventLinker) as event_emitter:
            pass

    # ==========================

    @pytest.mark.asyncio
    async def test_emission_in_async_context(self) -> None:
        pytest.skip("Celery package doesn't support async tests yet.")

    # ==========================

    @pytest.mark.asyncio
    async def test_emission_in_async_context_with_custom_event_linker(self) -> None:
        pytest.skip("Celery package doesn't support async tests yet.")
