"""
A modern and robust Python package for event-driven programming. Define, emit, and orchestrate events with ease using
customizable event emitters and flexible responses.
"""

__version__ = "0.4.0"

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
