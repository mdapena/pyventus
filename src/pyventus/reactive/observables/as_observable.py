from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from .observable import Observable, ObservableCallbackReturnType

_P = ParamSpec("_P")
"""A generic type representing the names and types of the callback parameters."""

_OutT = TypeVar("_OutT", covariant=True)
"""A generic type for the value that will be streamed through the observable."""


def as_observable(callback: Callable[_P, ObservableCallbackReturnType[_OutT]]) -> Callable[_P, Observable[_OutT]]:
    """
    Convert a given callback into a function that returns an `Observable`.

    **Notes:**

    -   The decorated callback can be either a standard `sync` or `async` function, as well as
        a `sync` or `async` generator to stream data through the `Observable`.

    -   It is important to note that the decorated callback is executed not upon calling the output
        function, but rather when the `Observable` produced by the output function is executed.

    :param callback: The callback to be encapsulated within an `Observable`.
    :return: A function that, upon invocation, generates an `Observable` instance.
    """

    @wraps(callback)
    def helper(*args: _P.args, **kwargs: _P.kwargs) -> Observable[_OutT]:
        # Creates an Observable instance based on the provided callback.
        return Observable[_OutT](callback=callback, args=args, kwargs=kwargs)

    return helper
