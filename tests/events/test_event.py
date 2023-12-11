from dataclasses import dataclass
from typing import Dict, Any

from _pytest.python_api import raises

from pyventus import Event


class TestEvent:
    def test_event_definition(self):
        # Arrange
        @dataclass(frozen=True)
        class EmailEvent(Event):
            email: str
            message: str

        # Act
        event = EmailEvent(email="email@email.com", message="Email message!")

        # Assert
        assert event
        assert event.name
        assert str(event)
        assert event.timestamp
        assert event.email == "email@email.com"
        assert event.message == "Email message!"

    def test_event_definition_with_validation(self):
        # Arrange
        @dataclass(frozen=True)
        class EmailEventWithValidation(Event):
            email: str
            message: str | None = None

            def __post_init__(self):
                if not self.email:
                    raise ValueError("'email' argument cannot be empty")

        # Act
        event = EmailEventWithValidation(email="email@email.com")

        # Assert
        assert event.email == "email@email.com"
        assert event.message is None

        # Arrange | Act | Assert
        with raises(ValueError):
            EmailEventWithValidation(email="")

    def test_event_immutability(self):
        with raises(Exception):
            # Arrange
            @dataclass(frozen=True)
            class CustomEvent(Event):
                attr1: Dict[str, str]

            custom: Any = CustomEvent(attr1={})

            # Act | Assert
            custom.attr1 = {"key": "value"}
