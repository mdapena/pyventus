"""
The `reactive` module in Pyventus is the core module for reactive programming. It provides a
set of tools to easily create and manage data streams that reflect changes in state over time.
"""

from .observables import (
    Completed,
    Observable,
    ObservableCallbackReturnType,
    ObservableCallbackType,
    as_observable,
)
from .observers import Observer
from .subscribers import (
    CompleteCallbackType,
    ErrorCallbackType,
    NextCallbackType,
    Subscriber,
)

__all__ = [
    "Observable",
    "Completed",
    "ObservableCallbackType",
    "ObservableCallbackReturnType",
    "as_observable",
    "Observer",
    "Subscriber",
    "NextCallbackType",
    "ErrorCallbackType",
    "CompleteCallbackType",
]
