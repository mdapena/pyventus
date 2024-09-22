"""
The `reactive` module in Pyventus is the core module for reactive programming.

It provides a set of tools to easily create and manage data streams that reflect changes in state over time.
"""

from .observables import (
    Completed,
    Observable,
    ObservableTask,
    ObservableTaskCallbackReturnType,
    ObservableTaskCallbackType,
    as_observable_task,
)
from .observers import Observer
from .subscribers import (
    CompleteCallbackType,
    ErrorCallbackType,
    NextCallbackType,
    Subscriber,
)

__all__ = [
    "Completed",
    "Observable",
    "ObservableTask",
    "ObservableTaskCallbackReturnType",
    "ObservableTaskCallbackType",
    "as_observable_task",
    "Observer",
    "CompleteCallbackType",
    "ErrorCallbackType",
    "NextCallbackType",
    "Subscriber",
]
