from asyncio import to_thread
from collections.abc import AsyncGenerator, Awaitable, Callable, Generator
from inspect import (
    isasyncgenfunction,
    isbuiltin,
    isclass,
    iscoroutinefunction,
    isfunction,
    isgeneratorfunction,
    ismethod,
)
from typing import Any, Generic, ParamSpec, TypeAlias, TypeVar, final

from ..exceptions import PyventusException
from ..utils.repr_utils import attributes_repr, formatted_repr

_P = ParamSpec("_P")
"""A generic type representing the names and types of the parameters for a callable."""

_R = TypeVar("_R", covariant=True)
"""A generic type representing the return value of a callable."""

_CallableType: TypeAlias = Callable[_P, _R | Awaitable[_R] | Generator[_R, None, None] | AsyncGenerator[_R, None]]
"""Type alias for a callable."""


@final
class CallableWrapper(Generic[_P, _R]):
    """
    A wrapper class that encapsulates a callable object.

    **Notes:**

    -   This class provides a unified interface for executing callable objects.

    -   If `force_async` is set to `True`, synchronous callables will be executed
        asynchronously using the `asyncio.to_thread` function. If `force_async` is `False`,
        the callable will run in its original context (synchronously or asynchronously, as
        defined). Note that `force_async` only applies to regular callables and does not
        affect generator callables.
    """

    # CallableWrapper attributes
    __slots__ = ("__callable", "__is_generator", "__is_async", "__name", "__force_async")

    def __init__(self, cb: _CallableType[_P, _R], /, *, force_async: bool) -> None:
        """
        Initialize an instance of `CallableWrapper`.

        :param cb: The callable object to be wrapped.
        :param force_async: A flag indicating whether to force the wrapped callable to run asynchronously.
            Note that `force_async` only applies to regular callables and does not affect generator callables.
        :raises PyventusException: If the given callable is invalid or if `force_async` is not a boolean.
        """
        # Validate the given callable object.
        validate_callable(cb)

        # Validate the provided force_async flag.
        if not isinstance(force_async, bool):
            raise PyventusException("The 'force_async' argument must be a boolean value.")

        # Store the callable and its properties.
        self.__callable: _CallableType[_P, _R] = cb
        self.__is_generator: bool = is_callable_generator(cb)
        self.__is_async: bool = is_callable_async(cb)
        self.__name: str = get_callable_name(cb)

        # Store the force_async flag.
        self.__force_async: bool = force_async

    def __repr__(self) -> str:
        """
        Retrieve a string representation of the instance.

        :return: A string representation of the instance.
        """
        return formatted_repr(
            instance=self,
            info=attributes_repr(
                callable=self.__callable,
                is_generator=self.__is_generator,
                is_async=self.__is_async,
                name=self.__name,
                force_async=self.__force_async,
            ),
        )

    @property
    def is_generator(self) -> bool:
        """
        Determine if the wrapped callable is a generator.

        :return: `True` if the wrapped callable is a generator; otherwise, `False`.
        """
        return self.__is_generator

    @property
    def is_async(self) -> bool:
        """
        Determine if the wrapped callable is asynchronous.

        :return: `True` if the wrapped callable is asynchronous; otherwise, `False`.
        """
        return self.__is_async

    @property
    def name(self) -> str:
        """
        Retrieve the name of the wrapped callable object.

        :return: A string representing the name of the wrapped callable object.
        """
        return self.__name

    @property
    def force_async(self) -> bool:
        """
        Determine whether the wrapped callable is forced to run asynchronously.

        :return: A boolean value indicating if the wrapped callable is forced to run
            asynchronously. Note that `force_async` only applies to regular callables
            and does not affect generator callables.
        """
        return self.__force_async

    async def execute(self, *args: _P.args, **kwargs: _P.kwargs) -> _R:
        """
        Execute the wrapped callable with the given arguments.

        :param args: Positional arguments to pass to the wrapped callable.
        :param kwargs: Keyword arguments to pass to the wrapped callable.
        :return: The result of the wrapped callable execution.
        :raises PyventusException: If the wrapped callable is a generator.
        """
        # Ensure that the callable is not a generator before execution.
        if self.__is_generator:
            raise PyventusException("Cannot execute a generator; it must be streamed.")

        if self.__is_async:
            # Execute the callable directly if it is asynchronous.
            return await self.__callable(*args, **kwargs)  # type: ignore[no-any-return, misc]
        elif self.__force_async:
            # If the callable is synchronous and force_async is True, run it in a separate thread.
            return await to_thread(self.__callable, *args, **kwargs)  # type: ignore[arg-type]
        else:
            # If the callable is synchronous and force_async is False, run it synchronously.
            return self.__callable(*args, **kwargs)  # type: ignore[return-value]

    def stream(self, *args: _P.args, **kwargs: _P.kwargs) -> AsyncGenerator[_R, None]:
        """
        Stream the results of the wrapped generator callable.

        :param args: Positional arguments to pass to the wrapped callable.
        :param kwargs: Keyword arguments to pass to the wrapped callable.
        :return: An async generator that yields results from the wrapped callable.
        :raises PyventusException: If the wrapped callable is not a generator.
        """
        # Ensure that the callable is a generator before streaming.
        if not self.__is_generator:
            raise PyventusException("Cannot stream a non-generator; it must be executed.")

        if self.__is_async:
            # If the callable is an async generator, return it directly.
            return self.__callable(*args, **kwargs)  # type: ignore[return-value]
        else:

            async def async_generator() -> AsyncGenerator[_R, None]:
                # Wrap the synchronous generator in an async generator.
                generator: Generator[_R, None, None] = self.__callable(*args, **kwargs)  # type: ignore[assignment]
                for value in generator:
                    yield value

            # Return the async generator.
            return async_generator()


def validate_callable(cb: Callable[..., Any], /) -> None:
    """
    Validate whether the given object is a valid callable.

    :param cb: The object to be validated.
    :return: None.
    :raises PyventusException: If the object is not a valid callable.
    """
    if not callable(cb) or isclass(cb):
        raise PyventusException(f"The '{get_callable_name(cb)}' is not a valid callable object.")


def get_callable_name(cb: Callable[..., Any] | None, /) -> str:
    """
    Retrieve the name of the provided callable.

    :param cb: The callable object.
    :return: The name of the callable as a string.
    """
    if cb is None:
        return "None"
    elif ismethod(cb) or isfunction(cb) or isbuiltin(cb):
        return cb.__name__
    elif not isclass(cb) and callable(cb):
        return type(cb).__name__
    else:
        return "Unknown"


def is_callable_async(cb: Callable[..., Any], /) -> bool:
    """
    Determine whether the given callable object is asynchronous.

    :param cb: The callable object to be checked.
    :return: `True` if the callable object is asynchronous, `False` otherwise.
    """
    if ismethod(cb) or isfunction(cb) or isbuiltin(cb):
        return iscoroutinefunction(cb) or isasyncgenfunction(cb)
    elif not isclass(cb) and hasattr(cb, "__call__") and callable(cb):  # noqa: B004
        return iscoroutinefunction(cb.__call__) or isasyncgenfunction(cb.__call__)
    else:
        return False


def is_callable_generator(cb: Callable[..., Any], /) -> bool:
    """
    Determine whether the provided callable object is a generator.

    :param cb: The callable object to be checked.
    :return:`True` if the callable object is a generator, `False` otherwise.
    """
    if ismethod(cb) or isfunction(cb) or isbuiltin(cb):
        return isgeneratorfunction(cb) or isasyncgenfunction(cb)
    elif not isclass(cb) and hasattr(cb, "__call__") and callable(cb):  # noqa: B004
        return isgeneratorfunction(cb.__call__) or isasyncgenfunction(cb.__call__)
    else:
        return False
