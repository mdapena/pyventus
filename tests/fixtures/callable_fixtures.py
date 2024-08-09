from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Awaitable, Callable, Dict, Generator, Tuple


class CallableMock:
    """
    A mock callable class for testing purposes.

    This class simulates a callable object that can be used in tests to track
    how many times it has been called, what arguments were passed to it, and
    what it returns or raises when called. It provides both synchronous and
    asynchronous versions of the callable.
    """

    class Base(ABC):
        """
        Base class for callable mocks.

        This abstract base class defines the common properties and initialization
        for both synchronous and asynchronous callable mocks.
        """

        # Attributes for the CallableMock.Base
        __slots__ = ("_call_count", "_last_args", "_last_kwargs", "_return_value", "_exception")

        def __init__(self, return_value: Any | None = None, raise_exception: Exception | None = None):
            """
            Initializes an instance of `CallableMock.Base`.
            :param return_value: The value to return when the callable is invoked, defaults to None.
            :param raise_exception: An exception to raise when the callable is invoked, defaults to None.
            """
            self._call_count: int = 0
            self._last_args: Tuple[Any, ...] = ()
            self._last_kwargs: Dict[str, Any] = {}
            self._return_value: Any | None = return_value
            self._exception: Exception | None = raise_exception

        @abstractmethod
        def __call__(self, *args, **kwargs) -> Any:
            """Abstract method to be implemented by subclasses for callable behavior."""
            pass

        @property
        def call_count(self) -> int:
            """Returns the number of times the callable has been invoked."""
            return self._call_count

        @property
        def last_args(self) -> Tuple[Any, ...]:
            """Returns the positional arguments from the last call."""
            return self._last_args

        @property
        def last_kwargs(self) -> Dict[str, Any]:
            """Returns the keyword arguments from the last call."""
            return self._last_kwargs

        @property
        def return_value(self) -> Any | None:
            """Returns the value that the callable will return when invoked."""
            return self._return_value

        @property
        def exception(self) -> Exception | None:
            """Returns the exception that will be raised when the callable is invoked."""
            return self._exception

    class Sync(Base):
        """Synchronous callable mock."""

        def __call__(self, *args, **kwargs) -> Any:
            """
            Invokes the synchronous callable, tracking call details.
            :param args: Positional arguments for the callable.
            :param kwargs: Keyword arguments for the callable.
            :return: The return value specified during initialization.
            :raises Exception: If an exception was specified during initialization.
            """
            self._call_count += 1
            self._last_args = args
            self._last_kwargs = kwargs

            if self._exception and issubclass(self._exception.__class__, Exception):
                raise self._exception

            return self._return_value

    class Async(Base):
        """Asynchronous callable mock."""

        async def __call__(self, *args, **kwargs) -> Any:
            """
            Invokes the asynchronous callable, tracking call details.
            :param args: Positional arguments for the callable.
            :param kwargs: Keyword arguments for the callable.
            :return: The return value specified during initialization.
            :raises Exception: If an exception was specified during initialization.
            """
            self._call_count += 1
            self._last_kwargs = kwargs
            self._last_args = args

            if self._exception and issubclass(self._exception.__class__, Exception):
                raise self._exception

            return self._return_value


# ----------------------------------------------
# Callables
# ----------


def _sync_function(*args, **kwargs):
    """A dummy synchronous function."""
    pass  # pragma: no cover


def _sync_generator_function(*args, **kwargs):
    """A dummy synchronous generator function."""
    yield  # pragma: no cover


async def _async_function(*args, **kwargs):
    """A dummy asynchronous function."""
    pass  # pragma: no cover


async def _async_generator_function(*args, **kwargs):
    """A dummy asynchronous generator function."""
    yield  # pragma: no cover


class DummyCallable:
    """A collection of dummy callable fixtures for synchronous and asynchronous operations."""

    class Sync:
        """Contains dummy synchronous callable fixtures."""

        class Generator:
            """Contains dummy synchronous generator callable fixtures."""

            func: Generator[None, None, None] = _sync_generator_function

            @staticmethod
            def static(*args, **kwargs):
                yield  # pragma: no cover

            @classmethod
            def cls(cls, *args, **kwargs):
                yield  # pragma: no cover

            def inst(sel, *args, **kwargs):
                yield  # pragma: no cover

            def __call__(self, *args, **kwargs):
                yield  # pragma: no cover

            @property
            def ALL(self) -> Tuple[Generator]:
                """
                Return a tuple of all dummy synchronous generator callables.

                This includes:
                -   A synchronous generator function.
                -   A static synchronous generator method.
                -   A class synchronous generator method .
                -   A instance synchronous generator method.
                -   A __call__ synchronous generator method.
                """
                return (
                    type(self).func,
                    type(self).static,
                    type(self).cls,
                    self.inst,
                    self,
                )

            @property
            def ALL_NAMES(self) -> Tuple[str]:
                """
                Return a tuple of all dummy synchronous generator callable names.

                This includes:
                -   A synchronous generator function.
                -   A static synchronous generator method.
                -   A class synchronous generator method .
                -   A instance synchronous generator method.
                -   A __call__ synchronous generator method.
                """
                return (
                    type(self).func.__name__,
                    type(self).static.__name__,
                    type(self).cls.__name__,
                    self.inst.__name__,
                    type(self).__name__,
                )

        func: Callable[..., None] = _sync_function

        lamb: Callable[..., None] = lambda *args: None

        @staticmethod
        def static(*args, **kwargs) -> None:
            pass  # pragma: no cover

        @classmethod
        def cls(cls, *args, **kwargs) -> None:
            pass  # pragma: no cover

        def inst(self, *args, **kwargs) -> None:
            pass  # pragma: no cover

        def __call__(self, *args, **kwargs) -> None:
            pass  # pragma: no cover

        @property
        def ALL(self) -> Tuple[Callable]:
            """
            Return a tuple of all dummy synchronous callables.

            This includes:
            -   A synchronous function.
            -   A lambda function.
            -   A static synchronous method.
            -   A class synchronous method.
            -   A instance synchronous method.
            -   A __call__ synchronous method.
            """
            return (
                type(self).func,
                type(self).lamb,
                type(self).static,
                type(self).cls,
                self.inst,
                self,
            )

        @property
        def ALL_NAMES(self) -> Tuple[str]:
            """
            Return a tuple of all dummy synchronous callable names.

            This includes:
            -   A synchronous function.
            -   A lambda function.
            -   A static synchronous method.
            -   A class synchronous method.
            -   A instance synchronous method.
            -   A __call__ synchronous method.
            """
            return (
                type(self).func.__name__,
                type(self).lamb.__name__,
                type(self).static.__name__,
                type(self).cls.__name__,
                self.inst.__name__,
                type(self).__name__,
            )

    class Async:
        """Contains dummy asynchronous callable fixtures."""

        class Generator:
            """Contains dummy asynchronous generator callable fixtures."""

            func: AsyncGenerator[None, None] = _async_generator_function

            @staticmethod
            async def static(*args, **kwargs):
                yield  # pragma: no cover

            @classmethod
            async def cls(cls, *args, **kwargs):
                yield  # pragma: no cover

            async def inst(self, *args, **kwargs):
                yield  # pragma: no cover

            async def __call__(self, *args, **kwargs):
                yield  # pragma: no cover

            @property
            def ALL(self) -> Tuple[AsyncGenerator]:
                """
                Return a tuple of all dummy asynchronous generator callables.

                This includes:
                -   An asynchronous generator function.
                -   A static asynchronous generator method.
                -   A class asynchronous generator method .
                -   A instance asynchronous generator method.
                -   A __call__ asynchronous generator method.
                """
                return (
                    type(self).func,
                    type(self).static,
                    type(self).cls,
                    self.inst,
                    self,
                )

            @property
            def ALL_NAMES(self) -> Tuple[str]:
                """
                Return a tuple of all dummy asynchronous generator callable names.

                This includes:
                -   An asynchronous generator function.
                -   A static asynchronous generator method.
                -   A class asynchronous generator method .
                -   A instance asynchronous generator method.
                -   A __call__ asynchronous generator method.
                """
                return (
                    type(self).func.__name__,
                    type(self).static.__name__,
                    type(self).cls.__name__,
                    self.inst.__name__,
                    type(self).__name__,
                )

        func: Callable[..., Awaitable[None]] = _async_function

        @staticmethod
        async def static(*args, **kwargs):
            pass  # pragma: no cover

        @classmethod
        async def cls(cls, *args, **kwargs):
            pass  # pragma: no cover

        async def inst(self, *args, **kwargs):
            pass  # pragma: no cover

        async def __call__(self, *args, **kwargs):
            pass  # pragma: no cover

        @property
        def ALL(self) -> Tuple[Callable]:
            """
            Return a tuple of all dummy asynchronous callables.

            This includes:
            -   An asynchronous function.
            -   A static asynchronous method.
            -   A class asynchronous method.
            -   A instance asynchronous method.
            -   A __call__ asynchronous method.
            """
            return (
                type(self).func,
                type(self).static,
                type(self).cls,
                self.inst,
                self,
            )

        @property
        def ALL_NAMES(self) -> Tuple[str]:
            """
            Return a tuple of all dummy asynchronous callable names.

            This includes:
            -   An asynchronous function.
            -   A static asynchronous method.
            -   A class asynchronous method.
            -   A instance asynchronous method.
            -   A __call__ asynchronous method.
            """
            return (
                type(self).func.__name__,
                type(self).static.__name__,
                type(self).cls.__name__,
                self.inst.__name__,
                type(self).__name__,
            )

    class Invalid:
        """Represents an invalid callable fixture."""

        pass  # pragma: no cover