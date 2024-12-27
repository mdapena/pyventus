from dataclasses import dataclass
from sys import gettrace
from typing import Any, Generic, TypeVar

import pytest
from pyventus import PyventusException
from pyventus.reactive import CompleteCallbackType, ErrorCallbackType, NextCallbackType, Observable, Subscriber

from ....fixtures import CallableMock
from ....utils import get_private_attr

# =================================
# Test Fixtures & Utils
# =================================

_T = TypeVar("_T")
"""A generic type for the Observable subclass used in testing."""


class Subject(Generic[_T], Observable[_T]):
    """An observable subclass designed for testing the Observable interface."""

    async def next(self, value: _T) -> None:
        """Emit the next value to all subscribers."""
        await self._emit_next(value)

    async def error(self, exception: Exception) -> None:
        """Notify all subscribers of an error."""
        await self._emit_error(exception)

    async def complete(self) -> None:
        """Notify all subscribers that the Observable has completed."""
        await self._emit_complete()


# =================================


@dataclass  # Define a named tuple for better readability of event linker fixture
class ObservableFixture:
    observable: Observable[Any]
    subscribers: set[Subscriber[Any]]


@pytest.fixture
def empty() -> ObservableFixture:
    """Fixture for an empty Observable."""
    return ObservableFixture(observable=Subject[Any](), subscribers=set())


@pytest.fixture
def populated() -> ObservableFixture:
    """
    Fixture for an:

    Observable with {Subscriber1, Subscriber2, Subscriber3}
    """
    subject = Subject[Any]()

    sub1 = subject.subscribe(next_callback=lambda value: None)
    sub2 = subject.subscribe(next_callback=lambda value: None)
    sub3 = subject.subscribe(next_callback=lambda value: None)

    return ObservableFixture(observable=subject, subscribers={sub1, sub2, sub3})


# =================================


def create_subscriber() -> Subscriber[Any]:
    """Retrieve a new Subscriber"""
    return Subscriber[Any](
        teardown_callback=lambda sub: True,
        next_callback=lambda value: None,
        error_callback=None,
        complete_callback=None,
        force_async=False,
    )


# =================================


class TestObservable:
    # =================================
    # Test Cases for creation
    # =================================

    @pytest.mark.parametrize(
        ["debug"],
        [
            (None,),
            (True,),
            (False,),
        ],
    )
    def test_creation_with_valid_input(self, debug: bool | None) -> None:
        # Arrange/Act
        subject = Subject[Any](debug=debug)

        # Assert
        assert subject is not None
        assert isinstance(subject, Observable)
        assert subject._logger.debug_enabled is (bool(gettrace() is not None) if debug is None else debug)
        assert subject._thread_lock is not None

    # =================================

    @pytest.mark.parametrize(
        ["debug", "exception"],
        [
            (bool, PyventusException),
            ("True", PyventusException),
        ],
    )
    def test_creation_with_invalid_input(self, debug: Any, exception: type[Exception]) -> None:
        # Arrange/Act/Assert
        with pytest.raises(exception):
            Subject[Any](debug=debug)

    # =================================
    # Test Cases for get_valid_subscriber()
    # =================================

    def test_get_valid_subscriber_with_valid_input(self) -> None:
        # Arrange
        subscriber = create_subscriber()

        # Act/Assert
        assert Observable.get_valid_subscriber(subscriber) is subscriber

    # =================================

    @pytest.mark.parametrize(
        ["subscriber", "exception"],
        [
            (None, PyventusException),
            (True, PyventusException),
            ("", PyventusException),
            (Subscriber, PyventusException),
            (object(), PyventusException),
        ],
    )
    def test_get_valid_subscriber_with_invalid_input(self, subscriber: Any, exception: type[Exception]) -> None:
        # Arrange/Act/Assert
        with pytest.raises(exception):
            Observable.get_valid_subscriber(subscriber)

    # =================================
    # Test Cases for get_subscribers()
    # =================================

    def test_get_subscribers_when_empty(self, empty: ObservableFixture) -> None:
        # Arrange/Act/Assert
        assert empty.observable.get_subscribers() == empty.subscribers

    # =================================

    def test_get_subscribers_when_populated(self, populated: ObservableFixture) -> None:
        # Arrange/Act/Assert
        assert populated.observable.get_subscribers() == populated.subscribers

    # =================================
    # Test Cases for get_subscriber_count()
    # =================================

    def test_get_subscriber_count_when_empty(self, empty: ObservableFixture) -> None:
        # Arrange/Act/Assert
        assert empty.observable.get_subscriber_count() == len(empty.subscribers)

    # =================================

    def test_get_subscriber_count_when_populated(self, populated: ObservableFixture) -> None:
        # Arrange/Act/Assert
        assert populated.observable.get_subscriber_count() == len(populated.subscribers)

    # =================================
    # Test Cases for contains_subscriber()
    # =================================

    def test_contains_subscriber_when_empty(self, empty: ObservableFixture) -> None:
        # Arrange/Act/Assert
        assert empty.observable.contains_subscriber(create_subscriber()) is False

    # =================================

    def test_contains_subscriber_when_populated(self, populated: ObservableFixture) -> None:
        # Arrange/Act/Assert
        assert populated.observable.contains_subscriber(populated.subscribers.pop()) is True

    # =================================
    # Test Cases for subscribe
    # =================================

    # Define a dataclass for better readability of test cases
    @dataclass
    class SubscribeTestCase:
        next_callback: NextCallbackType[Any] | None
        error_callback: ErrorCallbackType | None
        complete_callback: CompleteCallbackType | None
        force_async: bool

    # =================================

    @pytest.mark.parametrize(
        ["tc"],
        [
            (
                SubscribeTestCase(
                    next_callback=CallableMock.Sync(),
                    error_callback=None,
                    complete_callback=None,
                    force_async=False,
                ),
            ),
            (
                SubscribeTestCase(
                    next_callback=None,
                    error_callback=CallableMock.Async(),
                    complete_callback=None,
                    force_async=True,
                ),
            ),
            (
                SubscribeTestCase(
                    next_callback=None,
                    error_callback=None,
                    complete_callback=CallableMock.Sync(),
                    force_async=False,
                ),
            ),
            (
                SubscribeTestCase(
                    next_callback=CallableMock.Async(),
                    error_callback=CallableMock.Sync(),
                    complete_callback=None,
                    force_async=True,
                ),
            ),
            (
                SubscribeTestCase(
                    next_callback=CallableMock.Sync(),
                    error_callback=None,
                    complete_callback=CallableMock.Async(),
                    force_async=False,
                ),
            ),
            (
                SubscribeTestCase(
                    next_callback=None,
                    error_callback=CallableMock.Async(),
                    complete_callback=CallableMock.Sync(),
                    force_async=True,
                ),
            ),
            (
                SubscribeTestCase(
                    next_callback=CallableMock.Async(),
                    error_callback=CallableMock.Sync(),
                    complete_callback=CallableMock.Async(),
                    force_async=False,
                ),
            ),
        ],
    )
    def test_subscribe(self, tc: SubscribeTestCase) -> None:
        # Arrange
        subject = Subject[Any]()

        # Act
        subscriber = subject.subscribe(
            next_callback=tc.next_callback,
            error_callback=tc.error_callback,
            complete_callback=tc.complete_callback,
            force_async=tc.force_async,
        )

        subscriber_next_callback = get_private_attr(subscriber, "__next_callback")
        subscriber_error_callback = get_private_attr(subscriber, "__error_callback")
        subscriber_complete_callback = get_private_attr(subscriber, "__complete_callback")

        # Assert
        assert subscriber is not None
        assert isinstance(subscriber, Subscriber)
        assert subject.contains_subscriber(subscriber)
        assert subject.get_subscriber_count() == 1

        if subscriber_next_callback:
            assert subscriber_next_callback.force_async is tc.force_async
            assert get_private_attr(subscriber_next_callback, "__callable") is tc.next_callback
        else:
            assert subscriber_next_callback is None

        if subscriber_error_callback:
            assert subscriber_error_callback.force_async is tc.force_async
            assert get_private_attr(subscriber_error_callback, "__callable") is tc.error_callback
        else:
            assert subscriber_error_callback is None

        if subscriber_complete_callback:
            assert subscriber_complete_callback.force_async is tc.force_async
            assert get_private_attr(subscriber_complete_callback, "__callable") is tc.complete_callback
        else:
            assert subscriber_complete_callback is None

    # =================================

    def test_subscribe_when_populated(self, populated: ObservableFixture) -> None:
        # Arrange/Act
        subscriber = populated.observable.subscribe(next_callback=lambda value: None)

        # Asserts
        assert populated.observable.contains_subscriber(subscriber)
        assert populated.observable.get_subscriber_count() == (len(populated.subscribers) + 1)

    # =================================
    # Test Cases for subscribe as Decorator
    # =================================

    @pytest.mark.parametrize(
        ["tc", "stateful_subctx"],
        [
            (
                SubscribeTestCase(
                    next_callback=CallableMock.Sync(),
                    error_callback=None,
                    complete_callback=None,
                    force_async=False,
                ),
                True,
            ),
            (
                SubscribeTestCase(
                    next_callback=CallableMock.Sync(),
                    error_callback=None,
                    complete_callback=None,
                    force_async=False,
                ),
                False,
            ),
        ],
    )
    def test_subscribe_as_decorator(self, tc: SubscribeTestCase, stateful_subctx: bool) -> None:
        # Arrange
        subject = Subject[Any]()
        subctx = subject.subscribe(force_async=tc.force_async, stateful_subctx=stateful_subctx)

        # Act
        results = subctx(tc.next_callback)  # type: ignore[arg-type]

        # Assert
        if stateful_subctx:
            next_callback, ctx = results  # type: ignore[misc]
            obs, subscriber = ctx.unpack()

            assert next_callback is tc.next_callback
            assert isinstance(ctx, Observable.ObservableSubCtx)

            assert obs is subject
            assert subscriber is not None
            assert isinstance(subscriber, Subscriber)
            assert subject.contains_subscriber(subscriber)

            subscriber_next_callback = get_private_attr(subscriber, "__next_callback")
            subscriber_error_callback = get_private_attr(subscriber, "__error_callback")
            subscriber_complete_callback = get_private_attr(subscriber, "__complete_callback")

            assert subscriber_next_callback.force_async is tc.force_async
            assert get_private_attr(subscriber_next_callback, "__callable") is tc.next_callback

            assert subscriber_error_callback is None
            assert subscriber_complete_callback is None
        else:
            assert results is tc.next_callback
            assert subject.get_subscriber_count() == 1

    # =================================

    def test_subscribe_as_decorator_with_invalid_input(self) -> None:
        # Arrange
        subject = Subject[Any]()
        subctx = subject.subscribe()

        # Act, Assert
        with pytest.raises(PyventusException):
            subctx(None)  # type: ignore[arg-type]

    # =================================
    # Test Cases for subscribe as Context Manager
    # =================================

    @pytest.mark.parametrize(
        ["tc", "stateful_subctx"],
        [
            (
                SubscribeTestCase(
                    next_callback=CallableMock.Sync(),
                    error_callback=None,
                    complete_callback=None,
                    force_async=False,
                ),
                True,
            ),
            (
                SubscribeTestCase(
                    next_callback=None,
                    error_callback=CallableMock.Async(),
                    complete_callback=None,
                    force_async=True,
                ),
                False,
            ),
            (
                SubscribeTestCase(
                    next_callback=None,
                    error_callback=None,
                    complete_callback=CallableMock.Sync(),
                    force_async=False,
                ),
                True,
            ),
            (
                SubscribeTestCase(
                    next_callback=CallableMock.Async(),
                    error_callback=CallableMock.Sync(),
                    complete_callback=None,
                    force_async=True,
                ),
                False,
            ),
            (
                SubscribeTestCase(
                    next_callback=CallableMock.Sync(),
                    error_callback=None,
                    complete_callback=CallableMock.Async(),
                    force_async=False,
                ),
                True,
            ),
            (
                SubscribeTestCase(
                    next_callback=None,
                    error_callback=CallableMock.Async(),
                    complete_callback=CallableMock.Sync(),
                    force_async=True,
                ),
                False,
            ),
            (
                SubscribeTestCase(
                    next_callback=CallableMock.Async(),
                    error_callback=CallableMock.Sync(),
                    complete_callback=CallableMock.Async(),
                    force_async=False,
                ),
                True,
            ),
        ],
    )
    def test_subscribe_as_context_manager(self, tc: SubscribeTestCase, stateful_subctx: bool) -> None:
        # Arrange
        subject = Subject[Any]()
        subctx = subject.subscribe(force_async=tc.force_async, stateful_subctx=stateful_subctx)

        # Act
        with subctx as ctx:
            ctx.on_next(tc.next_callback)  # type: ignore[arg-type]
            ctx.on_error(tc.error_callback)  # type: ignore[arg-type]
            ctx.on_complete(tc.complete_callback)  # type: ignore[arg-type]

        obs, subscriber = subctx.unpack()

        # Assert
        assert subctx is not None
        assert isinstance(subctx, Observable.ObservableSubCtx)
        assert subject.get_subscriber_count() == 1

        if stateful_subctx:
            assert obs is subject
            assert subscriber is not None
            assert isinstance(subscriber, Subscriber)
            assert subject.contains_subscriber(subscriber)

            subscriber_next_callback = get_private_attr(subscriber, "__next_callback")
            subscriber_error_callback = get_private_attr(subscriber, "__error_callback")
            subscriber_complete_callback = get_private_attr(subscriber, "__complete_callback")

            if subscriber_next_callback:
                assert subscriber_next_callback.force_async is tc.force_async
                assert get_private_attr(subscriber_next_callback, "__callable") is tc.next_callback
            else:
                assert subscriber_next_callback is None

            if subscriber_error_callback:
                assert subscriber_error_callback.force_async is tc.force_async
                assert get_private_attr(subscriber_error_callback, "__callable") is tc.error_callback
            else:
                assert subscriber_error_callback is None

            if subscriber_complete_callback:
                assert subscriber_complete_callback.force_async is tc.force_async
                assert get_private_attr(subscriber_complete_callback, "__callable") is tc.complete_callback
            else:
                assert subscriber_complete_callback is None
        else:
            assert obs is None
            assert subscriber is None

    # =================================

    def test_subscribe_as_context_manager_with_invalid_input(self) -> None:
        # Arrange
        subject = Subject[Any]()

        # Act/Assert
        with pytest.raises(PyventusException):
            with subject.subscribe():
                pass

    # =================================

    def test_subscribe_as_context_manager_and_unpack_before_exit(self) -> None:
        # Arrange
        subject = Subject[Any]()

        # Act/Assert
        with pytest.raises(PyventusException):
            with subject.subscribe() as ctx:
                ctx.on_next(lambda value: None)
                ctx.unpack()

    # =================================
    # Test Case for subscribers teardown callback
    # =================================

    def test_subscribers_teardown_callback(self) -> None:
        # Arrange
        subject = Subject[Any]()
        subscriber = subject.subscribe(next_callback=lambda value: None)

        # Act
        results = subscriber.unsubscribe()

        # Assert
        assert results is True
        assert subscriber.unsubscribe() is False
        assert subject.get_subscriber_count() == 0

    # =================================
    # Test Cases for remove_subscriber()
    # =================================

    def test_remove_subscriber_when_empty(self, empty: ObservableFixture) -> None:
        # Arrange/Act/Assert
        assert empty.observable.remove_subscriber(create_subscriber()) is False

    # =================================

    def test_remove_subscriber_when_populated(self, populated: ObservableFixture) -> None:
        # Arrange
        sub1, sub2 = populated.subscribers.pop(), populated.subscribers.pop()

        # Act
        result1 = populated.observable.remove_subscriber(create_subscriber())
        result2 = populated.observable.remove_subscriber(sub1)
        result3 = populated.observable.remove_subscriber(sub2)

        # Assert
        assert result1 is False
        assert result2 is True and result3 is True
        assert populated.observable.get_subscriber_count() == 1
        assert populated.observable.contains_subscriber(populated.subscribers.pop()) is True

    # =================================
    # Test Cases for remove_all()
    # =================================

    def test_remove_all_when_empty(self, empty: ObservableFixture) -> None:
        # Arrange/Act/Assert
        assert empty.observable.remove_all() is False

    # =================================

    def test_remove_all_when_populated(self, populated: ObservableFixture) -> None:
        # Arrange/Act
        results = populated.observable.remove_all()

        # Assert
        assert results is True
        assert populated.observable.get_subscriber_count() == 0

    # =================================
    # Test Cases for _emit_next()
    # =================================

    async def test_emit_next_multicast(self) -> None:
        # Arrange
        value = object()
        subject = Subject[Any]()
        callback = CallableMock.Sync()
        subject.subscribe(next_callback=None, error_callback=callback, complete_callback=callback)
        subject.subscribe(next_callback=callback, error_callback=callback, complete_callback=callback)
        subject.subscribe(next_callback=callback, error_callback=callback, complete_callback=callback)

        # Act
        await subject.next(value)
        await subject.next(value)
        subject.remove_all()
        await subject.next(value)

        # Assert
        assert callback.call_count == 4
        assert callback.last_args == (value,)
        assert callback.last_kwargs == {}

    # =================================

    async def test_emit_next_unicast(self) -> None:
        # Arrange
        value = object()
        subject = Subject[Any]()
        callback = CallableMock.Sync()
        subject.subscribe(next_callback=callback, error_callback=callback, complete_callback=callback)

        # Act
        await subject.next(value)
        subject.remove_all()
        await subject.next(value)

        # Assert
        assert callback.call_count == 1
        assert callback.last_args == (value,)
        assert callback.last_kwargs == {}

    # =================================

    async def test_emit_next_with_exceptions_and_different_values_multicast(self) -> None:
        # Arrange
        value1 = object()
        value2 = object()
        subject = Subject[Any]()
        callback = CallableMock.Sync(raise_exception=Exception())
        subject.subscribe(next_callback=callback, error_callback=callback, complete_callback=callback)
        subject.subscribe(next_callback=callback, error_callback=callback, complete_callback=callback)

        # Act
        await subject.next(value1)
        await subject.next(value2)
        subject.remove_all()
        await subject.next(value1)

        # Assert
        assert callback.call_count == 4
        assert callback.last_args == (value2,)
        assert callback.last_kwargs == {}

    # =================================

    async def test_emit_next_with_exceptions_and_values_unicast(self) -> None:
        # Arrange
        value1 = object()
        value2 = object()
        subject = Subject[Any]()
        callback = CallableMock.Sync(raise_exception=Exception())
        subject.subscribe(next_callback=callback, error_callback=callback, complete_callback=callback)

        # Act
        await subject.next(value1)
        await subject.next(value2)
        subject.remove_all()
        await subject.next(value1)

        # Assert
        assert callback.call_count == 2
        assert callback.last_args == (value2,)
        assert callback.last_kwargs == {}

    # =================================
    # Test Cases for _emit_error()
    # =================================

    async def test_emit_error_multicast(self) -> None:
        # Arrange
        exception = Exception()
        subject = Subject[Any]()
        callback = CallableMock.Sync()
        subject.subscribe(next_callback=callback, error_callback=None, complete_callback=callback)
        subject.subscribe(next_callback=callback, error_callback=callback, complete_callback=callback)
        subject.subscribe(next_callback=callback, error_callback=callback, complete_callback=callback)

        # Act
        await subject.error(exception)
        await subject.error(exception)
        subject.remove_all()
        await subject.error(exception)

        # Assert
        assert callback.call_count == 4
        assert callback.last_args == (exception,)
        assert callback.last_kwargs == {}

    # =================================

    async def test_emit_error_unicast(self) -> None:
        # Arrange
        exception = Exception()
        subject = Subject[Any]()
        callback = CallableMock.Sync()
        subject.subscribe(next_callback=callback, error_callback=callback, complete_callback=callback)

        # Act
        await subject.error(exception)
        subject.remove_all()
        await subject.error(exception)

        # Assert
        assert callback.call_count == 1
        assert callback.last_args == (exception,)
        assert callback.last_kwargs == {}

    # =================================

    async def test_emit_error_with_exceptions_and_different_values_multicast(self) -> None:
        # Arrange
        exception1 = Exception()
        exception2 = Exception()
        subject = Subject[Any]()
        callback = CallableMock.Sync(raise_exception=Exception())
        subject.subscribe(next_callback=callback, error_callback=callback, complete_callback=callback)
        subject.subscribe(next_callback=callback, error_callback=callback, complete_callback=callback)

        # Act
        await subject.error(exception1)
        await subject.error(exception2)
        subject.remove_all()
        await subject.error(exception1)

        # Assert
        assert callback.call_count == 4
        assert callback.last_args == (exception2,)
        assert callback.last_kwargs == {}

    # =================================

    async def test_emit_error_with_exceptions_and_different_values_unicast(self) -> None:
        # Arrange
        exception1 = Exception()
        exception2 = Exception()
        subject = Subject[Any]()
        callback = CallableMock.Sync(raise_exception=Exception())
        subject.subscribe(next_callback=callback, error_callback=callback, complete_callback=callback)

        # Act
        await subject.error(exception1)
        await subject.error(exception2)
        subject.remove_all()
        await subject.error(exception1)

        # Assert
        assert callback.call_count == 2
        assert callback.last_args == (exception2,)
        assert callback.last_kwargs == {}

    # =================================
    # Test Cases for _emit_complete()
    # =================================

    async def test_emit_complete_multicast(self) -> None:
        # Arrange
        subject = Subject[Any]()
        callback = CallableMock.Sync()
        subject.subscribe(next_callback=callback, error_callback=callback, complete_callback=None)
        subject.subscribe(next_callback=callback, error_callback=callback, complete_callback=callback)
        subject.subscribe(next_callback=callback, error_callback=callback, complete_callback=callback)

        # Act
        await subject.complete()
        await subject.complete()  # Call again to verify that subscribers are removed after completion.

        # Assert
        assert callback.call_count == 2
        assert callback.last_args == ()
        assert callback.last_kwargs == {}

    # =================================

    async def test_emit_complete_unicast(self) -> None:
        # Arrange
        subject = Subject[Any]()
        callback = CallableMock.Sync()
        subject.subscribe(next_callback=callback, error_callback=callback, complete_callback=callback)

        # Act
        await subject.complete()
        await subject.complete()  # Call again to verify that subscribers are removed after completion.

        # Assert
        assert callback.call_count == 1
        assert callback.last_args == ()
        assert callback.last_kwargs == {}

    # =================================

    async def test_emit_complete_with_exceptions_multicast(self) -> None:
        # Arrange
        subject = Subject[Any]()
        callback = CallableMock.Sync(raise_exception=Exception())
        subject.subscribe(next_callback=callback, error_callback=callback, complete_callback=callback)
        subject.subscribe(next_callback=callback, error_callback=callback, complete_callback=callback)

        # Act
        await subject.complete()
        await subject.complete()  # Call again to verify that subscribers are removed after completion.

        # Assert
        assert callback.call_count == 2
        assert callback.last_args == ()
        assert callback.last_kwargs == {}

    # =================================

    async def test_emit_complete_with_exceptions_unicast(self) -> None:
        # Arrange
        subject = Subject[Any]()
        callback = CallableMock.Sync(raise_exception=Exception())
        subject.subscribe(next_callback=callback, error_callback=callback, complete_callback=callback)

        # Act
        await subject.complete()
        await subject.complete()  # Call again to verify that subscribers are removed after completion.

        # Assert
        assert callback.call_count == 1
        assert callback.last_args == ()
        assert callback.last_kwargs == {}
