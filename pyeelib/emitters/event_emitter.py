from abc import ABC, abstractmethod
from typing import Any, Tuple, ParamSpec, List, Coroutine, Callable, Type

from pyeelib.events import Event
from pyeelib.linkers import EventLinker
from pyeelib.listeners import EventListener

P = ParamSpec("P")


class EventEmitter(ABC):
    _EVENT_TYPES = Event | BaseException | str

    def __init__(self, event_linker: Type[EventLinker] = EventLinker):
        self._event_linker: Type[EventLinker] = event_linker

    def emit(self, event: _EVENT_TYPES, *args: P.args, supress_exceptions: bool = False, **kwargs: P.kwargs) -> None:
        try:
            event_args: Tuple[Any] = args if isinstance(event, str) else (event, *args)

            event_key: str = event if isinstance(event, str) else event.__class__

            event_listeners: List[EventListener] = self._event_linker.get_listeners_by_event(event_key)

            for event_listener in event_listeners:
                self._execute(*event_args, callback=event_listener, **kwargs)
                if event_listener.ttl <= 0:
                    self._event_linker.unsubscribe(event_key, event_listener=event_listener)
        except BaseException as exception:
            if supress_exceptions:
                event_listeners = self._event_linker.get_listeners_by_event(event=exception.__class__)

                if not isinstance(exception, BaseException):
                    event_listeners.extend(self._event_linker.get_listeners_by_event(event=BaseException))

                for event_listener in event_listeners:
                    self._execute(exception, callback=event_listener)
            else:
                raise exception

    @abstractmethod
    def _execute(self, *args: P.args, callback: Callable[P, Coroutine], **kwargs: P.args) -> None:
        pass
