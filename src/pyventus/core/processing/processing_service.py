from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, TypeAlias

ProcessingServiceCallbackType: TypeAlias = Callable[..., Any]
"""Type alias for the callback that can be executed by the processing service."""


class ProcessingService(ABC):
    """
    A base class that defines a common interface for processing calls.

    **Notes:**

    -   The main goal of this class is to decouple the process of executing calls from
        the underlying implementation, thereby establishing a template for defining a
        variety of strategies to manage the execution.
    """

    # Allow subclasses to define __slots__
    __slots__ = ()

    @abstractmethod
    def submit(self, callback: ProcessingServiceCallbackType, *args: Any, **kwargs: Any) -> None:
        """
        Submit a callback along with its arguments for execution.

        Subclasses must implement this method to define the specific execution strategy.

        :param callback: The callback to be executed.
        :param args: Positional arguments to be passed to the callback.
        :param kwargs: Keyword arguments to be passed to the callback.
        :return: None.
        """
        pass
