from dataclasses import dataclass
from types import EllipsisType
from typing import Any, Final, final

from pyventus import PyventusException


@final
class EventFixtures:
    """Event Fixtures containing various data classes and exceptions."""

    Str: Final[str] = "StringEvent"

    Exc: Final[type[ValueError]] = ValueError

    class CustomExc(ValueError):
        def __init__(self) -> None:
            super().__init__("Custom Exception!")

    @dataclass
    class EmptyDtc:
        pass

    @dataclass
    class DtcImmutable:
        attr1: str
        attr2: tuple[str, ...]

    @dataclass
    class DtcMutable:
        attr1: list[str]
        attr2: dict[str, str]

    @dataclass
    class DtcWithVal:
        attr1: str  # It must be at least 3 characters.
        attr2: Any

        def __post_init__(self) -> None:
            if len(self.attr1) < 3:
                raise PyventusException(f"[{type(self).__name__}] Error: 'attr1' must be at least 3 characters.")

    class NonDtc:
        pass

    All: EllipsisType = Ellipsis
