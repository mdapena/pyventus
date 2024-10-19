"""A powerful Python package for event-driven programming; define, emit, and orchestrate events with ease."""

__version__ = "0.6.0"

from .core.exceptions import PyventusException
from .emitters import EventEmitter, EmittableEventType
from .emitters.asyncio import AsyncIOEventEmitter
from .emitters.executor import ExecutorEventEmitter
from .handlers import EventHandler, EventCallbackType, SuccessCallbackType, FailureCallbackType
from .linkers import EventLinker, SubscribableEventType

__all__ = [
    "PyventusException",
    "EventEmitter",
    "EmittableEventType",
    "AsyncIOEventEmitter",
    "ExecutorEventEmitter",
    "EventHandler",
    "EventCallbackType",
    "SuccessCallbackType",
    "FailureCallbackType",
    "EventLinker",
    "SubscribableEventType",
]
