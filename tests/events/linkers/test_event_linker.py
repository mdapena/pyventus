from sys import gettrace
from types import EllipsisType

from _pytest.python_api import raises

from pyventus import PyventusException
from pyventus.events import EventLinker
from ... import EventFixtures, CallbackFixtures


class TestEventLinker:

    def test__init_subclass__(self):
        # ----------------------------------------------
        # Happy path tests (Arrange | Act | Assert)
        # ----------
        class CustomEventLinker(EventLinker, debug=True):
            pass

        assert CustomEventLinker._get_logger().debug_enabled
        assert EventLinker._get_logger().debug_enabled == bool(gettrace() is not None)

        event_handler = CustomEventLinker.subscribe(..., event_callback=CallbackFixtures.Sync())
        EventLinker.remove_all()

        assert EventLinker.get_registry() == {}
        assert CustomEventLinker.get_registry()[EllipsisType.__name__] == [event_handler]

        # ----------------------------------------------
        # Error path tests (Arrange | Act | Assert)
        # ----------
        with raises(PyventusException):

            class InvalidEventLinker1(EventLinker, debug="None"):
                pass

        with raises(PyventusException):

            class InvalidEventLinker2(EventLinker, max_event_handlers=0):
                pass

        with raises(PyventusException):

            class InvalidEventLinker3(EventLinker, default_success_callback=True):
                pass

        with raises(PyventusException):

            class InvalidEventLinker4(EventLinker, default_failure_callback=True):
                pass

    def test_get_event_name(self):
        # ----------------------------------------------
        # Happy path tests (Arrange | Act | Assert)
        # ----------
        assert EventFixtures.StringEvent == EventLinker.get_event_name(event=EventFixtures.StringEvent)
        assert EventFixtures.ExceptionEvent.__name__ == EventLinker.get_event_name(event=EventFixtures.ExceptionEvent)
        assert EventFixtures.DtcEvent1.__name__ == EventLinker.get_event_name(event=EventFixtures.DtcEvent1)
        assert EllipsisType.__name__ == EventLinker.get_event_name(event=...)

        # ----------------------------------------------
        # Error path tests (Arrange | Act | Assert)
        # ----------
        with raises(PyventusException):
            EventLinker.get_event_name(event=None)

        with raises(PyventusException):
            EventLinker.get_event_name(event=False)

        with raises(PyventusException):
            EventLinker.get_event_name(event="")

        with raises(PyventusException):
            EventLinker.get_event_name(event=str)

        with raises(PyventusException):
            EventLinker.get_event_name(event=EventFixtures.NonDtcEvent)

    def test_get_max_event_handlers(self):
        # ----------------------------------------------
        # Happy path tests (Arrange | Act | Assert)
        # ----------
        class CustomEventLinker1(EventLinker, max_event_handlers=1):
            pass  # pragma: no cover

        assert CustomEventLinker1.get_max_event_handlers() == 1

    def test_get_default_success_callback(self):
        # ----------------------------------------------
        # Happy path tests (Arrange | Act | Assert)
        # ----------
        success_callback = CallbackFixtures.Async()

        class CustomEventLinker1(EventLinker, default_success_callback=success_callback):
            pass  # pragma: no cover

        assert CustomEventLinker1.get_default_success_callback() == success_callback
        assert CustomEventLinker1.get_default_failure_callback() is None

    def test_get_default_failure_callback(self):
        # ----------------------------------------------
        # Happy path tests (Arrange | Act | Assert)
        # ----------
        failure_callback = CallbackFixtures.Async()

        class CustomEventLinker1(EventLinker, default_failure_callback=failure_callback):
            pass  # pragma: no cover

        assert CustomEventLinker1.get_default_success_callback() is None
        assert CustomEventLinker1.get_default_failure_callback() == failure_callback

    def test_get_registry(self):
        # ----------------------------------------------
        # Happy path tests (Arrange | Act | Assert)
        # ----------
        event_handler_1 = EventLinker.subscribe(..., EventFixtures.DtcEvent1, event_callback=CallbackFixtures.Sync())
        event_handler_2 = EventLinker.subscribe(
            EventFixtures.DtcEvent1,
            EventFixtures.DtcEvent2,
            event_callback=CallbackFixtures.Sync(),
        )

        # Try to modify the event registry manually
        EventLinker.get_registry()[EventFixtures.DtcEvent2.__name__].append(event_handler_1)

        assert len(EventLinker.get_registry().keys()) == 3
        assert (
            len(EventLinker.get_registry().get(EventFixtures.DtcEvent1.__name__, [])) == 2
            and event_handler_1 in EventLinker.get_registry().get(EventFixtures.DtcEvent1.__name__, [])
            and event_handler_2 in EventLinker.get_registry().get(EventFixtures.DtcEvent1.__name__, [])
        )
        assert len(
            EventLinker.get_registry().get(EllipsisType.__name__, [])
        ) == 1 and event_handler_1 in EventLinker.get_registry().get(EllipsisType.__name__, [])
        assert len(
            EventLinker.get_registry().get(EventFixtures.DtcEvent2.__name__, [])
        ) == 1 and event_handler_2 in EventLinker.get_registry().get(EventFixtures.DtcEvent2.__name__, [])

    def test_get_events(self):
        # ----------------------------------------------
        # Happy path tests (Arrange | Act | Assert)
        # ----------
        EventLinker.subscribe(EventFixtures.DtcEvent1, event_callback=CallbackFixtures.Sync())
        EventLinker.subscribe(..., EventFixtures.DtcEvent1, event_callback=CallbackFixtures.Async())
        EventLinker.subscribe(..., event_callback=CallbackFixtures.Sync())

        assert len(EventLinker.get_events()) == 2
        assert EllipsisType.__name__ in EventLinker.get_events()
        assert EventFixtures.DtcEvent1.__name__ in EventLinker.get_events()

    def test_get_event_handlers(self):
        # ----------------------------------------------
        # Happy path tests (Arrange | Act | Assert)
        # ----------
        event_handler_1 = EventLinker.subscribe(EventFixtures.DtcEvent1, ..., event_callback=CallbackFixtures.Sync())
        event_handler_2 = EventLinker.subscribe(
            EventFixtures.DtcEvent1, EventFixtures.DtcEvent2, ..., event_callback=CallbackFixtures.Async()
        )

        assert len(EventLinker.get_event_handlers()) == 2
        assert event_handler_1 in EventLinker.get_event_handlers()
        assert event_handler_2 in EventLinker.get_event_handlers()

    def test_get_events_by_event_handler(self):
        # ----------------------------------------------
        # Happy path tests (Arrange | Act | Assert)
        # ----------
        event_handler_1 = EventLinker.subscribe(EventFixtures.DtcEvent1, ..., event_callback=CallbackFixtures.Sync())
        event_handler_2 = EventLinker.subscribe(EventFixtures.DtcEvent1, event_callback=CallbackFixtures.Async())
        EventLinker.unsubscribe(..., event_handler=event_handler_2)

        assert (
            len(EventLinker.get_events_by_event_handler(event_handler_1)) == 2
            and EventFixtures.DtcEvent1.__name__ in EventLinker.get_events_by_event_handler(event_handler_1)
            and EllipsisType.__name__ in EventLinker.get_events_by_event_handler(event_handler_1)
        )
        assert EventLinker.get_events_by_event_handler(
            event_handler=event_handler_2,
        ) == [EventFixtures.DtcEvent1.__name__]

        # ----------------------------------------------
        # Error path tests (Arrange | Act | Assert)
        # ----------
        with raises(PyventusException):
            EventLinker.get_events_by_event_handler(event_handler=None)
        with raises(PyventusException):
            EventLinker.get_events_by_event_handler(event_handler=True)

    def test_get_event_handlers_by_events(self):
        # ----------------------------------------------
        # Happy path tests (Arrange | Act | Assert)
        # ----------
        event_handler_1 = EventLinker.subscribe(EventFixtures.DtcEvent1, ..., event_callback=CallbackFixtures.Sync())
        event_handler_2 = EventLinker.subscribe(
            EventFixtures.DtcEvent1, EventFixtures.DtcEvent2, event_callback=CallbackFixtures.Async()
        )

        assert (
            len(EventLinker.get_event_handlers_by_events(EventFixtures.DtcEvent1)) == 2
            and event_handler_1 in EventLinker.get_event_handlers_by_events(EventFixtures.DtcEvent1)
            and event_handler_2 in EventLinker.get_event_handlers_by_events(EventFixtures.DtcEvent1)
        )
        assert (
            len(EventLinker.get_event_handlers_by_events(EventFixtures.DtcEvent1, ...)) == 2
            and event_handler_1 in EventLinker.get_event_handlers_by_events(EventFixtures.DtcEvent1, ...)
            and event_handler_2 in EventLinker.get_event_handlers_by_events(EventFixtures.DtcEvent1, ...)
        )
        assert EventLinker.get_event_handlers_by_events(..., ..., Ellipsis) == [event_handler_1]
        assert EventLinker.get_event_handlers_by_events(EventFixtures.DtcEvent2) == [event_handler_2]
        assert len(EventLinker.get_event_handlers_by_events("...")) == 0

        # ----------------------------------------------
        # Error path tests (Arrange | Act | Assert)
        # ----------
        with raises(PyventusException):
            EventLinker.get_event_handlers_by_events()
        with raises(PyventusException):
            EventLinker.get_event_handlers_by_events(True)

    def test_once_decorator(self):
        # ----------------------------------------------
        # Happy path tests (Arrange | Act | Assert)
        # ----------
        @EventLinker.once(EventFixtures.StringEvent, EventFixtures.ExceptionEvent, EventFixtures.DtcEvent1)
        def event_callback1(*args, **kwargs):  # Multiple event subscription
            pass  # pragma: no cover

        @EventLinker.once(..., force_async=True)
        async def event_callback2(*args, **kwargs):  # Single event subscription
            pass  # pragma: no cover

        assert len(EventLinker.get_event_handlers()) == 2

        event_handler1 = EventLinker.get_event_handlers_by_events(EventFixtures.StringEvent)[0]
        assert event_handler1 and event_handler1.once and not event_handler1.force_async  # Flag validations

        event_handler2 = EventLinker.get_event_handlers_by_events(...)[0]
        assert event_handler2 and event_handler2.once and event_handler2.force_async  # Flag validations

        assert event_callback2 is EventLinker.once(EventFixtures.EmptyEvent)(event_callback2)  # Check return value

        # ----------------------------------------------
        # Error path tests (Arrange | Act | Assert)
        # ----------
        with raises(PyventusException):

            @EventLinker.once()
            def event_callback3():
                pass  # pragma: no cover

        assert len(EventLinker.get_event_handlers()) == 3

    def test_once_context_manager(self):
        # ----------------------------------------------
        # Happy path tests (Arrange | Act | Assert)
        # ----------
        event_callback = CallbackFixtures.Sync()
        success_callback = CallbackFixtures.Async()
        failure_callback = CallbackFixtures.Sync()

        with EventLinker.once(
            EventFixtures.StringEvent, EventFixtures.ExceptionEvent, EventFixtures.DtcEvent1
        ) as linker:  # Multiple event subscription
            linker.on_event(event_callback)
            linker.on_success(success_callback)
            linker.on_failure(failure_callback)

        with EventLinker.once(..., force_async=True) as linker:  # Single event subscription
            linker.on_event(event_callback)
            linker.on_failure(failure_callback)

        assert len(EventLinker.get_event_handlers()) == 2

        event_handler1 = EventLinker.get_event_handlers_by_events(EventFixtures.DtcEvent1)[0]
        assert event_handler1 and event_handler1.once and not event_handler1.force_async  # Flag validations
        assert (
            event_handler1._event_callback is event_callback
            and event_handler1._success_callback is success_callback
            and event_handler1._failure_callback is failure_callback
        )

        event_handler2 = EventLinker.get_event_handlers_by_events(Ellipsis)[0]
        assert event_handler2 and event_handler2.once and event_handler2.force_async  # Flag validations
        assert (
            event_handler2._event_callback is event_callback
            and event_handler2._success_callback is None
            and event_handler1._failure_callback is failure_callback
        )

        # ----------------------------------------------
        # Error path tests (Arrange | Act | Assert)
        # ----------
        with raises(PyventusException):

            with EventLinker.once(EventFixtures.EmptyEvent) as linker:
                linker.on_success(success_callback)
                linker.on_failure(failure_callback)

        assert len(EventLinker.get_event_handlers()) == 2

    def test_on_decorator(self):
        # ----------------------------------------------
        # Happy path tests (Arrange | Act | Assert)
        # ----------
        @EventLinker.on(EventFixtures.StringEvent, EventFixtures.ExceptionEvent, EventFixtures.DtcEvent1)
        def event_callback1(*args, **kwargs):  # Multiple event subscription
            pass  # pragma: no cover

        @EventLinker.on(..., force_async=True)
        async def event_callback2(*args, **kwargs):  # Single event subscription
            pass  # pragma: no cover

        assert len(EventLinker.get_event_handlers()) == 2

        event_handler1 = EventLinker.get_event_handlers_by_events(EventFixtures.ExceptionEvent)[0]
        assert event_handler1 and not event_handler1.once and not event_handler1.force_async  # Flag validations

        event_handler2 = EventLinker.get_event_handlers_by_events(Ellipsis)[0]
        assert event_handler2 and not event_handler2.once and event_handler2.force_async  # Flag validations

        assert event_callback2 is EventLinker.on(EventFixtures.EmptyEvent)(event_callback2)  # Check return value

        # ----------------------------------------------
        # Error path tests (Arrange | Act | Assert)
        # ----------
        with raises(PyventusException):

            @EventLinker.on()
            def event_callback3():
                pass  # pragma: no cover

        assert len(EventLinker.get_event_handlers()) == 3

    def test_on_context_manager(self):
        # ----------------------------------------------
        # Happy path tests (Arrange | Act | Assert)
        # ----------
        event_callback = CallbackFixtures.Sync()
        success_callback = CallbackFixtures.Async()
        failure_callback = CallbackFixtures.Sync()

        with EventLinker.on(
            EventFixtures.StringEvent, EventFixtures.ExceptionEvent, EventFixtures.DtcEvent1
        ) as linker:  # Multiple event subscription
            linker.on_event(event_callback)
            linker.on_success(success_callback)
            linker.on_failure(failure_callback)

        with EventLinker.on(..., force_async=True) as linker:  # Single event subscription
            linker.on_event(event_callback)
            linker.on_failure(failure_callback)

        assert len(EventLinker.get_event_handlers()) == 2

        event_handler1 = EventLinker.get_event_handlers_by_events(EventFixtures.StringEvent)[0]
        assert event_handler1 and not event_handler1.once and not event_handler1.force_async  # Flag validations
        assert (  # Callback validations
            event_handler1._event_callback is event_callback
            and event_handler1._success_callback is success_callback
            and event_handler1._failure_callback is failure_callback
        )

        event_handler2 = EventLinker.get_event_handlers_by_events(...)[0]
        assert event_handler2 and not event_handler2.once and event_handler2.force_async  # Flag validations
        assert (  # Callback validations
            event_handler2._event_callback is event_callback
            and event_handler2._success_callback is None
            and event_handler1._failure_callback is failure_callback
        )

        # ----------------------------------------------
        # Error path tests (Arrange | Act | Assert)
        # ----------
        with raises(PyventusException):

            with EventLinker.on(EventFixtures.EmptyEvent) as linker:
                linker.on_success(success_callback)
                linker.on_failure(failure_callback)

        assert len(EventLinker.get_event_handlers()) == 2

    def test_subscribe(self):
        # ----------------------------------------------
        # Happy path tests (Arrange | Act | Assert)
        # ----------
        event_callback = CallbackFixtures.Sync()
        success_callback = CallbackFixtures.Async()
        failure_callback = CallbackFixtures.Sync()

        event_handler1 = EventLinker.subscribe(
            EventFixtures.DtcEvent1,
            event_callback=event_callback,
            success_callback=success_callback,
        )
        event_handler2 = EventLinker.subscribe(
            ...,
            EventFixtures.DtcWithValidation,
            event_callback=event_callback,
            failure_callback=failure_callback,
        )
        event_handler3 = EventLinker.subscribe(
            EventFixtures.StringEvent,
            EventFixtures.DtcWithValidation,
            event_callback=event_callback,
            success_callback=success_callback,
            failure_callback=failure_callback,
        )
        event_handler4 = EventLinker.subscribe(
            Ellipsis,
            PyventusException,
            ...,
            event_callback=event_callback,
            once=True,
        )
        event_handler5 = EventLinker.subscribe(
            Exception,
            Exception,
            event_callback=event_callback,
            force_async=True,
        )
        event_handler6 = EventLinker.subscribe(
            "Exception",
            event_callback=event_callback,
            force_async=True,
            once=True,
        )

        # Assert
        assert event_handler1 != event_handler2 != event_handler3 != event_handler4 != event_handler5 != event_handler6
        assert (
            event_handler1._event_callback is event_callback
            and event_handler1._success_callback is success_callback
            and event_handler1._failure_callback is None
            and not event_handler1.once
            and not event_handler1.force_async
        )
        assert (
            event_handler2._event_callback is event_callback
            and event_handler2._success_callback is None
            and event_handler2._failure_callback is failure_callback
            and not event_handler2.once
            and not event_handler2.force_async
        )
        assert (
            event_handler3._event_callback is event_callback
            and event_handler3._success_callback is success_callback
            and event_handler3._failure_callback is failure_callback
            and not event_handler3.once
            and not event_handler3.force_async
        )
        assert (
            event_handler4._event_callback is event_callback
            and event_handler4._success_callback is None
            and event_handler4._failure_callback is None
            and event_handler4.once
            and not event_handler4.force_async
        )
        assert (
            event_handler5._event_callback is event_callback
            and event_handler5._success_callback is None
            and event_handler5._failure_callback is None
            and not event_handler5.once
            and event_handler5.force_async
        )
        assert (
            event_handler6._event_callback is event_callback
            and event_handler6._success_callback is None
            and event_handler6._failure_callback is None
            and event_handler6.once
            and event_handler6.force_async
        )

        assert len(EventLinker.get_events()) == 6
        assert len(EventLinker.get_event_handlers()) == 6

        assert len(
            EventLinker.get_registry().get(EventFixtures.DtcEvent1.__name__, [])
        ) == 1 and event_handler1 in EventLinker.get_registry().get(EventFixtures.DtcEvent1.__name__, [])
        assert len(
            EventLinker.get_registry().get(EventFixtures.StringEvent, [])
        ) == 1 and event_handler3 in EventLinker.get_registry().get(EventFixtures.StringEvent, [])
        assert len(
            EventLinker.get_registry().get(PyventusException.__name__, [])
        ) == 1 and event_handler4 in EventLinker.get_registry().get(PyventusException.__name__, [])
        assert (
            len(EventLinker.get_registry().get(EllipsisType.__name__, [])) == 2
            and event_handler2 in EventLinker.get_registry().get(EllipsisType.__name__, [])
            and event_handler4 in EventLinker.get_registry().get(EllipsisType.__name__, [])
        )
        assert (
            len(EventLinker.get_registry().get(EventFixtures.DtcWithValidation.__name__, [])) == 2
            and event_handler2 in EventLinker.get_registry().get(EventFixtures.DtcWithValidation.__name__, [])
            and event_handler3 in EventLinker.get_registry().get(EventFixtures.DtcWithValidation.__name__, [])
        )
        assert (
            len(EventLinker.get_registry().get(Exception.__name__, [])) == 2
            and event_handler5 in EventLinker.get_registry().get(Exception.__name__, [])
            and event_handler6 in EventLinker.get_registry().get(Exception.__name__, [])
        )

        # ----------------------------------------------
        # Error path tests (Arrange | Act | Assert)
        # ----------
        with raises(PyventusException):
            EventLinker.subscribe(event_callback=event_callback)

        assert len(EventLinker.get_event_handlers()) == 6

    def test_subscribe_with_max_event_handler(self):
        # ----------------------------------------------
        # Happy path tests (Arrange | Act | Assert)
        # ----------
        class CustomEventLinker(EventLinker, max_event_handlers=2):
            pass  # pragma: no cover

        event_callback = CallbackFixtures.Sync()

        CustomEventLinker.subscribe(EventFixtures.DtcEvent1, event_callback=event_callback)
        CustomEventLinker.subscribe(EventFixtures.DtcEvent1, ..., event_callback=event_callback)

        # Remove and add new event handlers
        CustomEventLinker.remove_event(EventFixtures.DtcEvent1)
        CustomEventLinker.subscribe(EventFixtures.DtcEvent1, ..., event_callback=event_callback)
        CustomEventLinker.subscribe(EventFixtures.DtcEvent1, EventFixtures.DtcEvent1, event_callback=event_callback)

        assert len(CustomEventLinker.get_registry().get(EllipsisType.__name__, [])) == 2
        assert len(CustomEventLinker.get_registry().get(EventFixtures.DtcEvent1.__name__, [])) == 2

        # ----------------------------------------------
        # Error path tests (Arrange | Act | Assert)
        # ----------
        with raises(PyventusException):
            CustomEventLinker.subscribe(EventFixtures.StringEvent, ..., event_callback=event_callback)

        assert len(CustomEventLinker.get_registry().get(EllipsisType.__name__, [])) == 2
        assert len(CustomEventLinker.get_registry().get(EventFixtures.DtcEvent1.__name__, [])) == 2
        assert len(CustomEventLinker.get_registry().get(EventFixtures.StringEvent, [])) == 0

    def test_subscribe_with_default_success_callback(self):
        # ----------------------------------------------
        # Happy path tests (Arrange | Act | Assert)
        # ----------
        event_callback = CallbackFixtures.Sync()
        default_success_callback = CallbackFixtures.Sync()
        success_callback = CallbackFixtures.Async()

        class CustomEventLinker(EventLinker, default_success_callback=default_success_callback):
            pass  # pragma: no cover

        event_handler1 = EventLinker.subscribe(..., event_callback=event_callback)
        event_handler2 = CustomEventLinker.subscribe(..., event_callback=event_callback)
        event_handler3 = CustomEventLinker.subscribe(
            ..., event_callback=event_callback, success_callback=success_callback
        )

        assert (  # Default EventLinker
            event_handler1._event_callback == event_callback
            and event_handler1._success_callback is None
            and event_handler1._failure_callback is None
        )
        assert (
            event_handler2._event_callback == event_callback
            and event_handler2._success_callback is default_success_callback
            and event_handler2._failure_callback is None
        )
        assert (
            event_handler3._event_callback == event_callback
            and event_handler3._success_callback is success_callback
            and event_handler3._failure_callback is None
        )

    def test_subscribe_with_default_failure_callback(self):
        # ----------------------------------------------
        # Happy path tests (Arrange | Act | Assert)
        # ----------
        event_callback = CallbackFixtures.Sync()
        default_failure_callback = CallbackFixtures.Sync()
        failure_callback = CallbackFixtures.Async()

        class CustomEventLinker(EventLinker, default_failure_callback=default_failure_callback):
            pass  # pragma: no cover

        event_handler1 = EventLinker.subscribe(..., event_callback=event_callback)
        event_handler2 = CustomEventLinker.subscribe(..., event_callback=event_callback)
        event_handler3 = CustomEventLinker.subscribe(
            ..., event_callback=event_callback, failure_callback=failure_callback
        )

        assert (  # Default EventLinker
            event_handler1._event_callback == event_callback
            and event_handler1._success_callback is None
            and event_handler1._failure_callback is None
        )
        assert (
            event_handler2._event_callback == event_callback
            and event_handler2._success_callback is None
            and event_handler2._failure_callback is default_failure_callback
        )
        assert (
            event_handler3._event_callback == event_callback
            and event_handler3._success_callback is None
            and event_handler3._failure_callback is failure_callback
        )

    def test_unsubscribe(self):
        # ----------------------------------------------
        # Happy path tests (Arrange | Act | Assert)
        # ----------
        event_callback = CallbackFixtures.Sync()

        event_handler1 = EventLinker.subscribe(EventFixtures.DtcEvent1, event_callback=event_callback)
        event_handler2 = EventLinker.subscribe(..., EventFixtures.DtcEvent1, event_callback=event_callback)
        event_handler3 = EventLinker.subscribe(EventFixtures.StringEvent, event_callback=event_callback)

        result1 = EventLinker.unsubscribe(..., EventFixtures.DtcEvent1, event_handler=event_handler1)
        result2 = EventLinker.unsubscribe(EventFixtures.StringEvent, event_handler=event_handler2)
        result3 = EventLinker.unsubscribe(EventFixtures.StringEvent, event_handler=event_handler3)

        assert result1 and not result2 and result3
        assert len(EventLinker.get_events()) == 2
        assert len(EventLinker.get_event_handlers()) == 1
        assert EventLinker.get_registry().get(EllipsisType.__name__, []) == [event_handler2]
        assert EventLinker.get_registry().get(EventFixtures.DtcEvent1.__name__, []) == [event_handler2]

        # ----------------------------------------------
        # Error path tests (Arrange | Act | Assert)
        # ----------
        with raises(PyventusException):
            EventLinker.unsubscribe(event_handler=event_handler2)
        with raises(PyventusException):
            EventLinker.unsubscribe(..., event_handler=None)
        with raises(PyventusException):
            EventLinker.unsubscribe(..., event_handler=True)

        assert len(EventLinker.get_events()) == 2
        assert len(EventLinker.get_event_handlers()) == 1

    def test_remove_event_handler(self):
        # ----------------------------------------------
        # Happy path tests (Arrange | Act | Assert)
        # ----------
        event_callback = CallbackFixtures.Sync()

        event_handler1 = EventLinker.subscribe(EventFixtures.DtcWithValidation, event_callback=event_callback)
        event_handler2 = EventLinker.subscribe(..., EventFixtures.DtcWithValidation, event_callback=event_callback)
        event_handler3 = EventLinker.subscribe(
            EventFixtures.StringEvent,
            EventFixtures.DtcWithValidation,
            event_callback=event_callback,
        )

        result1 = EventLinker.remove_event_handler(event_handler=event_handler2)
        result2 = EventLinker.remove_event_handler(event_handler=event_handler2)
        assert result1 and not result2
        assert (
            len(EventLinker.get_events()) == 2
            and EventFixtures.DtcWithValidation.__name__ in EventLinker.get_events()
            and EventFixtures.StringEvent in EventLinker.get_events()
        )
        assert (
            len(EventLinker.get_event_handlers()) == 2
            and event_handler1 in EventLinker.get_event_handlers()
            and event_handler2 not in EventLinker.get_event_handlers()
            and event_handler3 in EventLinker.get_event_handlers()
        )

        result3 = EventLinker.remove_event_handler(event_handler=event_handler3)
        result4 = EventLinker.remove_event_handler(event_handler=event_handler3)
        assert result3 and not result4
        assert (
            len(EventLinker.get_events()) == 1 and EventFixtures.DtcWithValidation.__name__ in EventLinker.get_events()
        )
        assert (
            len(EventLinker.get_event_handlers()) == 1
            and event_handler1 in EventLinker.get_event_handlers()
            and event_handler2 not in EventLinker.get_event_handlers()
            and event_handler3 not in EventLinker.get_event_handlers()
        )

        result5 = EventLinker.remove_event_handler(event_handler=event_handler1)
        result6 = EventLinker.remove_event_handler(event_handler=event_handler1)
        assert result5 and not result6
        assert EventLinker.get_registry() == {}

        # ----------------------------------------------
        # Error path tests (Arrange | Act | Assert)
        # ----------
        with raises(PyventusException):
            EventLinker.remove_event_handler(event_handler=None)
        with raises(PyventusException):
            EventLinker.remove_event_handler(event_handler=True)

    def test_remove_event(self):
        # ----------------------------------------------
        # Happy path tests (Arrange | Act | Assert)
        # ----------
        event_callback = CallbackFixtures.Sync()

        event_handler1 = EventLinker.subscribe(EventFixtures.DtcWithValidation, event_callback=event_callback)
        event_handler2 = EventLinker.subscribe(..., EventFixtures.DtcWithValidation, event_callback=event_callback)
        event_handler3 = EventLinker.subscribe(
            EventFixtures.StringEvent,
            EventFixtures.DtcWithValidation,
            event_callback=event_callback,
        )

        result1 = EventLinker.remove_event(event=EllipsisType.__name__)  # Remove Ellipsis using its string name
        result2 = EventLinker.remove_event(event=Ellipsis)
        result3 = EventLinker.remove_event(event=EventFixtures.DtcEvent1)

        assert result1 and not result2 and not result3
        assert (
            len(EventLinker.get_events()) == 2
            and EventFixtures.DtcWithValidation.__name__ in EventLinker.get_events()
            and EventFixtures.StringEvent in EventLinker.get_events()
        )
        assert (
            len(EventLinker.get_event_handlers()) == 3
            and event_handler1 in EventLinker.get_event_handlers()
            and event_handler2 in EventLinker.get_event_handlers()
            and event_handler3 in EventLinker.get_event_handlers()
        )

        result4 = EventLinker.remove_event(event=EventFixtures.DtcWithValidation)
        result5 = EventLinker.remove_event(event=EventFixtures.DtcWithValidation)

        assert result4 and not result5
        assert len(EventLinker.get_events()) == 1 and EventFixtures.StringEvent in EventLinker.get_events()
        assert len(EventLinker.get_event_handlers()) == 1 and event_handler3 in EventLinker.get_event_handlers()

        # ----------------------------------------------
        # Error path tests (Arrange | Act | Assert)
        # ----------
        with raises(PyventusException):
            EventLinker.remove_event(event=None)

        assert len(EventLinker.get_events()) == 1
        assert len(EventLinker.get_event_handlers()) == 1

    def test_remove_all(self):
        # ----------------------------------------------
        # Happy path tests (Arrange | Act | Assert)
        # ----------
        event_callback = CallbackFixtures.Sync()

        EventLinker.subscribe(EventFixtures.DtcWithValidation, event_callback=event_callback)
        EventLinker.subscribe(..., EventFixtures.DtcWithValidation, event_callback=event_callback)
        EventLinker.subscribe(
            EventFixtures.StringEvent,
            EventFixtures.DtcWithValidation,
            event_callback=event_callback,
        )

        result1 = EventLinker.remove_all()
        result2 = EventLinker.remove_all()

        assert result1 and not result2
        assert EventLinker.get_registry() == {}
