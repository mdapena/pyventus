"""A powerful Python package for event-driven programming; define, emit, and orchestrate events with ease."""

__version__ = "0.4.1"

from .core.exceptions import PyventusException
from .emitters import EventEmitter, EmittableEventType
from .emitters.asyncio import AsyncIOEventEmitter
from .emitters.executor import ExecutorEventEmitter
from .events import Event
from .handlers import EventHandler, EventCallbackType, SuccessCallbackType, FailureCallbackType
from .linkers import EventLinker, SubscribableEventType

__all__ = [
    "PyventusException",
    "EventEmitter",
    "EmittableEventType",
    "AsyncIOEventEmitter",
    "ExecutorEventEmitter",
    "Event",
    "EventHandler",
    "EventCallbackType",
    "SuccessCallbackType",
    "FailureCallbackType",
    "EventLinker",
    "SubscribableEventType",
]
