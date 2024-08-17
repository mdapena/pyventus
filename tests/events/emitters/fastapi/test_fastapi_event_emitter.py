from asyncio import Task, create_task, gather, get_running_loop, run
from typing import Any, Callable, Set, Type

import pytest
from fastapi import BackgroundTasks, Depends, FastAPI
from starlette import status
from starlette.testclient import TestClient

from pyventus import PyventusException
from pyventus.events import EventLinker
from pyventus.events.emitters.fastapi import FastAPIEventEmitter

from ..event_emitter_test import EventEmitterTest

# ==========================
# Mocks and fixtures
# ==========================


def create_fastapi_test_client() -> TestClient:
    return TestClient(FastAPI())


# ==========================


def create_background_tasks_mock() -> BackgroundTasks:

    class BackgroundTasksMock(BackgroundTasks):

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, **kwargs)
            self.__background_tasks: Set[Task[None]] = set()

        def add_task(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
            try:
                get_running_loop()
                task = create_task(func(*args, **kwargs))
                self.__background_tasks.add(task)
                task.add_done_callback(self.__background_tasks.remove)
            except RuntimeError:
                run(func(*args, **kwargs))

        async def wait_for_tasks(self) -> None:
            # Retrieve the current set of background tasks and clear the registry
            tasks: Set[Task[None]] = self.__background_tasks.copy()
            self.__background_tasks.clear()

            # Await the completion of all background tasks
            await gather(*tasks, return_exceptions=True)

    return BackgroundTasksMock()


# ==========================


class TestFastAPIEventEmitter(EventEmitterTest[FastAPIEventEmitter]):
    def _create_event_emitter(self, event_linker: Type[EventLinker]) -> FastAPIEventEmitter:
        return FastAPIEventEmitter(background_tasks=create_background_tasks_mock(), event_linker=event_linker)

    # ==========================
    # Test Cases for creation
    # ==========================

    def test_creation_with_valid_input(self) -> None:
        # Arrange, Act, Assert
        assert self._create_event_emitter(EventLinker) is not None

    # ==========================

    @pytest.mark.parametrize(
        ["background_tasks", "event_linker", "debug", "exception"],
        [
            (BackgroundTasks(), None, False, PyventusException),
            (BackgroundTasks(), type, False, PyventusException),
            (BackgroundTasks(), EventLinker, object(), PyventusException),
            (None, EventLinker, False, PyventusException),
            (True, EventLinker, False, PyventusException),
        ],
    )
    def test_creation_with_invalid_input(
        self, background_tasks: BackgroundTasks, event_linker: Any, debug: Any, exception: Type[Exception]
    ) -> None:
        # Arrange, Act, Assert
        with pytest.raises(exception):
            FastAPIEventEmitter(background_tasks=background_tasks, event_linker=event_linker, debug=debug)

    # ==========================

    def test_creation_with_depends(self) -> None:
        client = create_fastapi_test_client()

        @client.app.get("/")  # type: ignore[attr-defined, misc]
        def api(event_emitter: FastAPIEventEmitter = Depends(FastAPIEventEmitter)) -> None:
            assert event_emitter and isinstance(event_emitter, FastAPIEventEmitter)

        res = client.get("/")
        assert res.status_code == status.HTTP_200_OK

    # ==========================

    def test_creation_with_depends_and_options(self) -> None:
        client = create_fastapi_test_client()

        @client.app.get("/")  # type: ignore[attr-defined, misc]
        def api(event_emitter: FastAPIEventEmitter = Depends(FastAPIEventEmitter.options(debug=True))) -> None:
            assert event_emitter and isinstance(event_emitter, FastAPIEventEmitter)

        res = client.get("/")
        assert res.status_code == status.HTTP_200_OK

    # ==========================
    # Test Cases for emit()
    # ==========================

    def test_emission_in_sync_context(self) -> None:
        client = create_fastapi_test_client()

        @client.app.get("/")  # type: ignore[attr-defined, misc]
        def api() -> None:
            with self.run_emissions_test(EventLinker) as event_emitter:
                pass

        res = client.get("/")
        assert res.status_code == status.HTTP_200_OK

    # ==========================

    def test_emission_in_sync_context_with_custom_event_linker(self) -> None:
        client = create_fastapi_test_client()

        class CustomEventLinker(EventLinker): ...

        @client.app.get("/")  # type: ignore[attr-defined, misc]
        def api() -> None:
            with self.run_emissions_test(CustomEventLinker) as event_emitter:
                pass

        res = client.get("/")
        assert res.status_code == status.HTTP_200_OK

    # ==========================

    @pytest.mark.asyncio
    async def test_emission_in_async_context(self) -> None:
        client = create_fastapi_test_client()

        @client.app.get("/")  # type: ignore[attr-defined, misc]
        async def api() -> None:
            with self.run_emissions_test(EventLinker) as event_emitter:
                await event_emitter._background_tasks.wait_for_tasks()  # type: ignore[attr-defined]

        res = client.get("/")
        assert res.status_code == status.HTTP_200_OK

    # ==========================

    @pytest.mark.asyncio
    async def test_emission_in_async_context_with_custom_event_linker(self) -> None:
        client = create_fastapi_test_client()

        class CustomEventLinker(EventLinker): ...

        @client.app.get("/")  # type: ignore[attr-defined, misc]
        async def api() -> None:
            with self.run_emissions_test(CustomEventLinker) as event_emitter:
                await event_emitter._background_tasks.wait_for_tasks()  # type: ignore[attr-defined]

        res = client.get("/")
        assert res.status_code == status.HTTP_200_OK
