import asyncio

import pytest
from _pytest.python_api import raises
from fastapi import Depends, BackgroundTasks
from starlette import status

from pyventus import EventLinker, PyventusException
from pyventus.emitters.fastapi import FastAPIEventEmitter
from ..event_emitter_test import EventEmitterTest
from ... import FastAPITestContext


class TestFastAPIEventEmitter(EventEmitterTest):

    def test_creation(self, fastapi_test_context: FastAPITestContext) -> None:
        @fastapi_test_context.client.app.get("/")
        def callback(
            background_tasks: BackgroundTasks,
            event_emitter1: FastAPIEventEmitter = Depends(FastAPIEventEmitter),
            event_emitter2: FastAPIEventEmitter = Depends(FastAPIEventEmitter.options(debug=True)),
        ) -> None:
            event_emitter0 = FastAPIEventEmitter(background_tasks=background_tasks, debug=False)
            assert event_emitter0 and isinstance(event_emitter0, FastAPIEventEmitter)
            assert event_emitter1 and isinstance(event_emitter1, FastAPIEventEmitter)
            assert event_emitter2 and isinstance(event_emitter2, FastAPIEventEmitter)

        res = fastapi_test_context.client.get("/")

        assert res.status_code == status.HTTP_200_OK

    def test_creation_with_invalid_params(self, fastapi_test_context: FastAPITestContext) -> None:
        with raises(PyventusException):
            FastAPIEventEmitter(background_tasks=None)
        with raises(PyventusException):
            FastAPIEventEmitter(background_tasks=True)

    def test_emission_in_sync_context(self, fastapi_test_context: FastAPITestContext) -> None:
        @fastapi_test_context.client.app.get("/")
        def callback(event_emitter: FastAPIEventEmitter = Depends(FastAPIEventEmitter)) -> None:
            with TestFastAPIEventEmitter.run_emission_test(event_emitter=event_emitter):
                pass

        res = fastapi_test_context.client.get("/")

        assert res.status_code == status.HTTP_200_OK

    def test_emission_in_sync_context_with_custom_event_linker(self, fastapi_test_context: FastAPITestContext) -> None:
        class CustomEventLinker(EventLinker):
            pass

        @fastapi_test_context.client.app.get("/")
        def callback(
            event_emitter: FastAPIEventEmitter = Depends(FastAPIEventEmitter.options(event_linker=CustomEventLinker)),
        ) -> None:
            with TestFastAPIEventEmitter.run_emission_test(event_emitter=event_emitter, event_linker=CustomEventLinker):
                pass

        res = fastapi_test_context.client.get("/")

        assert res.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_emission_in_async_context(self, fastapi_test_context: FastAPITestContext) -> None:
        @fastapi_test_context.client.app.get("/")
        async def callback(event_emitter: FastAPIEventEmitter = Depends(FastAPIEventEmitter)) -> None:
            with TestFastAPIEventEmitter.run_emission_test(event_emitter=event_emitter):
                await asyncio.gather(*fastapi_test_context.background_futures, return_exceptions=True)

        res = fastapi_test_context.client.get("/")

        assert res.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_emission_in_async_context_with_custom_event_linker(self, fastapi_test_context: FastAPITestContext):
        class CustomEventLinker(EventLinker):
            pass

        @fastapi_test_context.client.app.get("/")
        async def callback(
            event_emitter: FastAPIEventEmitter = Depends(FastAPIEventEmitter.options(event_linker=CustomEventLinker)),
        ) -> None:
            with TestFastAPIEventEmitter.run_emission_test(event_emitter=event_emitter, event_linker=CustomEventLinker):
                await asyncio.gather(*fastapi_test_context.background_futures, return_exceptions=True)

        res = fastapi_test_context.client.get("/")

        assert res.status_code == status.HTTP_200_OK
