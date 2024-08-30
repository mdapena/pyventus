"""
The `events` module in Pyventus is the core module for event-driven programming.

It offers a comprehensive suite of tools to easily define, emit, and orchestrate events.
"""

from .emitters import EmittableEventType, EventEmitter
from .emitters.asyncio import AsyncIOEventEmitter
from .emitters.executor import ExecutorEventEmitter
from .handlers import EventHandler
from .linkers import EventLinker, SubscribableEventType
from .subscribers import (
    EventCallbackType,
    EventSubscriber,
    FailureCallbackType,
    SuccessCallbackType,
)

__all__ = [
    "EventEmitter",
    "EmittableEventType",
    "AsyncIOEventEmitter",
    "ExecutorEventEmitter",
    "EventHandler",
    "EventLinker",
    "SubscribableEventType",
    "EventSubscriber",
    "EventCallbackType",
    "SuccessCallbackType",
    "FailureCallbackType",
]
