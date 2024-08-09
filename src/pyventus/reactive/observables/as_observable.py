from functools import wraps
from typing import Callable, ParamSpec, TypeVar

from .observable import Observable, ObservableCallbackReturnType

_out_T = TypeVar("_out_T", covariant=True)
"""A generic type for the value that will be streamed through the observable."""

_P = ParamSpec("_P")
"""A generic type representing the names and types of the callback parameters."""


def as_observable(callback: Callable[_P, ObservableCallbackReturnType[_out_T]]) -> Callable[_P, Observable[_out_T]]:
    """
    Decorator factory that converts a given callback into a function that returns an `Observable`.

    **Notes:**

    -   The decorated callback can be either a standard `sync` or `async` function, as well as a
        `sync` or `async` generator to stream data through the `Observable`.

    -   It is important to note that the decorated callback is executed not upon calling the output
        function, but rather when the `Observable` produced by the output function is executed.

    :param callback: The callback to be encapsulated within an `Observable`.
    :return: A function that, upon invocation, generates an `Observable` instance.
    """

    @wraps(callback)
    def helper(*args: _P.args, **kwargs: _P.kwargs) -> Observable[_out_T]:
        # Creates an Observable instance based on the provided callback.
        return Observable[_out_T](callback=callback, args=args, kwargs=kwargs)

    return helper
