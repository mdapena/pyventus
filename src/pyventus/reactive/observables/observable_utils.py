from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from typing_extensions import overload

from .observable_task import ObservableTask, ObservableTaskCallbackReturnType

_P = ParamSpec("_P")
"""A generic type representing the names and types of the callback parameters."""

_OutT = TypeVar("_OutT", covariant=True)
"""A generic type for the value that will be streamed through the observable task."""


@overload
def as_observable_task(
    callback: Callable[_P, ObservableTaskCallbackReturnType[_OutT]], /
) -> Callable[_P, ObservableTask[_OutT]]: ...


@overload
def as_observable_task(
    *, debug: bool
) -> Callable[[Callable[_P, ObservableTaskCallbackReturnType[_OutT]]], Callable[_P, ObservableTask[_OutT]]]: ...


def as_observable_task(
    callback: Callable[_P, ObservableTaskCallbackReturnType[_OutT]] | None = None, /, *, debug: bool | None = None
) -> (
    Callable[_P, ObservableTask[_OutT]]
    | Callable[[Callable[_P, ObservableTaskCallbackReturnType[_OutT]]], Callable[_P, ObservableTask[_OutT]]]
):
    """
    Convert a given callback into an observable task.

    **Notes:**

    -   The decorated callback can be either a standard `sync` or `async` function, as well as
        a `sync` or `async` generator to stream data through the `ObservableTask`.

    -   It is important to note that the decorated callback is executed not upon calling the output
        function, but rather when the `ObservableTask` produced by the output function is executed.

    :param callback: The callback to be encapsulated and made observable.
    :param debug: Specifies the debug mode for the logger. If `None`,
        the mode is determined based on the execution environment.
    :return: A function that, upon invocation, generates an `ObservableTask`.
    """

    def decorator(
        _callback: Callable[_P, ObservableTaskCallbackReturnType[_OutT]],
    ) -> Callable[_P, ObservableTask[_OutT]]:
        @wraps(_callback)
        def helper(*args: _P.args, **kwargs: _P.kwargs) -> ObservableTask[_OutT]:
            # Create an ObservableTask instance based on the provided callback.
            return ObservableTask[_OutT](callback=_callback, args=args, kwargs=kwargs, debug=debug)

        return helper

    return decorator(callback) if callback is not None else decorator
