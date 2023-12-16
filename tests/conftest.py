from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, final, Tuple, Any

import pytest
from fakeredis import FakeStrictRedis
from pyventus import Event, EventLinker
from rq import Queue


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


def rq_queue() -> Queue:
    """
    Creates and returns a RQ (Redis Queue) object for testing purposes.
    :return: The RQ queue object.
    """
    # Create a new RQ queue object
    return Queue(name="default", connection=FakeStrictRedis(), is_async=False)


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
