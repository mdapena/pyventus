from _pytest.python_api import raises

from pyventus import Event, EventLinker, PyventusException, EventHandler, EventEmitter
from pyventus.core.loggers import Logger
from .. import EventFixtures, CallbackFixtures


class TestEventLinker:
    def test_get_events(self, clean_event_linker: bool):
        # Arrange | Act
        EventLinker.subscribe(EventFixtures.CustomEvent1, event_callback=CallbackFixtures.Sync())
        EventLinker.subscribe(EventFixtures.CustomEvent1, event_callback=CallbackFixtures.Async())
        EventLinker.subscribe(Event, event_callback=CallbackFixtures.Sync())

        # Assert
        assert len(EventLinker.get_events()) == 2
        assert Event.__name__ in EventLinker.get_events()
        assert EventFixtures.CustomEvent1.__name__ in EventLinker.get_events()

    def test_get_event_handlers(self, clean_event_linker: bool):
        # Arrange | Act
        event_handler_1 = EventLinker.subscribe(
            Event, EventFixtures.CustomEvent1, event_callback=CallbackFixtures.Sync()
        )
        event_handler_2 = EventLinker.subscribe(
            EventFixtures.CustomEvent1, EventFixtures.CustomEvent2, event_callback=CallbackFixtures.Async()
        )

        # Assert
        assert len(EventLinker.get_event_handlers()) == 2
        assert event_handler_1 in EventLinker.get_event_handlers()
        assert event_handler_2 in EventLinker.get_event_handlers()

    def test_get_event_registry(self, clean_event_linker: bool):
        # Arrange | Act
        event_handler_1 = EventLinker.subscribe(
            Event, EventFixtures.CustomEvent1, event_callback=CallbackFixtures.Sync()
        )
        event_handler_2 = EventLinker.subscribe(
            EventFixtures.CustomEvent1, EventFixtures.CustomEvent2, event_callback=CallbackFixtures.Async()
        )

        # Assert
        assert len(EventLinker.get_event_registry().keys()) == 3

        assert len(EventLinker.get_event_registry()[Event.__name__]) == 1
        assert event_handler_1 in EventLinker.get_event_registry()[Event.__name__]

        assert len(EventLinker.get_event_registry()[EventFixtures.CustomEvent1.__name__]) == 2
        assert event_handler_1 in EventLinker.get_event_registry()[EventFixtures.CustomEvent1.__name__]
        assert event_handler_2 in EventLinker.get_event_registry()[EventFixtures.CustomEvent1.__name__]

        assert len(EventLinker.get_event_registry()[EventFixtures.CustomEvent2.__name__]) == 1
        assert event_handler_2 in EventLinker.get_event_registry()[EventFixtures.CustomEvent1.__name__]

        # Act
        EventLinker.get_event_registry().pop(Event.__name__)  # type: ignore
        EventLinker.get_event_registry()[Event.__name__].append(event_handler_2)

        # Assert
        assert len(EventLinker.get_event_registry().keys()) == 3
        assert len(EventLinker.get_event_registry()[Event.__name__]) == 1

    def test_get_max_event_handlers(self, clean_event_linker: bool):
        # Arrange | Act
        class CustomEventLinker(EventLinker, max_event_handlers=2):
            pass  # pragma: no cover

        # Assert
        assert EventLinker.get_max_event_handlers() is None
        assert CustomEventLinker.get_max_event_handlers() == 2

    def test_get_default_success_callback(self, clean_event_linker):
        # Arrange | Act
        success_callback = CallbackFixtures.Async()

        class CustomEventLinker(EventLinker, default_success_callback=success_callback):
            pass  # pragma: no cover

        # Assert
        assert EventLinker.get_default_success_callback() is None
        assert EventLinker.get_default_failure_callback() is None
        assert CustomEventLinker.get_default_success_callback() == success_callback
        assert CustomEventLinker.get_default_failure_callback() is None

    def test_get_default_failure_callback(self, clean_event_linker):
        # Arrange | Act
        failure_callback = CallbackFixtures.Async()

        class CustomEventLinker(EventLinker, default_failure_callback=failure_callback):
            pass  # pragma: no cover

        # Assert
        assert EventLinker.get_default_success_callback() is None
        assert EventLinker.get_default_failure_callback() is None
        assert CustomEventLinker.get_default_success_callback() is None
        assert CustomEventLinker.get_default_failure_callback() == failure_callback

    def test_get_events_by_handler(self, clean_event_linker: bool):
        # Arrange | Act | Assert
        with raises(PyventusException):
            EventLinker.get_events_by_handler(event_handler=None)  # type: ignore

        # Arrange | Act
        event_handler_1 = EventLinker.subscribe(
            Event, EventFixtures.CustomEvent1, event_callback=CallbackFixtures.Sync()
        )
        event_handler_2 = EventLinker.subscribe(EventFixtures.CustomEvent2, event_callback=CallbackFixtures.Async())

        # Assert
        assert len(EventLinker.get_events_by_handler(event_handler=event_handler_1)) == 2
        assert Event.__name__ in EventLinker.get_events_by_handler(event_handler=event_handler_1)
        assert EventFixtures.CustomEvent1.__name__ in EventLinker.get_events_by_handler(event_handler=event_handler_1)
        assert len(EventLinker.get_events_by_handler(event_handler=event_handler_2)) == 1
        assert EventFixtures.CustomEvent2.__name__ in EventLinker.get_events_by_handler(event_handler=event_handler_2)

        # Arrange | Act
        event_handler_3 = EventHandler(event_callback=CallbackFixtures.Sync())

        # Assert
        assert len(EventLinker.get_events_by_handler(event_handler=event_handler_3)) == 0

    def test_get_handlers_by_events(self, clean_event_linker: bool):
        # Arrange | Act | Assert
        with raises(PyventusException):
            EventLinker.get_handlers_by_events()
        with raises(PyventusException):
            EventLinker.get_handlers_by_events("testing", str)  # type: ignore
        with raises(PyventusException):
            EventLinker.get_handlers_by_events(Event, BaseException)  # type: ignore
        assert len(EventLinker.get_handlers_by_events(Event)) == 0

        # Arrange | Act
        event_handler_1 = EventLinker.subscribe(
            Event, EventFixtures.CustomEvent1, event_callback=CallbackFixtures.Sync()
        )
        event_handler_2 = EventLinker.subscribe(
            EventFixtures.CustomEvent1, EventFixtures.CustomEvent2, event_callback=CallbackFixtures.Async()
        )

        # Assert
        assert len(EventLinker.get_handlers_by_events(Event)) == 1
        assert len(EventLinker.get_handlers_by_events(Event, Event, Event)) == 1
        assert event_handler_1 in EventLinker.get_handlers_by_events(Event)
        assert len(EventLinker.get_handlers_by_events(EventFixtures.CustomEvent1)) == 2
        assert event_handler_1 in EventLinker.get_handlers_by_events(EventFixtures.CustomEvent1)
        assert event_handler_2 in EventLinker.get_handlers_by_events(EventFixtures.CustomEvent1)
        assert len(EventLinker.get_handlers_by_events(EventFixtures.CustomEvent2)) == 1
        assert event_handler_2 in EventLinker.get_handlers_by_events(EventFixtures.CustomEvent2)
        assert len(EventLinker.get_handlers_by_events("None")) == 0
        assert (
            len(
                EventLinker.get_handlers_by_events(Event, EventFixtures.CustomEvent1, Event, EventFixtures.CustomEvent1)
            )
            == 2
        )

    def test_event_linkage_wrapper(self, clean_event_linker: bool):
        # Arrange
        event_callback1 = CallbackFixtures.Sync()

        # Act
        wrapper1 = EventLinker.EventLinkageWrapper(
            EventFixtures.CustomEvent1,
            event_linker=EventLinker,
            once=False,
        )

        # Assert
        assert not EventLinker.get_event_registry()

        # Act | Assert
        assert event_callback1 == wrapper1(event_callback1)

        # Assert
        assert wrapper1._success_callback is None
        assert wrapper1._failure_callback is None
        assert wrapper1._event_callback == event_callback1
        assert len(EventLinker.get_handlers_by_events(EventFixtures.CustomEvent1)) == 1
        assert not EventLinker.get_handlers_by_events(EventFixtures.CustomEvent1)[0].once
        assert len(EventLinker.get_events()) == 1

        # Arrange
        event_callback2 = CallbackFixtures.Sync()
        success_callback2 = CallbackFixtures.Async()
        failure_callback2 = CallbackFixtures.Sync()

        # Act
        wrapper2 = EventLinker.EventLinkageWrapper("StringEvent", event_linker=EventLinker, once=True)

        # Act
        with wrapper2 as linker:
            linker.on_event(event_callback2)
            linker.on_success(success_callback2)
            linker.on_failure(failure_callback2)

        # Assert
        assert wrapper2._event_callback == event_callback2
        assert wrapper2._success_callback == success_callback2
        assert wrapper2._failure_callback == failure_callback2
        assert len(EventLinker.get_handlers_by_events("StringEvent")) == 1
        assert EventLinker.get_handlers_by_events("StringEvent")[0].once
        assert len(EventLinker.get_events()) == 2

    def test_once_as_decorator(self, clean_event_linker: bool):
        # Arrange | Act | Assert
        with raises(PyventusException):

            @EventLinker.once()
            def invalid_once_callback(event: Event):  # pragma: no cover
                pass  # pragma: no cover

        # Arrange | Act
        @EventLinker.once(Event, Exception)
        def first_once_callback(*args, **kwargs):
            pass  # pragma: no cover

        @EventLinker.once(Exception)
        async def second_once_callback(exception: Exception):
            pass  # pragma: no cover

        # Assert
        assert len(EventLinker.get_handlers_by_events(Event)) == 1
        assert EventLinker.get_handlers_by_events(Event)[0].once
        assert len(EventLinker.get_handlers_by_events(Exception)) == 2
        assert EventLinker.get_handlers_by_events(Exception)[0].once
        assert EventLinker.get_handlers_by_events(Exception)[1].once
        assert len(EventLinker.get_event_handlers()) == 2

    def test_once_as_context_manager(self, clean_event_linker: bool):
        # Arrange | Act | Assert
        with raises(PyventusException):
            with EventLinker.once() as linker:

                @linker.on_event
                def event_callback(*args, **kwargs):
                    pass  # pragma: no cover

        # Arrange | Act | Assert
        with raises(PyventusException):
            with EventLinker.once(Event) as linker:
                pass  # pragma: no cover

        # Arrange | Act
        with EventLinker.once(Event, Exception) as linker:

            @linker.on_event
            def first_event_callback(*args, **kwargs):
                pass  # pragma: no cover

            @linker.on_success
            async def first_success_callback(*args, **kwargs):
                pass  # pragma: no cover

            @linker.on_failure
            def first_failure_callback(*args, **kwargs):
                pass  # pragma: no cover

        with EventLinker.once(Exception) as linker:

            @linker.on_event
            async def second_event_callback(exception: Exception):
                pass  # pragma: no cover

            @linker.on_success
            def second_success_callback():
                pass  # pragma: no cover

            @linker.on_failure
            async def second_failure_callback(exception: Exception):
                pass  # pragma: no cover

        # Assert
        assert len(EventLinker.get_handlers_by_events(Event)) == 1
        assert EventLinker.get_handlers_by_events(Event)[0].once
        assert len(EventLinker.get_handlers_by_events(Exception)) == 2
        assert EventLinker.get_handlers_by_events(Exception)[0].once
        assert EventLinker.get_handlers_by_events(Exception)[1].once
        assert len(EventLinker.get_event_handlers()) == 2

    def test_on_as_decorator(self, clean_event_linker: bool):
        # Arrange | Act | Assert
        with raises(PyventusException):

            @EventLinker.on()
            def invalid_once_callback(event: Event):  # pragma: no cover
                pass  # pragma: no cover

        # Arrange | Act
        @EventLinker.on(Event, EventFixtures.CustomEvent1)
        def first_once_callback(*args, **kwargs):
            pass  # pragma: no cover

        @EventLinker.on(Exception)
        async def second_once_callback(exception: Exception):
            pass  # pragma: no cover

        # Assert
        assert len(EventLinker.get_handlers_by_events(Event)) == 1
        assert not EventLinker.get_handlers_by_events(Event)[0].once
        assert len(EventLinker.get_handlers_by_events(EventFixtures.CustomEvent1)) == 1
        assert EventLinker.get_handlers_by_events(EventFixtures.CustomEvent1) == EventLinker.get_handlers_by_events(
            Event
        )
        assert len(EventLinker.get_handlers_by_events(Exception)) == 1
        assert not EventLinker.get_handlers_by_events(Exception)[0].once
        assert len(EventLinker.get_event_handlers()) == 2

    def test_on_as_context_manager(self, clean_event_linker: bool):
        # Arrange | Act | Assert
        with raises(PyventusException):
            with EventLinker.on() as linker:

                @linker.on_event
                def invalid_once_callback(event: Event):
                    pass  # pragma: no cover

        with raises(PyventusException):
            with EventLinker.on(Event) as linker:
                pass  # pragma: no cover

        # Arrange | Act
        with EventLinker.on(Event, EventFixtures.CustomEvent1) as linker:

            @linker.on_event
            def first_event_callback(*args, **kwargs):
                pass  # pragma: no cover

            @linker.on_failure
            def first_failure_callback(*args, **kwargs):
                pass  # pragma: no cover

        with EventLinker.on(Exception) as linker:

            @linker.on_event
            async def second_event_callback(exception: Exception):
                pass  # pragma: no cover

        # Assert
        assert len(EventLinker.get_handlers_by_events(Event)) == 1
        assert not EventLinker.get_handlers_by_events(Event)[0].once
        assert len(EventLinker.get_handlers_by_events(EventFixtures.CustomEvent1)) == 1
        assert EventLinker.get_handlers_by_events(EventFixtures.CustomEvent1) == EventLinker.get_handlers_by_events(
            Event
        )
        assert len(EventLinker.get_handlers_by_events(Exception)) == 1
        assert not EventLinker.get_handlers_by_events(Exception)[0].once
        assert len(EventLinker.get_event_handlers()) == 2

    def test_subscribe(self, clean_event_linker: bool):
        # Arrange | Act | Assert
        with raises(PyventusException):
            EventLinker.subscribe(event_callback=CallbackFixtures.Sync())

        event_callback = CallbackFixtures.Sync()

        # Arrange | Act
        event_handler1 = EventLinker.subscribe(EventFixtures.CustomEvent1, event_callback=event_callback)
        event_handler2 = EventLinker.subscribe(Event, EventFixtures.CustomEvent2, event_callback=event_callback)
        event_handler3 = EventLinker.subscribe("StringEvent", EventFixtures.CustomEvent1, event_callback=event_callback)
        event_handler4 = EventLinker.subscribe(PyventusException, Event, event_callback=event_callback)
        event_handler5 = EventLinker.subscribe(Exception, Exception, event_callback=event_callback)
        event_handler6 = EventLinker.subscribe("Exception", event_callback=event_callback)

        # Assert
        assert event_handler1 != event_handler2 != event_handler3 != event_handler4 != event_handler5 != event_handler6
        assert len(EventLinker.get_events()) == 6
        assert len(EventLinker.get_event_handlers()) == 6
        assert len(EventLinker.get_event_registry()[EventFixtures.CustomEvent1.__name__]) == 2
        assert len(EventLinker.get_event_registry()["Exception"]) == 2
        assert len(EventLinker.get_event_registry()["StringEvent"]) == 1
        assert EventLinker.get_handlers_by_events(PyventusException)[0] == event_handler4
        assert len(EventLinker.get_handlers_by_events(Event)) == 2
        assert len(EventLinker.get_events_by_handler(event_handler5)) == 1
        assert len(EventLinker.get_handlers_by_events(Event, EventFixtures.CustomEvent2)) == 2

    def test_subscribe_with_max_event_handler(self, clean_event_linker: bool):
        # Arrange
        class CustomEventLinker(EventLinker, max_event_handlers=3):
            pass  # pragma: no cover

        event_callback = CallbackFixtures.Sync()

        # Act
        event_handler1 = CustomEventLinker.subscribe(EventFixtures.CustomEvent1, event_callback=event_callback)
        event_handler2 = CustomEventLinker.subscribe(Event, EventFixtures.CustomEvent1, event_callback=event_callback)
        event_handler3 = CustomEventLinker.subscribe(
            "StrEvent", EventFixtures.CustomEvent1, event_callback=event_callback
        )

        # Assert
        assert len(CustomEventLinker.get_handlers_by_events(EventFixtures.CustomEvent1)) == 3

        # Act and Assert
        with raises(PyventusException):
            CustomEventLinker.subscribe(PyventusException, EventFixtures.CustomEvent1, event_callback=event_callback)

        # Assert
        assert len(CustomEventLinker.get_handlers_by_events(EventFixtures.CustomEvent1)) == 3

        # Act
        CustomEventLinker.unsubscribe(EventFixtures.CustomEvent1, event_handler=event_handler1)

        # Assert
        assert len(CustomEventLinker.get_handlers_by_events(EventFixtures.CustomEvent1)) == 2
        assert event_handler1 not in EventLinker.get_event_handlers()

        # Act
        event_handler4 = CustomEventLinker.subscribe(
            PyventusException, EventFixtures.CustomEvent1, event_callback=event_callback
        )

        # Assert
        assert len(CustomEventLinker.get_handlers_by_events(EventFixtures.CustomEvent1)) == 3

    def test_default_success_callback(self, clean_event_linker: bool):
        # Arrange
        default_success_callback = CallbackFixtures.Sync()
        success_callback = CallbackFixtures.Async()
        event_callback = CallbackFixtures.Sync()

        class CustomEventLinker(EventLinker, default_success_callback=default_success_callback):
            pass  # pragma: no cover

        # Act
        event_handler1 = EventLinker.subscribe(Event, event_callback=event_callback)
        event_handler2 = CustomEventLinker.subscribe(Event, event_callback=event_callback)
        event_handler3 = CustomEventLinker.subscribe(
            Exception, event_callback=event_callback, success_callback=success_callback
        )

        # Assert
        assert event_handler1._event_callback == event_callback
        assert event_handler1._success_callback is None
        assert event_handler1._failure_callback is None

        assert event_handler1._event_callback == event_callback
        assert event_handler2._success_callback == default_success_callback
        assert event_handler2._failure_callback is None

        assert event_handler1._event_callback == event_callback
        assert event_handler3._success_callback == success_callback
        assert event_handler3._failure_callback is None

    def test_default_failure_callback(self, clean_event_linker: bool):
        # Arrange
        default_failure_callback = CallbackFixtures.Sync()
        failure_callback = CallbackFixtures.Async()
        event_callback = CallbackFixtures.Sync()

        class CustomEventLinker(EventLinker, default_failure_callback=default_failure_callback):
            pass  # pragma: no cover

        # Act
        event_handler1 = EventLinker.subscribe(Event, event_callback=event_callback)
        event_handler2 = CustomEventLinker.subscribe(Event, event_callback=event_callback)
        event_handler3 = CustomEventLinker.subscribe(
            Exception, event_callback=event_callback, failure_callback=failure_callback
        )

        # Assert
        assert event_handler1._event_callback == event_callback
        assert event_handler1._success_callback is None
        assert event_handler1._failure_callback is None

        assert event_handler1._event_callback == event_callback
        assert event_handler2._success_callback is None
        assert event_handler2._failure_callback == default_failure_callback

        assert event_handler1._event_callback == event_callback
        assert event_handler3._success_callback is None
        assert event_handler3._failure_callback == failure_callback

    def test_unsubscribe(self, clean_event_linker: bool):
        event_callback = CallbackFixtures.Sync()

        # Arrange | Act
        event_handler1 = EventLinker.subscribe(EventFixtures.CustomEvent1, event_callback=event_callback)
        event_handler2 = EventLinker.subscribe(Event, EventFixtures.CustomEvent1, event_callback=event_callback)
        event_handler3 = EventLinker.subscribe("StrEvent", EventFixtures.CustomEvent1, event_callback=event_callback)

        # Assert
        assert len(EventLinker.get_events()) == 3
        assert len(EventLinker.get_event_handlers()) == 3
        assert len(EventLinker.get_handlers_by_events(EventFixtures.CustomEvent1)) == 3

        # Act | Assert
        assert not EventLinker.unsubscribe(EventFixtures.CustomEvent2, event_handler=event_handler1)
        assert len(EventLinker.get_event_handlers()) == 3

        # Act | Assert
        assert EventLinker.unsubscribe("CustomEvent1", event_handler=event_handler1)
        assert not EventLinker.unsubscribe(EventFixtures.CustomEvent1, event_handler=event_handler1)
        assert len(EventLinker.get_handlers_by_events(EventFixtures.CustomEvent1)) == 2
        assert len(EventLinker.get_event_handlers()) == 2

        # Act | Assert
        assert EventLinker.unsubscribe(EventFixtures.CustomEvent1, event_handler=event_handler2)
        assert len(EventLinker.get_handlers_by_events(EventFixtures.CustomEvent1)) == 1
        assert len(EventLinker.get_event_handlers()) == 2

        # Act | Assert
        with raises(PyventusException):
            EventLinker.unsubscribe(event_handler=event_handler3)
        with raises(PyventusException):
            EventLinker.unsubscribe(Event, event_handler=None)  # type: ignore

        # Assert
        assert len(EventLinker.get_event_handlers()) == 2
        assert len(EventLinker.get_handlers_by_events(EventFixtures.CustomEvent1)) == 1

        # Act | Assert
        assert EventLinker.unsubscribe(EventFixtures.CustomEvent1, event_handler=event_handler3)
        assert len(EventLinker.get_handlers_by_events(EventFixtures.CustomEvent1)) == 0
        assert len(EventLinker.get_event_registry().keys()) == 2
        assert len(EventLinker.get_event_handlers()) == 2

    def test_remove_event_handler(self, clean_event_linker: bool):
        # Arrange | Act | Assert
        with raises(PyventusException):
            EventLinker.remove_event_handler(None)  # type: ignore

        # Arrange
        event_callback = CallbackFixtures.Sync()
        event_handler1 = EventLinker.subscribe(EventFixtures.CustomEvent1, event_callback=event_callback)
        event_handler2 = EventLinker.subscribe(Event, EventFixtures.CustomEvent1, event_callback=event_callback)
        event_handler3 = EventLinker.subscribe("StrEvent", EventFixtures.CustomEvent1, event_callback=event_callback)

        # Assert
        assert len(EventLinker.get_handlers_by_events(EventFixtures.CustomEvent1)) == 3
        assert len(EventLinker.get_event_handlers()) == 3
        assert len(EventLinker.get_events()) == 3

        # Act and Assert
        assert EventLinker.remove_event_handler(event_handler=event_handler1)
        assert not EventLinker.remove_event_handler(event_handler=event_handler1)
        assert len(EventLinker.get_handlers_by_events(EventFixtures.CustomEvent1)) == 2
        assert len(EventLinker.get_event_handlers()) == 2
        assert len(EventLinker.get_events()) == 3

        # Act and Assert
        assert EventLinker.remove_event_handler(event_handler=event_handler3)
        assert not EventLinker.remove_event_handler(event_handler=event_handler3)
        assert len(EventLinker.get_handlers_by_events(EventFixtures.CustomEvent1)) == 1
        assert len(EventLinker.get_event_handlers()) == 1
        assert len(EventLinker.get_events()) == 2

    def test_remove_event(self, clean_event_linker: bool):
        # Arrange
        event_callback = CallbackFixtures.Sync()
        event_handler1 = EventLinker.subscribe(EventFixtures.CustomEvent1, event_callback=event_callback)
        event_handler2 = EventLinker.subscribe(Event, EventFixtures.CustomEvent1, event_callback=event_callback)
        event_handler3 = EventLinker.subscribe("StrEvent", EventFixtures.CustomEvent1, event_callback=event_callback)

        # Act and Assert
        with raises(PyventusException):
            EventLinker.remove_event(None)  # type: ignore
        assert len(EventLinker.get_events()) == 3

        # Act and Assert
        assert EventLinker.remove_event(Event)
        assert not EventLinker.remove_event(Event)
        assert len(EventLinker.get_event_handlers()) == 3
        assert len(EventLinker.get_events()) == 2

        # Act and Assert
        assert EventLinker.remove_event("CustomEvent1")
        assert not EventLinker.remove_event("CustomEvent1")
        assert len(EventLinker.get_events()) == 1
        assert "StrEvent" in EventLinker.get_events()
        assert len(EventLinker.get_event_handlers()) == 1
        assert event_handler3 in EventLinker.get_event_handlers()

        # Act and Assert
        assert not EventLinker.remove_event("StrEvents")
        assert len(EventLinker.get_events()) == 1
        assert EventLinker.remove_event("StrEvent")
        assert EventLinker.get_event_registry() == {}

    def test_remove_all(self, clean_event_linker: bool):
        # Arrange
        event_callback = CallbackFixtures.Sync()
        event_handler1 = EventLinker.subscribe(EventFixtures.CustomEvent1, event_callback=event_callback)
        event_handler2 = EventLinker.subscribe(Event, EventFixtures.CustomEvent1, event_callback=event_callback)
        event_handler3 = EventLinker.subscribe("StrEvent", EventFixtures.CustomEvent1, event_callback=event_callback)

        # Assert
        assert len(EventLinker.get_events()) == 3
        assert len(EventLinker.get_event_handlers()) == 3

        # Act | Assert
        assert EventLinker.remove_all()
        assert EventLinker.remove_all()
        assert EventLinker.get_event_registry() == {}

    def test_namespaces(self, clean_event_linker: bool):
        # Arrange | Act | Assert
        with raises(PyventusException):

            class CustomEventLinker0(EventLinker, max_event_handlers=0):
                pass  # pragma: no cover

        with raises(PyventusException):

            class CustomEventLinker1(EventLinker, default_success_callback="Callable"):  # type: ignore
                pass  # pragma: no cover

        # Arrange | Act
        class CustomEventLinker2(EventLinker, max_event_handlers=10):
            pass  # pragma: no cover

        class CustomEventLinker3(EventLinker, max_event_handlers=None, debug=False):
            @classmethod
            def get_logger(cls) -> Logger:
                return cls._get_logger()

        class CustomEventLinker4(EventLinker, debug=True):
            @classmethod
            def get_logger(cls) -> Logger:
                return cls._get_logger()

        # Assert
        assert CustomEventLinker2.get_max_event_handlers() == 10
        assert CustomEventLinker3.get_max_event_handlers() is None
        assert not CustomEventLinker3.get_logger().debug_enabled
        assert CustomEventLinker4.get_max_event_handlers() is None
        assert CustomEventLinker4.get_logger().debug_enabled
        assert EventLinker.get_max_event_handlers() is None

        # Act
        CustomEventLinker2.subscribe(Event, event_callback=CallbackFixtures.Sync())
        CustomEventLinker3.subscribe(Event, event_callback=CallbackFixtures.Sync())
        EventLinker.subscribe(Event, event_callback=CallbackFixtures.Sync())

        # Assert
        assert len(EventLinker.get_event_handlers()) == len(CustomEventLinker2.get_event_handlers())
        assert len(EventLinker.get_event_handlers()) == len(CustomEventLinker3.get_event_handlers())
        assert CustomEventLinker4.get_event_registry() == {}

        # Act
        EventLinker.remove_all()

        # Assert
        assert len(EventLinker.get_event_handlers()) == 0
        assert len(EventLinker.get_event_handlers()) != len(CustomEventLinker2.get_event_handlers())
        assert len(EventLinker.get_event_handlers()) != len(CustomEventLinker3.get_event_handlers())
