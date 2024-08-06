from asyncio import to_thread
from inspect import (
    isfunction,
    isclass,
    isbuiltin,
    ismethod,
    iscoroutinefunction,
    isgeneratorfunction,
    isasyncgenfunction,
)
from typing import TypeVar, Callable, ParamSpec, Any, Generic, final

from ..exceptions import PyventusException

_ParamType = ParamSpec("_ParamType")
"""A generic type representing the names and types of the parameters for a callable."""

_ReturnType = TypeVar("_ReturnType", covariant=True)
"""A generic type representing the return value of a callable."""


@final
class CallableWrapper(Generic[_ParamType, _ReturnType]):
    """
    A wrapper class that encapsulates a synchronous or asynchronous callable object
    and provides a unified asynchronous interface for its execution.

    **Notes**:

    -   The `__call__` method of the `CallableWrapper` class is an asynchronous method
        that returns a `Coroutine`. It should never be treated as a synchronous function.

    -   If `force_async` is set to `True`, synchronous callables will be executed asynchronously
        using the `asyncio.to_thread` function. If `force_async` is `False`, the callable will
        run in its original context (synchronously or asynchronously, as defined).
    """

    # CallableWrapper attributes
    __slots__ = ("__name__", "__callable", "__is_callable_async", "__force_async")

    @property
    def name(self) -> str:
        """
        Retrieves the name of the wrapped callable object.
        :return: A string representing the name of the wrapped callable object.
        """
        return self.__name__

    @property
    def force_async(self) -> bool:
        """
        Determines whether the wrapped callable is forced to run asynchronously.
        :return: A boolean value indicating if the wrapped callable is forced to
            run asynchronously.
        """
        return self.__force_async

    def __init__(self, cb: Callable[_ParamType, _ReturnType], /, force_async: bool) -> None:
        """
        Initializes an instance of `CallableWrapper`.
        :param cb: The callable object to be wrapped.
        :param force_async: A flag indicating whether to force the wrapped callable to run asynchronously.
        :raises PyventusException: If the given callable is invalid or if `force_async` is not a boolean.
        """
        # Validate the given callable object.
        validate_callable(cb)

        # Ensure that the provided callable is not a generator.
        if is_callable_generator(cb):
            raise PyventusException("The 'callable' argument cannot be a generator.")

        # Validate the provided force_async flag.
        if not isinstance(force_async, bool):
            raise PyventusException("The 'force_async' argument must be a boolean value.")

        # Store the name of the wrapped callable.
        self.__name__: str = get_callable_name(cb)

        # Store the callable and determine if it is asynchronous.
        self.__callable: Callable[_ParamType, _ReturnType] = cb
        self.__is_callable_async: bool = is_callable_async(cb)

        # Store the force_async flag.
        self.__force_async: bool = force_async

    async def __call__(self, *args: _ParamType.args, **kwargs: _ParamType.kwargs) -> _ReturnType:
        """
        Executes the wrapped callable with the given arguments.
        :param args: Positional arguments to pass to the wrapped callable.
        :param kwargs: Keyword arguments to pass to the wrapped callable.
        :return: The result of the wrapped callable execution.
        """
        if self.__is_callable_async:
            # Execute the callable directly if it is asynchronous.
            return await self.__callable(*args, **kwargs)  # type: ignore[no-any-return, misc]
        elif self.__force_async:
            # If the callable is synchronous and force_async is True, run it in a separate thread.
            return await to_thread(self.__callable, *args, **kwargs)
        else:
            # If the callable is synchronous and force_async is False, run it synchronously.
            return self.__callable(*args, **kwargs)

    def __str__(self) -> str:
        """
        Returns a string representation of the `CallableWrapper` instance.
        :return: A string representation of the `CallableWrapper` instance.
        """
        return (
            f"CallableWrapper(callable='{self.name}', "
            f"is_callable_async={self.__is_callable_async}, "
            f"force_async={self.__force_async})"
        )


def validate_callable(cb: Callable[..., Any], /) -> None:
    """
    Validates whether the given object is a valid callable.
    :param cb: The object to be validated.
    :return: None
    :raises PyventusException: If the object is not a valid callable.
    """
    if not callable(cb):
        raise PyventusException(f"The '{get_callable_name(cb)}' is not a valid callable object.")


def get_callable_name(cb: Callable[..., Any] | None, /) -> str:
    """
    Retrieves the name of the provided callable.
    :param cb: The callable object.
    :return: The name of the callable as a string.
    """
    if cb is None:
        return "None"
    elif hasattr(cb, "__name__"):
        return cb.__name__
    elif hasattr(cb, "__class__"):
        return type(cb).__name__
    else:
        return "Unknown"


def is_callable_async(cb: Callable[..., Any], /) -> bool:
    """
    Checks whether the given callable object is asynchronous.
    :param cb: The callable object to be checked.
    :return: `True` if the callable object is asynchronous, `False` otherwise.
    """
    if ismethod(cb) or isfunction(cb) or isbuiltin(cb):
        return iscoroutinefunction(cb) or isasyncgenfunction(cb)
    elif not isclass(cb) and hasattr(cb, "__call__"):  # A callable class instance
        return iscoroutinefunction(cb.__call__) or isasyncgenfunction(cb.__call__)
    else:
        return False


def is_callable_generator(cb: Callable[..., Any], /) -> bool:
    """
    Checks whether the provided callable object is a generator.
    :param cb: The callable object to be checked.
    :return:`True` if the callable object is a generator, `False` otherwise.
    """
    if ismethod(cb) or isfunction(cb) or isbuiltin(cb):
        return isgeneratorfunction(cb) or isasyncgenfunction(cb)
    elif not isclass(cb) and hasattr(cb, "__call__"):  # A callable class instance
        return isgeneratorfunction(cb.__call__) or isasyncgenfunction(cb.__call__)
    else:
        return False
