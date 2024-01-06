import asyncio
from abc import ABC, abstractmethod
from asyncio import Future
from dataclasses import dataclass
from typing import Dict, final, Tuple, Any, Set, NamedTuple
from unittest.mock import patch

import pytest
from celery import Celery
from fakeredis import FakeStrictRedis
from fastapi import FastAPI, BackgroundTasks
from rq import Queue
from starlette.testclient import TestClient

from pyventus import Event, EventLinker, EventEmitter
from pyventus.emitters.celery import CeleryEventEmitter


@pytest.fixture
def clean_event_linker() -> bool:
    """
    Pytest fixture for cleaning up the EventLinker registry.

    This fixture removes all registered event links from the EventLinker registry
    and returns a boolean value indicating whether the cleanup was successful.
    :return: `True`, indicating that the cleanup was successful.
    """
    EventLinker.remove_all()
    return EventLinker.get_event_registry == {}


# --------------------
# RQ
# ----------


@pytest.fixture
def rq_queue() -> Queue:
    """
    Creates and returns a RQ (Redis Queue) object for testing purposes.
    :return: The RQ queue object.
    """
    # Create a new RQ queue object
    return Queue(name="default", connection=FakeStrictRedis(), is_async=False)


# --------------------
# Celery
# ----------


class CeleryMock(Celery):
    def send_task(
        self,
        name,
        args=None,
        kwargs=None,
        countdown=None,
        eta=None,
        task_id=None,
        producer=None,
        connection=None,
        router=None,
        result_cls=None,
        expires=None,
        publisher=None,
        link=None,
        link_error=None,
        add_to_parent=True,
        group_id=None,
        group_index=None,
        retries=0,
        chord=None,
        reply_to=None,
        time_limit=None,
        soft_time_limit=None,
        root_id=None,
        parent_id=None,
        route_name=None,
        shadow=None,
        chain=None,
        task_type=None,
        replaced_task_nesting=0,
        **options,
    ):
        self.tasks[name](*args if args else tuple(), **kwargs if kwargs else {})


class CelerySerializerMock(CeleryEventEmitter.Queue.Serializer):
    @staticmethod
    def dumps(obj: EventEmitter.EventEmission) -> Any:
        return obj

    @staticmethod
    def loads(serialized_obj: Any) -> EventEmitter.EventEmission:
        return serialized_obj


@pytest.fixture
def celery_queue() -> CeleryEventEmitter.Queue:
    celery_app = CeleryMock()
    celery_app.conf.accept_content = ["application/json", "application/x-python-serialize"]

    return CeleryEventEmitter.Queue(celery=celery_app, serializer=CelerySerializerMock)


# --------------------
# FastAPI
# ----------


class FastAPITestContext(NamedTuple):
    background_futures: Set[Future]
    client: TestClient


@pytest.fixture
def fastapi_test_context() -> FastAPITestContext:
    background_futures: Set[Future] = set()

    def add_task(self, func, *args, **kwargs) -> None:
        try:
            asyncio.get_running_loop()
            future = asyncio.ensure_future(func(*args, **kwargs))
            background_futures.add(future)
            future.add_done_callback(background_futures.remove)
        except RuntimeError:
            asyncio.run(func(*args, **kwargs))

    with patch.object(BackgroundTasks, "add_task", add_task):
        yield FastAPITestContext(background_futures=background_futures, client=TestClient(FastAPI()))


# --------------------
# Event Fixtures
# ----------


@final
class EventFixtures:
    @dataclass(frozen=True)
    class CustomEvent1(Event):
        attr1: str

    @dataclass(frozen=True)
    class CustomEvent2(Event):
        attr1: Dict[str, str]
        attr2: str

    @dataclass(frozen=True)
    class CustomEventWithValidation(Event):
        attr1: str
        attr2: float

        def __post_init__(self):
            if len(self.attr1) < 3:
                raise ValueError(f"[{self.__class__.__name__}] Error: 'attr1' must be at least 3 characters.")

            if self.attr2.is_integer():
                raise ValueError(f"[{self.__class__.__name__}] Error: 'attr2' must be a float number.")

    class CustomException1(Exception):
        def __init__(self, error: str | None = None):
            self.error: str = error if error else self.__class__.__name__
            super().__init__(error)

    class CustomException2(Exception):
        def __init__(self, error: str | None = None):
            self.error: str = error if error else self.__class__.__name__
            super().__init__(error)


# --------------------
# Callback Fixtures
# ----------


class CallbackFixtures:
    class Base(ABC):
        @property
        def call_count(self) -> int:
            return self._call_count

        @property
        def args(self) -> Tuple[Any, ...]:
            return self._args

        @property
        def kwargs(self) -> Dict[str, Any]:
            return self._kwargs

        @property
        def return_value(self) -> Any | None:
            return self._return_value

        @property
        def raise_exception(self) -> Exception | None:
            return self._raise_exception

        def __init__(self, return_value: Any | None = None, raise_exception: Exception | None = None):
            self._call_count: int = 0
            self._args: Tuple[Any, ...] = tuple()
            self._kwargs: Dict[str, Any] = {}
            self._return_value: Any = return_value
            self._raise_exception = raise_exception

        @abstractmethod
        def __call__(self, *args, **kwargs) -> Any:
            pass

    class Sync(Base):
        def __call__(self, *args, **kwargs) -> Any:
            self._call_count += 1
            self._args = args
            self._kwargs = kwargs

            if self._raise_exception and issubclass(self._raise_exception.__class__, Exception):
                raise self._raise_exception

            return self._return_value

    class Async(Base):
        async def __call__(self, *args, **kwargs) -> Any:
            self._call_count += 1
            self._kwargs = kwargs
            self._args = args

            if self._raise_exception and issubclass(self._raise_exception.__class__, Exception):
                raise self._raise_exception

            return self._return_value
