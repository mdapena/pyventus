from dataclasses import dataclass
from typing import Callable

from _pytest.python_api import raises

from src.pyventus.core.exceptions import PyventusException
from src.pyventus.events import Event
from src.pyventus.linkers import EventLinker
from src.pyventus.listeners import EventListener


# region: Custom Events
@dataclass(frozen=True)
class EmailEvent(Event):
    email: str
    message: str


@dataclass(frozen=True)
class CustomEvent(Event):
    id: str


# endregion

class TestEventLinker:

    # region: Callbacks
    async def callback_without_params(self): pass

    def callback_with_multi_params(self, *args, **kwargs): pass

    async def callback_with_exception_param(self, exception: Exception): pass

    def callback_with_event_param(self, event: Event): pass

    async def callback_with_two_params(self, email: str, message: str): pass

    # endregion

    def test_events_property(self, clean_event_linker: bool):
        # Arrange and Act
        EventLinker.subscribe(EmailEvent, callback=self.callback_with_event_param)
        EventLinker.subscribe(EmailEvent, callback=self.callback_with_event_param)
        EventLinker.subscribe(Event, callback=self.callback_with_event_param)

        # Assert
        assert len(EventLinker.events) == 2
        assert Event.__name__ in EventLinker.events
        assert EmailEvent.__name__ in EventLinker.events

    def test_event_listeners_property(self, clean_event_linker: bool):
        # Arrange and Act
        event_listener_1 = EventLinker.subscribe(Event, EmailEvent, callback=self.callback_with_event_param)
        event_listener_2 = EventLinker.subscribe(CustomEvent, EmailEvent, callback=self.callback_with_event_param)

        # Assert
        assert len(EventLinker.event_listeners) == 2
        assert event_listener_1 in EventLinker.event_listeners
        assert event_listener_2 in EventLinker.event_listeners

    def test_event_registry_property(self, clean_event_linker: bool):
        # Arrange and Act
        event_listener_1 = EventLinker.subscribe(Event, EmailEvent, callback=self.callback_with_event_param)
        event_listener_2 = EventLinker.subscribe(CustomEvent, EmailEvent, callback=self.callback_with_event_param)

        # Assert
        assert len(EventLinker.event_registry.keys()) == 3
        assert len(EventLinker.event_registry[Event.__name__]) == 1
        assert event_listener_1 in EventLinker.event_registry[Event.__name__]
        assert len(EventLinker.event_registry[EmailEvent.__name__]) == 2
        assert event_listener_1 in EventLinker.event_registry[EmailEvent.__name__]
        assert event_listener_2 in EventLinker.event_registry[EmailEvent.__name__]
        assert len(EventLinker.event_registry[CustomEvent.__name__]) == 1
        assert event_listener_2 in EventLinker.event_registry[CustomEvent.__name__]

        # Act
        EventLinker.event_registry.pop(Event.__name__)
        EventLinker.event_registry[Event.__name__].append(event_listener_2)

        # Assert
        assert len(EventLinker.event_registry.keys()) == 3
        assert len(EventLinker.event_registry[Event.__name__]) == 1

    def test_max_event_listeners_property(self, clean_event_linker: bool):
        # Arrange and Act
        class CustomEventLinker(EventLinker, max_event_listeners=2):
            pass

        # Assert
        assert EventLinker.max_event_listeners is None
        assert CustomEventLinker.max_event_listeners == 2

    def test_get_events_by_listener(self, clean_event_linker: bool):
        # Arrange, Act and Assert
        with raises(PyventusException):
            EventLinker.get_events_by_listener(event_listener=None)

        # Arrange and Act
        event_listener_1 = EventLinker.subscribe(Event, EmailEvent, callback=self.callback_with_event_param)
        event_listener_2 = EventLinker.subscribe(CustomEvent, callback=self.callback_with_event_param)

        # Assert
        assert len(EventLinker.get_events_by_listener(event_listener=event_listener_1)) == 2
        assert Event.__name__ in EventLinker.get_events_by_listener(event_listener=event_listener_1)
        assert EmailEvent.__name__ in EventLinker.get_events_by_listener(event_listener=event_listener_1)
        assert len(EventLinker.get_events_by_listener(event_listener=event_listener_2)) == 1
        assert CustomEvent.__name__ in EventLinker.get_events_by_listener(event_listener=event_listener_2)

        # Arrange and Act
        event_listener_3: EventListener = EventListener(callback=self.callback_with_event_param)

        # Assert
        assert len(EventLinker.get_events_by_listener(event_listener=event_listener_3)) == 0

    def test_get_listeners_by_events(self, clean_event_linker: bool):
        # Arrange, Act and Assert
        with raises(PyventusException):
            EventLinker.get_listeners_by_events()
        with raises(PyventusException):
            EventLinker.get_listeners_by_events('testing', str)
        with raises(PyventusException):
            EventLinker.get_listeners_by_events(Event, BaseException)
        assert len(EventLinker.get_listeners_by_events(Event)) == 0

        # Arrange and Act
        event_listener_1 = EventLinker.subscribe(Event, EmailEvent, callback=self.callback_with_event_param)
        event_listener_2 = EventLinker.subscribe(CustomEvent, EmailEvent, callback=self.callback_with_event_param)

        # Assert
        assert len(EventLinker.get_listeners_by_events(Event)) == 1
        assert len(EventLinker.get_listeners_by_events(Event, Event, Event)) == 1
        assert event_listener_1 in EventLinker.get_listeners_by_events(Event)
        assert len(EventLinker.get_listeners_by_events(EmailEvent)) == 2
        assert event_listener_1 in EventLinker.get_listeners_by_events(EmailEvent)
        assert event_listener_2 in EventLinker.get_listeners_by_events(EmailEvent)
        assert len(EventLinker.get_listeners_by_events(CustomEvent)) == 1
        assert event_listener_2 in EventLinker.get_listeners_by_events(CustomEvent)
        assert len(EventLinker.get_listeners_by_events(Event, EmailEvent, Event, CustomEvent)) == 2
        assert len(EventLinker.get_listeners_by_events('None')) == 0

    def test_once_decorator(self, clean_event_linker: bool):
        # Arrange, Act and Assert
        with raises(PyventusException):
            @EventLinker.once()
            def invalid_once_callback(event: Event): pass

        # Arrange and Act
        @EventLinker.once(Event, Exception)
        def first_once_callback(*args, **kwargs): pass

        @EventLinker.once(Exception)
        async def second_once_callback(exception: Exception): pass

        # Assert
        assert len(EventLinker.get_listeners_by_events(Event)) == 1
        assert EventLinker.get_listeners_by_events(Event)[0].once
        assert len(EventLinker.get_listeners_by_events(Exception)) == 2
        assert EventLinker.get_listeners_by_events(Exception)[0].once
        assert EventLinker.get_listeners_by_events(Exception)[1].once
        assert len(EventLinker.event_listeners) == 2

    def test_on_decorator(self, clean_event_linker: bool):
        # Arrange, Act and Assert
        with raises(PyventusException):
            @EventLinker.on()
            def invalid_once_callback(event: Event): pass

        # Arrange and Act
        @EventLinker.on(Event, EmailEvent)
        def first_once_callback(*args, **kwargs): pass

        @EventLinker.on(Exception)
        async def second_once_callback(exception: Exception): pass

        # Assert
        assert len(EventLinker.get_listeners_by_events(Event)) == 1
        assert not EventLinker.get_listeners_by_events(Event)[0].once
        assert len(EventLinker.get_listeners_by_events(EmailEvent)) == 1
        assert EventLinker.get_listeners_by_events(EmailEvent) == EventLinker.get_listeners_by_events(Event)
        assert len(EventLinker.get_listeners_by_events(Exception)) == 1
        assert not EventLinker.get_listeners_by_events(Exception)[0].once
        assert len(EventLinker.event_listeners) == 2

    def test_subscribe(self, clean_event_linker: bool):
        # Arrange, Act and Assert
        with raises(PyventusException):
            EventLinker.subscribe(callback=self.callback_with_event_param)
        with raises(PyventusException):
            def invalid_callback() -> Callable: pass

            EventLinker.subscribe(Event, callback=invalid_callback())

        # Arrange and Act
        event_listener_1 = EventLinker.subscribe(EmailEvent, callback=self.callback_with_event_param)
        event_listener_2 = EventLinker.subscribe(Event, CustomEvent, callback=self.callback_with_two_params)
        event_listener_3 = EventLinker.subscribe('StringEvent', EmailEvent, callback=self.callback_without_params)
        event_listener_4 = EventLinker.subscribe(PyventusException, Event, callback=self.callback_with_multi_params)
        event_listener_5 = EventLinker.subscribe(Exception, Exception, callback=self.callback_with_exception_param)
        event_listener_6 = EventLinker.subscribe('Exception', callback=self.callback_with_exception_param)

        # Assert
        assert event_listener_1 != event_listener_2 != event_listener_3 != event_listener_4 != event_listener_5 != event_listener_6
        assert len(EventLinker.events) == 6
        assert len(EventLinker.event_listeners) == 6
        assert len(EventLinker.event_registry[EmailEvent.__name__]) == 2
        assert len(EventLinker.event_registry['Exception']) == 2
        assert len(EventLinker.event_registry['StringEvent']) == 1
        assert EventLinker.get_listeners_by_events(PyventusException)[0] == event_listener_4
        assert len(EventLinker.get_listeners_by_events(Event)) == 2
        assert len(EventLinker.get_events_by_listener(event_listener_5)) == 1
        assert len(EventLinker.get_listeners_by_events(Event, CustomEvent)) == 2

    def test_subscribe_with_max_event_listener(self, clean_event_linker: bool):
        # Arrange
        class CustomEventLinker(EventLinker, max_event_listeners=3):
            pass

        # Act
        event_listener_1 = CustomEventLinker.subscribe(EmailEvent, callback=self.callback_with_event_param)
        event_listener_2 = CustomEventLinker.subscribe(Event, EmailEvent, callback=self.callback_with_two_params)
        event_listener_3 = CustomEventLinker.subscribe('StrEvent', EmailEvent, callback=self.callback_with_multi_params)

        # Assert
        assert len(CustomEventLinker.get_listeners_by_events(EmailEvent)) == 3

        # Act and Assert
        with raises(PyventusException):
            CustomEventLinker.subscribe(PyventusException, EmailEvent, callback=self.callback_with_multi_params)

        # Assert
        assert len(CustomEventLinker.get_listeners_by_events(EmailEvent)) == 3

        # Act
        CustomEventLinker.unsubscribe(EmailEvent, event_listener=event_listener_1)

        # Assert
        assert len(CustomEventLinker.get_listeners_by_events(EmailEvent)) == 2
        assert event_listener_1 not in EventLinker.event_listeners

        # Act
        event_listener_4 = CustomEventLinker.subscribe(
            PyventusException, EmailEvent,
            callback=self.callback_with_multi_params
        )

        # Assert
        assert len(CustomEventLinker.get_listeners_by_events(EmailEvent)) == 3

    def test_unsubscribe(self, clean_event_linker: bool):
        # Arrange and Act
        event_listener_1 = EventLinker.subscribe(EmailEvent, callback=self.callback_with_event_param)
        event_listener_2 = EventLinker.subscribe(Event, EmailEvent, callback=self.callback_with_two_params)
        event_listener_3 = EventLinker.subscribe('StrEvent', EmailEvent, callback=self.callback_with_multi_params)

        # Assert
        assert len(EventLinker.events) == 3
        assert len(EventLinker.event_listeners) == 3
        assert len(EventLinker.get_listeners_by_events(EmailEvent)) == 3

        # Act and Assert
        assert not EventLinker.unsubscribe(CustomEvent, event_listener=event_listener_1)
        assert len(EventLinker.event_listeners) == 3

        # Act and Assert
        assert EventLinker.unsubscribe('EmailEvent', event_listener=event_listener_1)
        assert not EventLinker.unsubscribe(EmailEvent, event_listener=event_listener_1)
        assert len(EventLinker.get_listeners_by_events(EmailEvent)) == 2
        assert len(EventLinker.event_listeners) == 2

        # Act and Assert
        assert EventLinker.unsubscribe(EmailEvent, event_listener=event_listener_2)
        assert len(EventLinker.get_listeners_by_events(EmailEvent)) == 1
        assert len(EventLinker.event_listeners) == 2

        # Act and Assert
        with raises(PyventusException):
            EventLinker.unsubscribe(event_listener=event_listener_3)
        with raises(PyventusException):
            EventLinker.unsubscribe(Event, event_listener=None)

        # Assert
        assert len(EventLinker.event_listeners) == 2
        assert len(EventLinker.get_listeners_by_events(EmailEvent)) == 1

        # Act and Assert
        assert EventLinker.unsubscribe(EmailEvent, event_listener=event_listener_3)
        assert len(EventLinker.get_listeners_by_events(EmailEvent)) == 0
        assert len(EventLinker.event_registry.keys()) == 2
        assert len(EventLinker.event_listeners) == 2

    def test_remove_event_listener(self, clean_event_linker: bool):
        # Arrange, Act and Assert
        with raises(PyventusException):
            EventLinker.remove_event_listener(None)

        # Arrange
        event_listener_1 = EventLinker.subscribe(EmailEvent, callback=self.callback_with_event_param)
        event_listener_2 = EventLinker.subscribe(Event, EmailEvent, callback=self.callback_with_two_params)
        event_listener_3 = EventLinker.subscribe('StrEvent', EmailEvent, callback=self.callback_with_multi_params)

        # Assert
        assert len(EventLinker.get_listeners_by_events(EmailEvent)) == 3
        assert len(EventLinker.event_listeners) == 3
        assert len(EventLinker.events) == 3

        # Act and Assert
        assert EventLinker.remove_event_listener(event_listener=event_listener_1)
        assert not EventLinker.remove_event_listener(event_listener=event_listener_1)
        assert len(EventLinker.get_listeners_by_events(EmailEvent)) == 2
        assert len(EventLinker.event_listeners) == 2
        assert len(EventLinker.events) == 3

        # Act and Assert
        assert EventLinker.remove_event_listener(event_listener=event_listener_3)
        assert not EventLinker.remove_event_listener(event_listener=event_listener_3)
        assert len(EventLinker.get_listeners_by_events(EmailEvent)) == 1
        assert len(EventLinker.event_listeners) == 1
        assert len(EventLinker.events) == 2

    def test_remove_event(self, clean_event_linker: bool):
        # Arrange
        event_listener_1 = EventLinker.subscribe(EmailEvent, callback=self.callback_with_event_param)
        event_listener_2 = EventLinker.subscribe(Event, EmailEvent, callback=self.callback_with_two_params)
        event_listener_3 = EventLinker.subscribe('StrEvent', EmailEvent, callback=self.callback_with_multi_params)

        # Act and Assert
        with raises(PyventusException):
            EventLinker.remove_event(None)
        assert len(EventLinker.events) == 3

        # Act and Assert
        assert EventLinker.remove_event(Event)
        assert not EventLinker.remove_event(Event)
        assert len(EventLinker.event_listeners) == 3
        assert len(EventLinker.events) == 2

        # Act and Assert
        assert EventLinker.remove_event('EmailEvent')
        assert not EventLinker.remove_event('EmailEvent')
        assert len(EventLinker.events) == 1
        assert 'StrEvent' in EventLinker.events
        assert len(EventLinker.event_listeners) == 1
        assert event_listener_3 in EventLinker.event_listeners

        # Act and Assert
        assert not EventLinker.remove_event('StrEvents')
        assert len(EventLinker.events) == 1
        assert EventLinker.remove_event('StrEvent')
        assert EventLinker.event_registry == {}

    def test_remove_all(self, clean_event_linker: bool):
        # Arrange
        event_listener_1 = EventLinker.subscribe(EmailEvent, callback=self.callback_with_event_param)
        event_listener_2 = EventLinker.subscribe(Event, EmailEvent, callback=self.callback_with_two_params)
        event_listener_3 = EventLinker.subscribe('StrEvent', EmailEvent, callback=self.callback_with_multi_params)

        # Assert
        assert len(EventLinker.events) == 3
        assert len(EventLinker.event_listeners) == 3

        # Act and Assert
        assert EventLinker.remove_all()
        assert EventLinker.remove_all()
        assert EventLinker.event_registry == {}

    def test_namespaces(self, clean_event_linker: bool):
        # Arrange, Act and Assert
        with raises(PyventusException):
            class CustomEventLinker1(EventLinker, max_event_listeners=0):
                pass

        # Arrange and Act
        class CustomEventLinker2(EventLinker, max_event_listeners=10):
            pass

        class CustomEventLinker3(EventLinker, max_event_listeners=None):
            pass

        class CustomEventLinker4(EventLinker):
            pass

        # Assert
        assert CustomEventLinker2.max_event_listeners == 10
        assert CustomEventLinker3.max_event_listeners is None
        assert CustomEventLinker4.max_event_listeners is None
        assert EventLinker.max_event_listeners is None

        # Act
        CustomEventLinker2.subscribe(Event, callback=self.callback_without_params)
        CustomEventLinker3.subscribe(Event, callback=self.callback_without_params)
        EventLinker.subscribe(Event, callback=self.callback_without_params)

        # Assert
        assert len(EventLinker.event_listeners) == len(CustomEventLinker2.event_listeners)
        assert len(EventLinker.event_listeners) == len(CustomEventLinker3.event_listeners)
        assert CustomEventLinker4.event_registry == {}

        # Act
        EventLinker.remove_all()

        # Assert
        assert len(EventLinker.event_listeners) == 0
        assert len(EventLinker.event_listeners) != len(CustomEventLinker2.event_listeners)
        assert len(EventLinker.event_listeners) != len(CustomEventLinker3.event_listeners)
