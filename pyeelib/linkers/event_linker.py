from typing import Dict, List, Mapping, ParamSpec, Callable, Type, Coroutine

from pyeelib.events import Event
from pyeelib.listeners import EventListener

P = ParamSpec("P")


class EventLinker:
    _EVENT_TYPES = Type[Event] | Type[BaseException] | str

    _event_listeners: Dict[str, List[EventListener]] = {}

    @classmethod
    @property
    def events(cls) -> List[str]:
        return list(cls._event_listeners.keys())

    @classmethod
    @property
    def listeners(cls) -> List[EventListener]:
        event_listeners: List[EventListener] = []
        for event_listener in cls._event_listeners.values():
            event_listeners.extend(event_listener)
        return list(set(event_listeners))

    @classmethod
    @property
    def event_listeners(cls) -> Mapping[str, List[EventListener]]:
        return cls._event_listeners

    @classmethod
    def _event_key(cls, event: _EVENT_TYPES) -> str:
        if isinstance(event, str):
            return event
        elif issubclass(event, (Event, BaseException)):
            return event.__name__
        else:
            raise ValueError('Unsupported event type')

    @classmethod
    def get_events_by_listener(cls, event_listener: EventListener) -> List[str]:
        return [k for k, v in cls._event_listeners.items() if event_listener in v]

    @classmethod
    def get_listeners_by_event(cls, event: _EVENT_TYPES) -> List[EventListener]:
        key: str = cls._event_key(event=event)
        return cls._event_listeners.get(key, [])

    @classmethod
    def on(cls, *events: _EVENT_TYPES, ttl: int | None = None):

        def _decorator(func: Callable[P, Coroutine | None]):
            cls.subscribe(*events, callback=func, ttl=ttl)
            return func

        return _decorator

    @classmethod
    def subscribe(cls, *events: _EVENT_TYPES, callback: Callable[P, Coroutine | None], ttl: int | None = None) -> None:
        event_listener: EventListener = EventListener(callback=callback, ttl=ttl)

        for event in events:
            key: str = cls._event_key(event=event)

            if key not in cls._event_listeners:
                cls._event_listeners[key] = []

            cls._event_listeners[key].append(event_listener)

    @classmethod
    def unsubscribe(cls, *events: _EVENT_TYPES, event_listener: EventListener) -> None:
        for event in events:
            key: str = cls._event_key(event=event)

            event_listeners = cls._event_listeners.get(key, [])

            if event_listener in event_listeners:
                event_listeners.remove(event_listener)

                if not event_listeners:
                    cls._event_listeners.pop(key)

    @classmethod
    def remove_listener(cls, event_listener: EventListener):
        for event, listeners in cls._event_listeners.items():
            if event_listener in listeners:
                listeners.remove(event_listener)

                if not listeners:
                    cls._event_listeners.pop(event)

    @classmethod
    def remove_event(cls, event: _EVENT_TYPES) -> bool:
        key: str = cls._event_key(event=event)

        if key in cls._event_listeners:
            cls._event_listeners.pop(key)
            return True

        return False

    @classmethod
    def remove_all(cls) -> None:
        cls._event_listeners = {}
