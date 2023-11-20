""" A versatile Python library for managing multiple, decoupled event emitters with ease. """

__version__ = "1.0.0"

from .emitters import EventEmitter, EmittableEventType
from .emitters.asyncio import AsyncioEventEmitter
from .emitters.rq import RqEventEmitter
from .events import Event
from .linkers import EventLinker, SubscribableEventType
from .listeners import EventListener

__all__ = [
    'EventEmitter',
    'EmittableEventType',
    'AsyncioEventEmitter',
    'RqEventEmitter',
    'Event',
    'EventLinker',
    'SubscribableEventType',
    'EventListener',
]
