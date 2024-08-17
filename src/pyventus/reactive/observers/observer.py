from abc import ABC, abstractmethod
from typing import Generic, TypeVar

_in_T = TypeVar("_in_T", contravariant=True)
"""A generic type representing the input value for the `next` method of the observer."""


class Observer(ABC, Generic[_in_T]):
    """
    An abstract base class that defines the workflow and essential protocols for
    responding to state changes emitted by an observable, including procedures
    for handling `next`, `error`, and `complete` notifications.

    **Notes:**

    -   This class is parameterized by the type of value that will be received
        in the `next` method.
    """

    # Allow subclasses to define __slots__
    __slots__ = ()

    @abstractmethod
    async def next(self, value: _in_T) -> None:
        """
        Handle the next value emitted by the observable.
        :param value: The value emitted by the observable.
        :return: None
        """
        pass

    @abstractmethod
    async def error(self, exception: Exception) -> None:
        """
        Handle an error that occurs in the observable.
        :param exception: The exception that was raised by the observable.
        :return: None
        """
        pass

    @abstractmethod
    async def complete(self) -> None:
        """
        Handle the completion of the observable.
        :return: None
        """
        pass
