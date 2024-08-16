from typing import Any

import pytest
from fakeredis import FakeStrictRedis
from rq import Queue

from pyventus import PyventusException
from pyventus.events import EventLinker
from pyventus.events.emitters.rq import RQEventEmitter

from ..event_emitter_test import EventEmitterTest


class TestRQEventEmitter(EventEmitterTest[RQEventEmitter]):

    def _create_event_emitter(self, event_linker: EventLinker) -> RQEventEmitter:
        return RQEventEmitter(
            event_linker=event_linker,
            queue=Queue(
                name="default",
                connection=FakeStrictRedis(),
                is_async=False,
            ),
        )

    # ==========================
    # Test Cases for creation
    # ==========================

    def test_creation_with_valid_input(self) -> None:
        # Arrange, Act, Assert
        assert RQEventEmitter(queue=Queue(connection=FakeStrictRedis())) is not None

    # ==========================

    @pytest.mark.parametrize(
        ["queue", "event_linker", "debug", "exception"],
        [
            (None, EventLinker, False, PyventusException),
            (True, EventLinker, False, PyventusException),
            (object(), EventLinker, False, PyventusException),
            (Queue(connection=FakeStrictRedis()), None, False, PyventusException),
            (Queue(connection=FakeStrictRedis()), type, False, PyventusException),
            (Queue(connection=FakeStrictRedis()), EventLinker, object(), PyventusException),
        ],
    )
    def test_creation_with_invalid_input(self, queue: Any, event_linker: Any, debug: Any, exception: Exception) -> None:
        # Arrange, Act, Assert
        with pytest.raises(exception):
            RQEventEmitter(queue=queue, event_linker=event_linker, debug=debug)

    # ==========================
    # Test Cases for emit()
    # ==========================

    def test_emission_in_sync_context(self) -> None:
        with self.run_emissions_test(EventLinker):
            ...

    # ==========================

    def test_emission_in_sync_context_with_custom_event_linker(self) -> None:
        class CustomEventLinker(EventLinker): ...

        with self.run_emissions_test(CustomEventLinker):
            ...

    # ==========================

    @pytest.mark.asyncio
    async def test_emission_in_async_context(self) -> None:
        pytest.skip("RQ package doesn't support async tests yet.")

    # ==========================

    @pytest.mark.asyncio
    async def test_emission_in_async_context_with_custom_event_linker(self) -> None:
        pytest.skip("RQ package doesn't support async tests yet.")
