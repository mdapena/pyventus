from dataclasses import dataclass
from sys import gettrace
from types import EllipsisType
from typing import Any

import pytest
from pyventus import PyventusException
from pyventus.events import (
    EventCallbackType,
    EventLinker,
    EventSubscriber,
    FailureCallbackType,
    SubscribableEventType,
    SuccessCallbackType,
)

from ....fixtures import CallableMock, EventFixtures
from ....utils import get_private_attr


# Define a named tuple for better readability of event linker fixture
@dataclass
class EventLinkerFixture:
    event_linker: type[EventLinker]
    events: set[str]
    subscribers: set[EventSubscriber]
    onetime_subscriber_events: set[str]
    onetime_subscribers: set[EventSubscriber]
    to_dict: dict[str, set[EventSubscriber]]


@pytest.fixture
def empty() -> EventLinkerFixture:
    """Fixture for an empty EventLinker."""
    EventLinker.remove_all()
    return EventLinkerFixture(
        event_linker=EventLinker,
        events=set(),
        subscribers=set(),
        onetime_subscriber_events=set(),
        onetime_subscribers=set(),
        to_dict={},
    )


@pytest.fixture
def populated() -> EventLinkerFixture:
    """
    Fixture for an:

    EventLinker = {
        "A": {EventSubscriber1, EventSubscriber3, EventSubscriber4},
        "B": {EventSubscriber1},
        "C": {EventSubscriber3},
        "D": {EventSubscriber2},
    }
    """
    EventLinker.remove_all()

    sub1 = EventLinker.subscribe(
        "A",
        "B",
        event_callback=CallableMock.Sync(),
        success_callback=None,
        failure_callback=None,
        force_async=False,
        once=False,
    )
    sub2 = EventLinker.subscribe(
        "D",
        event_callback=CallableMock.Async(),
        success_callback=None,
        failure_callback=None,
        force_async=False,
        once=True,
    )
    sub3 = EventLinker.subscribe(
        "A",
        "C",
        event_callback=CallableMock.Sync(),
        success_callback=None,
        failure_callback=None,
        force_async=False,
        once=False,
    )
    sub4 = EventLinker.subscribe(
        "A",
        event_callback=CallableMock.Async(),
        success_callback=None,
        failure_callback=None,
        force_async=False,
        once=True,
    )

    return EventLinkerFixture(
        event_linker=EventLinker,
        events={"A", "B", "C", "D"},
        subscribers={sub1, sub2, sub3, sub4},
        onetime_subscriber_events={"A", "D"},
        onetime_subscribers={sub2, sub4},
        to_dict={
            "A": {sub1, sub3, sub4},
            "B": {sub1},
            "C": {sub3},
            "D": {sub2},
        },
    )


# =================================


def create_subscriber() -> EventSubscriber:
    return EventSubscriber(
        teardown_callback=lambda sub: True,
        event_callback=lambda: None,
        success_callback=None,
        failure_callback=None,
        force_async=False,
        once=False,
    )


# =================================


class TestEventLinker:
    # =================================
    # Test Cases for max_subscribers setting and its getter
    # =================================

    def test_max_subscribers_default_value(self) -> None:
        # Arrange/Act/Assert
        assert EventLinker.get_max_subscribers() is None

    # =================================

    def test_max_subscribers_with_valid_input(self) -> None:
        # Arrange
        class CustomEventLinker(EventLinker, max_subscribers=2): ...

        # Act/Assert
        assert CustomEventLinker.get_max_subscribers() == 2

    # =================================

    def test_max_subscribers_with_invalid_input(self) -> None:
        # Arrange/Act/Assert
        with pytest.raises(PyventusException):

            class CustomEventLinker(EventLinker, max_subscribers=0): ...

    # =================================
    # Test Cases for default_success_callback setting and its getter
    # =================================

    def test_default_success_callback_default_value(self) -> None:
        # Arrange/Act/Assert
        assert EventLinker.get_default_success_callback() is None

    # =================================

    def test_default_success_callback_with_valid_input(self) -> None:
        # Arrange
        default_success_callback = CallableMock.Sync()

        # Act
        class CustomEventLinker(EventLinker, default_success_callback=default_success_callback): ...

        # Assert
        assert CustomEventLinker.get_default_success_callback() == default_success_callback

    # =================================

    def test_default_success_callback_with_invalid_input(self) -> None:
        # Arrange/Act/Assert
        with pytest.raises(PyventusException):

            class CustomEventLinker(EventLinker, default_success_callback=True): ...  # type: ignore[arg-type]

    # =================================
    # Test Cases for default_failure_callback setting and its getter
    # =================================

    def test_default_failure_callback_default_value(self) -> None:
        # Arrange/Act/Assert
        assert EventLinker.get_default_failure_callback() is None

    # =================================

    def test_default_failure_callback_with_valid_input(self) -> None:
        # Arrange
        default_failure_callback = CallableMock.Async()

        # Act
        class CustomEventLinker(EventLinker, default_failure_callback=default_failure_callback): ...

        # Assert
        assert CustomEventLinker.get_default_failure_callback() == default_failure_callback

    # =================================

    def test_default_failure_callback_with_invalid_input(self) -> None:
        # Arrange/Act/Assert
        with pytest.raises(PyventusException):

            class CustomEventLinker(EventLinker, default_failure_callback=True): ...  # type: ignore[arg-type]

    # =================================
    # Test Cases for debug mode setting and its getter
    # =================================

    def test_debug_mode_default_value(self) -> None:
        # Arrange
        env_exc: bool = bool(gettrace() is not None)

        # Act/Assert
        assert EventLinker._get_logger().debug_enabled is env_exc

    # =================================

    def test_debug_mode_with_valid_input(self) -> None:
        # Arrange/Act
        class CustomEventLinker(EventLinker, debug=True): ...

        # Assert
        assert CustomEventLinker._get_logger().debug_enabled is True

    # =================================

    def test_debug_mode_with_invalid_input(self) -> None:
        # Arrange/Act/Assert
        with pytest.raises(PyventusException):

            class CustomEventLinker(EventLinker, debug="True"): ...  # type: ignore[arg-type]

    # =================================
    # Test Case for the EvenLinker registry isolation
    # =================================

    def test_registry_isolation(self, populated: EventLinkerFixture) -> None:
        # Arrange/Act
        class IsolatedEventLinker1(EventLinker): ...

        class IsolatedEventLinker2(EventLinker): ...

        IsolatedEventLinker1.subscribe("1", event_callback=lambda: None)
        IsolatedEventLinker2.subscribe("1", event_callback=lambda: None)

        # Assert
        assert (
            populated.event_linker.get_registry()
            != IsolatedEventLinker1.get_registry()
            != IsolatedEventLinker2.get_registry()
        )

    # =================================
    # Test Cases for get_valid_event_name()
    # =================================

    @pytest.mark.parametrize(
        ["event", "expected"],
        [
            (EventFixtures.Str, EventFixtures.Str),
            (EventFixtures.Exc, EventFixtures.Exc.__name__),
            (EventFixtures.EmptyDtc, EventFixtures.EmptyDtc.__name__),
            (EventFixtures.DtcImmutable, EventFixtures.DtcImmutable.__name__),
            (EventFixtures.DtcMutable, EventFixtures.DtcMutable.__name__),
            (EventFixtures.DtcWithVal, EventFixtures.DtcWithVal.__name__),
            (EventFixtures.CustomExc, EventFixtures.CustomExc.__name__),
            (EventFixtures.All, type(EventFixtures.All).__name__),
        ],
    )
    def test_get_valid_event_name_with_valid_input(self, event: SubscribableEventType, expected: str) -> None:
        # Arrange/Act/Assert
        assert EventLinker.get_valid_event_name(event) == expected

    # =================================

    @pytest.mark.parametrize(
        ["event", "exception"],
        [
            (None, PyventusException),
            (True, PyventusException),
            ("", PyventusException),
            (str, PyventusException),
            (EllipsisType, PyventusException),
            (EventFixtures.NonDtc, PyventusException),
            (object, PyventusException),
        ],
    )
    def test_get_valid_event_name_with_invalid_input(self, event: Any, exception: type[Exception]) -> None:
        # Arrange/Act/Assert
        with pytest.raises(exception):
            EventLinker.get_valid_event_name(event)

    # =================================
    # Test Cases for get_valid_subscriber()
    # =================================

    def test_get_valid_subscriber_with_valid_input(self) -> None:
        # Arrange
        subscriber = create_subscriber()

        # Act/Assert
        assert EventLinker.get_valid_subscriber(subscriber) is subscriber

    # =================================

    @pytest.mark.parametrize(
        ["subscriber", "exception"],
        [
            (None, PyventusException),
            (True, PyventusException),
            ("", PyventusException),
            (EventSubscriber, PyventusException),
            (object(), PyventusException),
        ],
    )
    def test_get_valid_subscriber_with_invalid_input(self, subscriber: Any, exception: type[Exception]) -> None:
        # Arrange/Act/Assert
        with pytest.raises(exception):
            EventLinker.get_valid_subscriber(subscriber)

    # =================================
    # Test Cases for _get_valid_and_unique_event_names()
    # =================================

    @pytest.mark.parametrize(
        ["events", "expected"],
        [
            ((Ellipsis, ...), {EllipsisType.__name__}),
            (("A", "B", "C", "B", "A"), {"A", "B", "C"}),
            (
                (..., EventFixtures.EmptyDtc, "A", Exception, Ellipsis, EventFixtures.EmptyDtc, "A"),
                {"A", EllipsisType.__name__, EventFixtures.EmptyDtc.__name__, Exception.__name__},
            ),
        ],
    )
    def test_get_valid_and_unique_event_names_with_valid_input(
        self, events: tuple[SubscribableEventType, ...], expected: set[str]
    ) -> None:
        # Arrange/Act/Assert
        assert EventLinker._get_valid_and_unique_event_names(events=events) == expected

    # =================================

    @pytest.mark.parametrize(
        ["events", "exception"],
        [
            ((), PyventusException),
            ((None,), PyventusException),
            (("A", None), PyventusException),
            ((True,), PyventusException),
            (("A", True), PyventusException),
            (("",), PyventusException),
            (("A", ""), PyventusException),
        ],
    )
    def test_get_valid_and_unique_event_names_with_invalid_input(
        self, events: tuple[Any, ...], exception: type[Exception]
    ) -> None:
        # Arrange/Act/Assert
        with pytest.raises(exception):
            EventLinker._get_valid_and_unique_event_names(events=events)

    # =================================
    # Test Cases for _get_valid_and_unique_subscribers()
    # =================================

    def test_get_valid_and_unique_subscribers_with_valid_input(self) -> None:
        # Arrange
        sub1, sub2, sub3 = create_subscriber(), create_subscriber(), create_subscriber()
        expected = {sub1, sub2, sub3}

        # Act
        subscribers = EventLinker._get_valid_and_unique_subscribers(subscribers=(sub1, sub2, sub3, sub2, sub1, sub2))

        # Assert
        assert subscribers == expected

    # =================================

    @pytest.mark.parametrize(
        ["subscribers", "exception"],
        [
            ((), PyventusException),
            ((None,), PyventusException),
            ((create_subscriber(), None), PyventusException),
            ((object(),), PyventusException),
            ((create_subscriber(), object()), PyventusException),
            ((True,), PyventusException),
            ((create_subscriber(), True), PyventusException),
        ],
    )
    def test_get_valid_and_unique_subscribers_with_invalid_input(
        self, subscribers: tuple[Any, ...], exception: type[Exception]
    ) -> None:
        # Arrange/Act/Assert
        with pytest.raises(exception):
            EventLinker._get_valid_and_unique_subscribers(subscribers=subscribers)

    # =================================
    # Test Cases for is_empty()
    # =================================

    def test_is_empty_when_empty(self, empty: EventLinkerFixture) -> None:
        # Arrange/Act/Assert
        assert empty.event_linker.is_empty() is True

    # =================================

    def test_is_empty_when_populated(self, populated: EventLinkerFixture) -> None:
        # Arrange/Act/Assert
        assert populated.event_linker.is_empty() is False

    # =================================
    # Test Cases for get_registry()
    # =================================

    def test_get_registry_when_empty(self, empty: EventLinkerFixture) -> None:
        # Arrange/Act/Assert
        assert empty.event_linker.get_registry() == empty.to_dict

    # =================================

    def test_get_registry_when_populated(self, populated: EventLinkerFixture) -> None:
        # Arrange/Act/Assert
        assert populated.event_linker.get_registry() == populated.to_dict

    # =================================
    # Test Cases for get_events()
    # =================================

    def test_get_events_when_empty(self, empty: EventLinkerFixture) -> None:
        # Arrange/Act/Assert
        assert empty.event_linker.get_events() == empty.events

    # =================================

    def test_get_events_when_populated(self, populated: EventLinkerFixture) -> None:
        # Arrange/Act/Assert
        assert populated.event_linker.get_events() == populated.events

    # =================================
    # Test Cases for get_subscribers()
    # =================================

    def test_get_subscribers_when_empty(self, empty: EventLinkerFixture) -> None:
        # Arrange/Act/Assert
        assert empty.event_linker.get_subscribers() == empty.subscribers

    # =================================

    def test_get_subscribers_when_populated(self, populated: EventLinkerFixture) -> None:
        # Arrange/Act/Assert
        assert populated.event_linker.get_subscribers() == populated.subscribers

    # =================================
    # Test Cases for get_event_count()
    # =================================

    def test_get_event_count_when_empty(self, empty: EventLinkerFixture) -> None:
        # Arrange/Act/Assert
        assert empty.event_linker.get_event_count() == len(empty.events)

    # =================================

    def test_get_event_count_when_populated(self, populated: EventLinkerFixture) -> None:
        # Arrange/Act/Assert
        assert populated.event_linker.get_event_count() == len(populated.events)

    # =================================
    # Test Cases for get_subscriber_count()
    # =================================

    def test_get_subscriber_count_when_empty(self, empty: EventLinkerFixture) -> None:
        # Arrange/Act/Assert
        assert empty.event_linker.get_subscriber_count() == len(empty.subscribers)

    # =================================

    def test_get_subscriber_count_when_populated(self, populated: EventLinkerFixture) -> None:
        # Arrange/Act/Assert
        assert populated.event_linker.get_subscriber_count() == len(populated.subscribers)

    # =================================
    # Test Cases for get_events_from_subscribers()
    # =================================

    def test_get_events_from_subscribers_when_empty(self, empty: EventLinkerFixture) -> None:
        # Arrange
        sub1, sub2 = create_subscriber(), create_subscriber()

        # Act
        events = empty.event_linker.get_events_from_subscribers(sub1, sub1, sub2)

        # Assert
        assert events == set()

    # =================================

    def test_get_events_from_subscribers_when_populated(self, populated: EventLinkerFixture) -> None:
        # Arrange
        sub1, sub2, sub3 = populated.subscribers.pop(), populated.subscribers.pop(), create_subscriber()
        expected_events = {e for e, s in populated.to_dict.items() if sub1 in s or sub2 in s}

        # Act
        events = populated.event_linker.get_events_from_subscribers(sub1, sub1, sub2, sub3)

        # Assert
        assert events == expected_events

    # =================================
    # Test Cases for get_subscribers_from_events()
    # =================================

    def test_get_subscribers_from_events_when_empty(self, empty: EventLinkerFixture) -> None:
        # Arrange/Act/Assert
        assert empty.event_linker.get_subscribers_from_events("A", "A", "B", "C") == empty.subscribers

    # =================================

    def test_get_subscribers_from_events_when_populated(self, populated: EventLinkerFixture) -> None:
        # Arrange
        event1, event2, event3 = populated.events.pop(), populated.events.pop(), "Invalid"
        expected_subscribers: set[EventSubscriber] = populated.to_dict[event1]
        expected_subscribers.update(populated.to_dict[event2])

        # Act
        subscribers = populated.event_linker.get_subscribers_from_events(event1, event1, event2, event3)

        # Assert
        assert subscribers == expected_subscribers
        assert populated.event_linker.get_event_count() == 4
        assert populated.event_linker.get_subscriber_count() == 4

    # =================================

    def test_get_subscribers_from_events_when_populated_with_pop_onetime_subscribers(
        self, populated: EventLinkerFixture
    ) -> None:
        # Arrange
        expected_subscribers = populated.subscribers

        # Act
        subscribers = populated.event_linker.get_subscribers_from_events(
            *populated.events, "D", "Invalid", pop_onetime_subscribers=True
        )

        # Assert
        assert subscribers == expected_subscribers
        assert populated.event_linker.get_event_count() == 3
        assert populated.event_linker.get_subscriber_count() == 2

    # =================================
    # Test Cases for get_event_count_from_subscriber()
    # =================================

    def test_get_event_count_from_subscriber_when_empty(self, empty: EventLinkerFixture) -> None:
        # Arrange/Act/Assert
        assert empty.event_linker.get_event_count_from_subscriber(create_subscriber()) == 0

    # =================================

    def test_get_event_count_from_subscriber_when_populated(self, populated: EventLinkerFixture) -> None:
        # Arrange
        sub1 = populated.subscribers.pop()
        expected_event_count = len({e for e, s in populated.to_dict.items() if sub1 in s})

        # Act
        event_count = populated.event_linker.get_event_count_from_subscriber(sub1)

        # Assert
        assert event_count == expected_event_count

    # =================================
    # Test Cases for get_subscriber_count_from_event()
    # =================================

    def test_get_subscriber_count_from_event_when_empty(self, empty: EventLinkerFixture) -> None:
        # Arrange/Act/Assert
        assert empty.event_linker.get_subscriber_count_from_event("A") == 0

    # =================================

    def test_get_subscriber_count_from_event_when_populated(self, populated: EventLinkerFixture) -> None:
        # Arrange
        event = populated.events.pop()
        expected_subscriber_count = len(populated.to_dict[event])

        # Act
        subscriber_count = populated.event_linker.get_subscriber_count_from_event(event)

        # Assert
        assert subscriber_count == expected_subscriber_count

    # =================================
    # Test Cases for contains_event()
    # =================================

    def test_contains_event_when_empty(self, empty: EventLinkerFixture) -> None:
        # Arrange/Act/Assert
        assert empty.event_linker.contains_event("A") is False

    # =================================

    def test_contains_event_when_populated(self, populated: EventLinkerFixture) -> None:
        # Arrange/Act/Assert
        assert populated.event_linker.contains_event(populated.events.pop()) is True

    # =================================
    # Test Cases for contains_subscriber()
    # =================================

    def test_contains_subscriber_when_empty(self, empty: EventLinkerFixture) -> None:
        # Arrange/Act/Assert
        assert empty.event_linker.contains_subscriber(create_subscriber()) is False

    # =================================

    def test_contains_subscriber_when_populated(self, populated: EventLinkerFixture) -> None:
        # Arrange/Act/Assert
        assert populated.event_linker.contains_subscriber(populated.subscribers.pop()) is True

    # =================================
    # Test Cases for are_linked()
    # =================================

    def test_are_linked_when_empty(self, empty: EventLinkerFixture) -> None:
        # Arrange/Act/Assert
        assert empty.event_linker.are_linked("A", create_subscriber()) is False

    # =================================

    def test_are_linked_when_populated(self, populated: EventLinkerFixture) -> None:
        # Arrange
        event = populated.events.pop()
        subscriber = populated.to_dict[event].pop()

        # Act/Assert
        assert populated.event_linker.are_linked(event, subscriber) is True

    # =================================
    # Test Cases for subscribe()
    # =================================

    # Define a dataclass for better readability of test cases
    @dataclass
    class SubscribeTestCase:
        events: tuple[SubscribableEventType, ...]
        event_callback: EventCallbackType
        success_callback: SuccessCallbackType | None
        failure_callback: FailureCallbackType | None
        force_async: bool
        once: bool

    # =================================

    @pytest.mark.parametrize(
        ["tc", "default_success_callback", "default_failure_callback"],
        [
            # Tests without default success and failure callbacks
            # =================================
            (
                SubscribeTestCase(
                    events=("A", "B"),
                    event_callback=CallableMock.Sync(),
                    success_callback=None,
                    failure_callback=None,
                    force_async=False,
                    once=False,
                ),
                None,
                None,
            ),
            (
                SubscribeTestCase(
                    events=("A", "B"),
                    event_callback=CallableMock.Async(),
                    success_callback=CallableMock.Sync(),
                    failure_callback=None,
                    force_async=True,
                    once=False,
                ),
                None,
                None,
            ),
            (
                SubscribeTestCase(
                    events=("A", "B"),
                    event_callback=CallableMock.Async(),
                    success_callback=None,
                    failure_callback=CallableMock.Sync(),
                    force_async=False,
                    once=True,
                ),
                None,
                None,
            ),
            (
                SubscribeTestCase(
                    events=("A", "B"),
                    event_callback=CallableMock.Sync(),
                    success_callback=CallableMock.Sync(),
                    failure_callback=CallableMock.Async(),
                    force_async=True,
                    once=True,
                ),
                None,
                None,
            ),
            # Tests with default success and failure callbacks
            # =================================
            (
                SubscribeTestCase(
                    events=("A", "B"),
                    event_callback=CallableMock.Async(),
                    success_callback=None,
                    failure_callback=None,
                    force_async=False,
                    once=False,
                ),
                CallableMock.Sync(),
                CallableMock.Async(),
            ),
            (
                SubscribeTestCase(
                    events=("A", "B"),
                    event_callback=CallableMock.Sync(),
                    success_callback=CallableMock.Async(),
                    failure_callback=None,
                    force_async=True,
                    once=False,
                ),
                CallableMock.Sync(),
                CallableMock.Async(),
            ),
            (
                SubscribeTestCase(
                    events=("A", "B"),
                    event_callback=CallableMock.Async(),
                    success_callback=None,
                    failure_callback=CallableMock.Sync(),
                    force_async=False,
                    once=True,
                ),
                CallableMock.Async(),
                CallableMock.Sync(),
            ),
            (
                SubscribeTestCase(
                    events=("A", "B"),
                    event_callback=CallableMock.Sync(),
                    success_callback=CallableMock.Async(),
                    failure_callback=CallableMock.Sync(),
                    force_async=True,
                    once=True,
                ),
                CallableMock.Sync(),
                CallableMock.Async(),
            ),
        ],
    )
    def test_subscribe(
        self,
        tc: SubscribeTestCase,
        default_success_callback: SuccessCallbackType | None,
        default_failure_callback: FailureCallbackType | None,
    ) -> None:
        # Arrange
        class IsolatedEventLinker(
            EventLinker,
            default_success_callback=default_success_callback,
            default_failure_callback=default_failure_callback,
        ): ...

        # Act
        subscriber = IsolatedEventLinker.subscribe(
            *tc.events,
            event_callback=tc.event_callback,
            success_callback=tc.success_callback,
            failure_callback=tc.failure_callback,
            force_async=tc.force_async,
            once=tc.once,
        )

        subscriber_event_callback = get_private_attr(subscriber, "__event_callback")
        subscriber_success_callback = get_private_attr(subscriber, "__success_callback")
        subscriber_failure_callback = get_private_attr(subscriber, "__failure_callback")

        # Assert
        assert subscriber is not None
        assert isinstance(subscriber, EventSubscriber)

        assert subscriber.once is tc.once

        assert subscriber_event_callback.force_async is tc.force_async
        assert get_private_attr(subscriber_event_callback, "__callable") is tc.event_callback

        if tc.success_callback:
            assert subscriber_success_callback.force_async is tc.force_async
            assert get_private_attr(subscriber_success_callback, "__callable") is tc.success_callback
        else:
            if default_success_callback:
                assert subscriber_success_callback.force_async is tc.force_async
                assert get_private_attr(subscriber_success_callback, "__callable") is default_success_callback
            else:
                assert subscriber_success_callback is None

        if tc.failure_callback:
            assert subscriber_failure_callback.force_async is tc.force_async
            assert get_private_attr(subscriber_failure_callback, "__callable") is tc.failure_callback
        else:
            if default_failure_callback:
                assert subscriber_failure_callback.force_async is tc.force_async
                assert get_private_attr(subscriber_failure_callback, "__callable") is default_failure_callback
            else:
                assert subscriber_failure_callback is None

    # =================================

    def test_subscribe_with_max_subscribers_when_not_exceeded(self) -> None:
        # Arrange
        class IsolatedEventLinker(EventLinker, max_subscribers=1): ...

        IsolatedEventLinker.subscribe("B", event_callback=CallableMock.Sync())

        # Act/Assert
        assert IsolatedEventLinker.subscribe("A", "C", event_callback=CallableMock.Async())

    # =================================

    def test_subscribe_with_max_subscribers_when_exceeded(self) -> None:
        # Arrange
        class IsolatedEventLinker(EventLinker, max_subscribers=1): ...

        IsolatedEventLinker.subscribe("B", event_callback=CallableMock.Sync())

        # Act/Assert
        with pytest.raises(PyventusException):
            IsolatedEventLinker.subscribe("A", "B", event_callback=CallableMock.Async())

    # =================================

    @pytest.mark.parametrize(
        ["tc", "expected_event_count", "expected_subscriber_count"],
        [
            (
                SubscribeTestCase(
                    events=("E", "E"),
                    event_callback=CallableMock.Async(),
                    success_callback=None,
                    failure_callback=None,
                    force_async=False,
                    once=False,
                ),
                5,
                5,
            ),
            (
                SubscribeTestCase(
                    events=("A", "B"),
                    event_callback=CallableMock.Sync(),
                    success_callback=None,
                    failure_callback=None,
                    force_async=False,
                    once=False,
                ),
                4,
                5,
            ),
            (
                SubscribeTestCase(
                    events=("D", "E"),
                    event_callback=CallableMock.Async(),
                    success_callback=None,
                    failure_callback=None,
                    force_async=False,
                    once=False,
                ),
                5,
                5,
            ),
        ],
    )
    def test_subscribe_when_populated(
        self,
        tc: SubscribeTestCase,
        expected_event_count: int,
        expected_subscriber_count: int,
        populated: EventLinkerFixture,
    ) -> None:
        # Arrange/Act
        subscriber = populated.event_linker.subscribe(
            *tc.events,
            event_callback=tc.event_callback,
            success_callback=tc.success_callback,
            failure_callback=tc.failure_callback,
            force_async=tc.force_async,
            once=tc.once,
        )

        # Asserts
        assert all(populated.event_linker.are_linked(event, subscriber) for event in tc.events)
        assert populated.event_linker.get_event_count() == expected_event_count
        assert populated.event_linker.get_subscriber_count() == expected_subscriber_count

    # =================================
    # Test Cases for on() & once() as Decorator
    # =================================

    @pytest.mark.parametrize(
        ["tc", "stateful_subctx", "expected_event_count", "expected_subscriber_count"],
        [
            (
                SubscribeTestCase(
                    events=("E", "E"),
                    event_callback=CallableMock.Async(),
                    success_callback=None,
                    failure_callback=None,
                    force_async=False,
                    once=True,
                ),
                False,
                5,
                5,
            ),
            (
                SubscribeTestCase(
                    events=("A", "B"),
                    event_callback=CallableMock.Sync(),
                    success_callback=None,
                    failure_callback=None,
                    force_async=False,
                    once=True,
                ),
                True,
                4,
                5,
            ),
            (
                SubscribeTestCase(
                    events=("D", "E"),
                    event_callback=CallableMock.Async(),
                    success_callback=None,
                    failure_callback=None,
                    force_async=False,
                    once=True,
                ),
                True,
                5,
                5,
            ),
            (
                SubscribeTestCase(
                    events=("E", "E"),
                    event_callback=CallableMock.Sync(),
                    success_callback=None,
                    failure_callback=None,
                    force_async=False,
                    once=False,
                ),
                False,
                5,
                5,
            ),
            (
                SubscribeTestCase(
                    events=("A", "B"),
                    event_callback=CallableMock.Async(),
                    success_callback=None,
                    failure_callback=None,
                    force_async=False,
                    once=False,
                ),
                True,
                4,
                5,
            ),
            (
                SubscribeTestCase(
                    events=("D", "E"),
                    event_callback=CallableMock.Sync(),
                    success_callback=None,
                    failure_callback=None,
                    force_async=False,
                    once=False,
                ),
                True,
                5,
                5,
            ),
        ],
    )
    def test_on_and_once_as_decorator(
        self,
        tc: SubscribeTestCase,
        stateful_subctx: bool,
        expected_event_count: int,
        expected_subscriber_count: int,
        populated: EventLinkerFixture,
    ) -> None:
        # Arrange
        if tc.once:
            # Test once method as decorator
            subscription_context = populated.event_linker.once(
                *tc.events, force_async=tc.force_async, stateful_subctx=stateful_subctx
            )
        else:
            # Test on method as decorator
            subscription_context = populated.event_linker.on(
                *tc.events, force_async=tc.force_async, stateful_subctx=stateful_subctx
            )

        # Act
        results = subscription_context(tc.event_callback)

        # Assert
        if stateful_subctx:
            event_callback, ctx = results  # type: ignore[misc]
            event_linker, subscriber = ctx.unpack()

            assert event_callback is tc.event_callback
            assert isinstance(ctx, EventLinker.EventLinkerSubCtx)

            assert subscriber
            assert subscriber.once is tc.once
            assert populated.event_linker.contains_subscriber(subscriber)
            assert populated.event_linker is event_linker

            subscriber_event_callback = get_private_attr(subscriber, "__event_callback")
            subscriber_success_callback = get_private_attr(subscriber, "__success_callback")
            subscriber_failure_callback = get_private_attr(subscriber, "__failure_callback")

            assert subscriber_event_callback.force_async is tc.force_async
            assert get_private_attr(subscriber_event_callback, "__callable") is tc.event_callback

            assert subscriber_success_callback is None
            assert subscriber_failure_callback is None
        else:
            assert results is tc.event_callback

        assert populated.event_linker.get_event_count() == expected_event_count
        assert populated.event_linker.get_subscriber_count() == expected_subscriber_count

    # =================================

    def test_on_and_once_as_decorator_with_invalid_input(self, empty: EventLinkerFixture) -> None:
        # Arrange
        once_subctx = empty.event_linker.once("A")
        on_subctx = empty.event_linker.once("A")

        # Act/Assert
        with pytest.raises(PyventusException):
            once_subctx(None)  # type: ignore[arg-type]

        with pytest.raises(PyventusException):
            on_subctx(None)  # type: ignore[arg-type]

    # =================================
    # Test Cases for on() & once() as Context Manager
    # =================================

    @pytest.mark.parametrize(
        ["tc", "stateful_subctx", "expected_event_count", "expected_subscriber_count"],
        [
            (
                SubscribeTestCase(
                    events=("E", "E"),
                    event_callback=CallableMock.Sync(),
                    success_callback=None,
                    failure_callback=None,
                    force_async=False,
                    once=True,
                ),
                False,
                5,
                5,
            ),
            (
                SubscribeTestCase(
                    events=("A", "B"),
                    event_callback=CallableMock.Async(),
                    success_callback=CallableMock.Sync(),
                    failure_callback=None,
                    force_async=False,
                    once=True,
                ),
                True,
                4,
                5,
            ),
            (
                SubscribeTestCase(
                    events=("D", "E"),
                    event_callback=CallableMock.Sync(),
                    success_callback=None,
                    failure_callback=CallableMock.Async(),
                    force_async=False,
                    once=True,
                ),
                True,
                5,
                5,
            ),
            (
                SubscribeTestCase(
                    events=("E", "F"),
                    event_callback=CallableMock.Sync(),
                    success_callback=CallableMock.Async(),
                    failure_callback=CallableMock.Sync(),
                    force_async=False,
                    once=True,
                ),
                True,
                6,
                5,
            ),
            (
                SubscribeTestCase(
                    events=("E", "E"),
                    event_callback=CallableMock.Async(),
                    success_callback=None,
                    failure_callback=None,
                    force_async=False,
                    once=False,
                ),
                False,
                5,
                5,
            ),
            (
                SubscribeTestCase(
                    events=("A", "B"),
                    event_callback=CallableMock.Sync(),
                    success_callback=CallableMock.Async(),
                    failure_callback=None,
                    force_async=False,
                    once=False,
                ),
                True,
                4,
                5,
            ),
            (
                SubscribeTestCase(
                    events=("D", "E"),
                    event_callback=CallableMock.Async(),
                    success_callback=None,
                    failure_callback=CallableMock.Sync(),
                    force_async=False,
                    once=False,
                ),
                True,
                5,
                5,
            ),
            (
                SubscribeTestCase(
                    events=("E", "F"),
                    event_callback=CallableMock.Async(),
                    success_callback=CallableMock.Sync(),
                    failure_callback=CallableMock.Async(),
                    force_async=False,
                    once=False,
                ),
                True,
                6,
                5,
            ),
        ],
    )
    def test_on_and_once_as_context_manager(
        self,
        tc: SubscribeTestCase,
        stateful_subctx: bool,
        expected_event_count: int,
        expected_subscriber_count: int,
        populated: EventLinkerFixture,
    ) -> None:
        # Arrange
        if tc.once:
            # Test once method as decorator
            subscription_context = populated.event_linker.once(
                *tc.events, force_async=tc.force_async, stateful_subctx=stateful_subctx
            )
        else:
            # Test on method as decorator
            subscription_context = populated.event_linker.on(
                *tc.events, force_async=tc.force_async, stateful_subctx=stateful_subctx
            )

        # Act
        with subscription_context as ctx:
            ctx.on_event(tc.event_callback)
            ctx.on_success(tc.success_callback)  # type: ignore[arg-type]
            ctx.on_failure(tc.failure_callback)  # type: ignore[arg-type]

        event_linker, subscriber = ctx.unpack()

        # Assert
        assert isinstance(ctx, EventLinker.EventLinkerSubCtx)

        if stateful_subctx:
            assert subscriber
            assert subscriber.once is tc.once
            assert populated.event_linker.contains_subscriber(subscriber)
            assert populated.event_linker is event_linker

            subscriber_event_callback = get_private_attr(subscriber, "__event_callback")
            subscriber_success_callback = get_private_attr(subscriber, "__success_callback")
            subscriber_failure_callback = get_private_attr(subscriber, "__failure_callback")

            assert subscriber_event_callback.force_async is tc.force_async
            assert get_private_attr(subscriber_event_callback, "__callable") is tc.event_callback

            if tc.success_callback:
                assert subscriber_success_callback.force_async is tc.force_async
                assert get_private_attr(subscriber_success_callback, "__callable") is tc.success_callback
            else:
                assert subscriber_success_callback is None

            if tc.failure_callback:
                assert subscriber_failure_callback.force_async is tc.force_async
                assert get_private_attr(subscriber_failure_callback, "__callable") is tc.failure_callback
            else:
                assert subscriber_failure_callback is None
        else:
            assert subscriber is None
            assert event_linker is None

        assert populated.event_linker.get_event_count() == expected_event_count
        assert populated.event_linker.get_subscriber_count() == expected_subscriber_count

    # =================================

    def test_on_and_once_as_context_manager_with_invalid_input(self, empty: EventLinkerFixture) -> None:
        # Arrange
        once_subctx = empty.event_linker.once("A")
        on_subctx = empty.event_linker.once("A")

        # Act/Assert
        with pytest.raises(PyventusException):
            with once_subctx:
                pass

        with pytest.raises(PyventusException):
            with on_subctx:
                pass

    # =================================

    def test_on_and_once_as_context_manager_and_unpack_before_exit(self, empty: EventLinkerFixture) -> None:
        # Arrange
        once_subctx = empty.event_linker.once("A")
        on_subctx = empty.event_linker.once("A")

        # Act/Assert
        with pytest.raises(PyventusException):
            with once_subctx as ctx1:
                ctx1.on_event(CallableMock.Async())
                ctx1.unpack()

        with pytest.raises(PyventusException):
            with on_subctx as ctx2:
                ctx2.on_event(CallableMock.Sync())
                ctx2.unpack()

    # =================================
    # Test Case for subscribers teardown callback
    # =================================

    def test_subscribers_teardown_callback(self, empty: EventLinkerFixture) -> None:
        # Arrange
        subscriber = empty.event_linker.subscribe("A", "B", "C", event_callback=CallableMock.Async())

        # Act
        results = subscriber.unsubscribe()

        # Assert
        assert results is True
        assert subscriber.unsubscribe() is False
        assert empty.event_linker.is_empty() is True

    # =================================
    # Test Cases for remove()
    # =================================

    def test_remove_when_empty(self, empty: EventLinkerFixture) -> None:
        assert empty.event_linker.remove("A", create_subscriber()) is False

    # =================================

    def test_remove_when_populated(self, populated: EventLinkerFixture) -> None:
        # Arrange
        event1, event2, event3 = populated.events.pop(), populated.events.pop(), populated.events.pop()
        subscriber1 = populated.to_dict[event1].pop()
        subscriber2 = populated.to_dict[event2].pop()
        subscriber3 = populated.to_dict[event3].pop()

        # Act
        result1 = populated.event_linker.remove(event1, create_subscriber())
        result2 = populated.event_linker.remove("Invalid", subscriber1)
        result3 = populated.event_linker.remove(event1, subscriber1)
        result4 = populated.event_linker.remove(event2, subscriber2)
        result5 = populated.event_linker.remove(event3, subscriber3)

        # Assert
        assert result1 is False and result2 is False
        assert result3 is True and result4 is True and result5 is True
        assert not populated.event_linker.are_linked(event1, subscriber1)
        assert not populated.event_linker.are_linked(event2, subscriber2)
        assert not populated.event_linker.are_linked(event3, subscriber3)

    # =================================
    # Test Cases for remove_event()
    # =================================

    def test_remove_event_when_empty(self, empty: EventLinkerFixture) -> None:
        assert empty.event_linker.remove_event(...) is False

    # =================================

    @pytest.mark.parametrize(
        ["event", "expected", "expected_event_count", "expected_subscriber_count"],
        [
            ("Invalid", False, 4, 4),
            ("A", True, 3, 3),
            ("B", True, 3, 4),
            ("D", True, 3, 3),
        ],
    )
    def test_remove_event_when_populated(
        self,
        event: SubscribableEventType,
        expected: bool,
        expected_event_count: int,
        expected_subscriber_count: int,
        populated: EventLinkerFixture,
    ) -> None:
        # Arrange/Act
        results = populated.event_linker.remove_event(event)

        # Assert
        assert results is expected
        assert populated.event_linker.get_event_count() == expected_event_count
        assert populated.event_linker.get_subscriber_count() == expected_subscriber_count

    # =================================
    # Test Cases for remove_subscriber()
    # =================================

    def test_remove_subscriber_when_empty(self, empty: EventLinkerFixture) -> None:
        assert empty.event_linker.remove_subscriber(create_subscriber()) is False

    # =================================

    def test_remove_subscriber_when_populated(self, populated: EventLinkerFixture) -> None:
        # Arrange
        sub1, sub2, sub3 = populated.subscribers.pop(), populated.subscribers.pop(), populated.subscribers.pop()

        # Act
        result1 = populated.event_linker.remove_subscriber(create_subscriber())
        result2 = populated.event_linker.remove_subscriber(sub1)
        result3 = populated.event_linker.remove_subscriber(sub2)
        result4 = populated.event_linker.remove_subscriber(sub3)

        # Assert
        assert result1 is False
        assert result2 is True and result3 is True and result4 is True
        assert populated.event_linker.get_subscriber_count() == 1

    # =================================
    # Test Cases for remove_all()
    # =================================

    def test_remove_all_when_empty(self, empty: EventLinkerFixture) -> None:
        assert empty.event_linker.remove_all() is False

    # =================================

    def test_remove_all_when_populated(self, populated: EventLinkerFixture) -> None:
        # Arrange/Act
        results = populated.event_linker.remove_all()

        # Assert
        assert results is True
        assert populated.event_linker.is_empty() is True
