from typing import Any, Type

import pytest
from celery import Celery

from pyventus import PyventusException
from pyventus.events import EventEmitter
from pyventus.events.emitters.celery import CeleryEventEmitter


# ==========================
# Celery Mock and fixtures
# ==========================


class CeleryMock(Celery):  # type: ignore[misc]
    """Create and configure a CeleryMock for testing."""

    class Serializer(CeleryEventEmitter.Queue.Serializer):
        @staticmethod
        def dumps(obj: EventEmitter.EventEmission) -> Any:
            return obj

        @staticmethod
        def loads(serialized_obj: Any) -> EventEmitter.EventEmission:
            return serialized_obj  # type: ignore[no-any-return]

    def send_task(self, *args: Any, **kwargs: Any) -> None:
        self.tasks[kwargs["name"]](**kwargs["kwargs"])


# ==========================


def create_celery_mock() -> Celery:
    """Create and configure a Celery event emitter queue for testing."""
    celery_mock = CeleryMock()
    celery_mock.conf.accept_content = ["application/json", "application/x-python-serialize"]
    return celery_mock


# ==========================


def create_celery_queue_mock() -> CeleryEventEmitter.Queue:
    """Create and configure a Celery event emitter queue for testing."""
    return CeleryEventEmitter.Queue(celery=create_celery_mock(), serializer=CeleryMock.Serializer)


# ==========================


class TestCeleryEventEmitterQueue:

    # ==========================
    # Test Cases for creation
    # ==========================

    def test_creation_with_valid_input(self) -> None:
        # Arrange, Act, Assert
        assert create_celery_queue_mock() is not None

    # ==========================

    @pytest.mark.parametrize(
        ["celery", "name", "secret", "serializer", "exception"],
        [
            (None, None, None, CeleryEventEmitter.Queue.Serializer, PyventusException),
            (True, None, None, CeleryEventEmitter.Queue.Serializer, PyventusException),
            (Celery(), None, None, CeleryEventEmitter.Queue.Serializer, PyventusException),
            (create_celery_mock(), "", None, CeleryEventEmitter.Queue.Serializer, PyventusException),
            (create_celery_mock(), None, "", CeleryEventEmitter.Queue.Serializer, PyventusException),
            (create_celery_mock(), None, None, None, PyventusException),
            (create_celery_mock(), None, None, type, PyventusException),
        ],
    )
    def test_creation_with_invalid_input(
        self, celery: Any, name: Any, secret: Any, serializer: Any, exception: Type[Exception]
    ) -> None:
        # Arrange, Act, Assert
        with pytest.raises(exception):
            CeleryEventEmitter.Queue(celery=celery, name=name, secret=secret, serializer=serializer)

    # ==========================
    # Test Cases for payload creation
    # ==========================

    def test_payload_creation_with_valid_input(self) -> None:
        # Arrange, Act, Assert
        assert CeleryEventEmitter.Queue.Payload.from_json(serialized_obj=b"serialized", obj_hash=b"hash") is not None

    # ==========================

    def test_payload_creation_with_unexpected_kwargs(self) -> None:
        # Arrange, Act, Assert
        with pytest.raises(PyventusException):
            CeleryEventEmitter.Queue.Payload.from_json(serialized_obj=b"serialized", obj_hash=b"hash", extra=object())

    # ==========================

    def test_payload_creation_with_missing_kwargs(self) -> None:
        # Arrange, Act, Assert
        with pytest.raises(PyventusException):
            CeleryEventEmitter.Queue.Payload.from_json(serialized_obj=b"serialized")
