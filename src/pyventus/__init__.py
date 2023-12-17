"""
A modern and robust Python package for event-driven programming. Define, emit, and orchestrate events with ease using
customizable event emitters and flexible responses.
"""

__version__ = "0.2.0"

from .core.exceptions import PyventusException
from .emitters import EventEmitter, EmittableEventType
from .emitters.asyncio import AsyncIOEventEmitter
from .emitters.executor import ExecutorEventEmitter
from .emitters.rq import RQEventEmitter
from .events import Event
from .handlers import EventHandler, EventCallbackType, SuccessCallbackType, FailureCallbackType
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
    "EventCallbackType",
    "SuccessCallbackType",
    "FailureCallbackType",
    "EventLinker",
    "SubscribableEventType",
]
