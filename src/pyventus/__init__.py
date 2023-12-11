""" A versatile Python library for managing multiple, decoupled event emitters with ease. """

__version__ = "1.0.0"

from .core.exceptions import PyventusException
from .emitters import EventEmitter, EmittableEventType
from .emitters.asyncio import AsyncIOEventEmitter
from .emitters.executor import ExecutorEventEmitter
from .emitters.rq import RQEventEmitter
from .events import Event
from .handlers import EventHandler
from .linkers import EventLinker, SubscribableEventType

__all__ = [
    "PyventusException",
    "EventEmitter",
    "EmittableEventType",
    "AsyncIOEventEmitter",
    "ExecutorEventEmitter",
    "RQEventEmitter",
    "Event",
    "EventHandler",
    "EventLinker",
    "SubscribableEventType",
]
