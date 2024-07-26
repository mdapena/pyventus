from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

import pytest
from _pytest.python_api import raises

from pyventus import PyventusException
from pyventus.events import ExecutorEventEmitter, EventLinker
from ..event_emitter_test import EventEmitterTest


class TestExecutorEventEmitter(EventEmitterTest):

    def test_creation(self) -> None:
        # Thread event emitter
        thread_emitter = ExecutorEventEmitter(executor=ThreadPoolExecutor())
        assert thread_emitter is not None
        thread_emitter.shutdown()

        # Process event emitter
        process_emitter = ExecutorEventEmitter(executor=ProcessPoolExecutor())
        assert process_emitter is not None
        process_emitter.shutdown()

    def test_creation_with_invalid_params(self) -> None:
        with raises(PyventusException):
            ExecutorEventEmitter(executor=None)
        with raises(PyventusException):
            ExecutorEventEmitter(executor=True)

    def test_emission_in_sync_context(self) -> None:
        # Thread emission
        thread_emitter = ExecutorEventEmitter(executor=ThreadPoolExecutor())
        with TestExecutorEventEmitter.run_emission_test(event_emitter=thread_emitter), thread_emitter:
            pass  # pragma: no cover

    def test_emission_in_sync_context_with_custom_event_linker(self) -> None:
        class CustomEventLinker(EventLinker):
            pass

        thread_emitter = ExecutorEventEmitter(executor=ThreadPoolExecutor(), event_linker=CustomEventLinker)
        with TestExecutorEventEmitter.run_emission_test(event_emitter=thread_emitter, event_linker=CustomEventLinker):
            thread_emitter.shutdown(wait=True)

    @pytest.mark.asyncio
    async def test_emission_in_async_context(self) -> None:
        # Thread emission
        thread_emitter = ExecutorEventEmitter(executor=ThreadPoolExecutor())
        with TestExecutorEventEmitter.run_emission_test(event_emitter=thread_emitter):
            thread_emitter.shutdown(wait=True)

    @pytest.mark.asyncio
    async def test_emission_in_async_context_with_custom_event_linker(self) -> None:
        class CustomEventLinker(EventLinker):
            pass

        thread_emitter = ExecutorEventEmitter(executor=ThreadPoolExecutor(), event_linker=CustomEventLinker)
        with TestExecutorEventEmitter.run_emission_test(event_emitter=thread_emitter, event_linker=CustomEventLinker):
            thread_emitter.shutdown(wait=True)
