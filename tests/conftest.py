import asyncio
from abc import ABC, abstractmethod
from asyncio import Future
from dataclasses import dataclass
from typing import Dict, final, Tuple, Any, Set, NamedTuple, Type, Final, Callable, Coroutine
from unittest.mock import patch

import pytest
from celery import Celery
from fakeredis import FakeStrictRedis
from fastapi import FastAPI, BackgroundTasks
from rq import Queue
from starlette.testclient import TestClient

from pyventus import PyventusException
from pyventus.events import EventLinker, EventEmitter
from pyventus.events.emitters.celery import CeleryEventEmitter


# region ----------------------------------------------------------------------------------------------- Global Fixtures

# ----------------------------------------------
# Event Linker Fixture
# ----------


@pytest.fixture(autouse=True)
def clear_event_linker_registry() -> None:
    """
    Pytest fixture for cleaning up the `EventLinker` registry once per test function.
    :return: None.
    """
    EventLinker.remove_all()
    assert EventLinker.get_registry() == {}


# ----------------------------------------------
# Event Fixtures
# ----------


@final
class EventFixtures:
    """Event Fixtures"""

    StringEvent: Final[str] = "StringEvent"

    ExceptionEvent: Final[Type[ValueError]] = ValueError

    @dataclass
    class EmptyEvent:
        pass

    @dataclass
    class DtcEvent1:
        attr1: str

    @dataclass
    class DtcEvent2:
        attr1: str
        attr2: Dict[str, str]

    @dataclass
    class DtcWithValidation:
        attr1: str
        """It must be at least 3 characters."""

        attr2: float
        """It must be a float number."""

        def __post_init__(self):
            if len(self.attr1) < 3:
                raise PyventusException(f"[{type(self).__name__}] Error: 'attr1' must be at least 3 characters.")

            if self.attr2.is_integer():
                raise PyventusException(f"[{type(self).__name__}] Error: 'attr2' must be a float number.")

    class NonDtcEvent:
        attr1: Dict[str, str]
        attr2: str

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
    """Callback Fixtures"""

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


# --------------------
# Callback Definitions
# ----------


def sync_function():
    pass  # pragma: no cover


async def async_function():
    pass  # pragma: no cover


def sync_generator_function():
    yield  # pragma: no cover


async def async_generator_function():
    yield  # pragma: no cover


class CallbackDefinitions:

    class Sync:

        function: Callable[[None], None] = sync_function

        def __call__(self):
            pass  # pragma: no cover

        @staticmethod
        def static_method():
            pass  # pragma: no cover

        @classmethod
        def class_method(cls):
            pass  # pragma: no cover

        def instance_method(self):
            pass  # pragma: no cover

    class Async:

        function: Callable[[None], Coroutine] = async_function

        async def __call__(self):
            pass  # pragma: no cover

        @staticmethod
        async def static_method():
            pass  # pragma: no cover

        @classmethod
        async def class_method(cls):
            pass  # pragma: no cover

        async def instance_method(self):
            pass  # pragma: no cover

    class SyncGenerator:

        function: Callable[[None], None] = sync_generator_function

        def __call__(self):
            yield  # pragma: no cover

        @staticmethod
        def static_method():
            yield  # pragma: no cover

        @classmethod
        def class_method(cls):
            yield  # pragma: no cover

        def instance_method(self):
            yield  # pragma: no cover

    class AsyncGenerator:

        function: Callable[[None], Coroutine] = async_generator_function

        async def __call__(self):
            yield  # pragma: no cover

        @staticmethod
        async def static_method():
            yield  # pragma: no cover

        @classmethod
        async def class_method(cls):
            yield  # pragma: no cover

        async def instance_method(self):
            yield  # pragma: no cover

    class NoCallable:
        pass  # pragma: no cover


# endregion

# region ------------------------------------------------------------------------------------------ Redis Queue Fixtures

# ----------------------------------------------
# RQ Fixtures
# ----------


@pytest.fixture
def rq_queue() -> Queue:
    """
    Creates and returns a RQ (Redis Queue) object for testing purposes.
    :return: The RQ queue object.
    """
    # Create a new RQ queue object
    return Queue(name="default", connection=FakeStrictRedis(), is_async=False)


# endregion

# region ----------------------------------------------------------------------------------------------- Celery Fixtures


# ----------------------------------------------
# Celery Fixtures
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


# endregion

# region ---------------------------------------------------------------------------------------------- FastAPI Fixtures


# ----------------------------------------------
# FastAPI Fixtures
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


# endregion
