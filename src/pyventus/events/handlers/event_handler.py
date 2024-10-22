from abc import ABC, abstractmethod
from typing import Any

from ...core.loggers import StdOutLogger
from ...core.utils import summarized_repr


class EventHandler(ABC):
    """An abstract base class that defines the workflow and essential protocols for event handling."""

    # Allow subclasses to define __slots__
    __slots__ = ()

    @abstractmethod
    async def _handle_event(self, *args: Any, **kwargs: Any) -> Any:
        """
        Handle the event response.

        :param args: Positional arguments containing event-specific data.
        :param kwargs: Keyword arguments containing event-specific data.
        :return: The result of handling the event.
        """
        pass

    @abstractmethod
    async def _handle_success(self, results: Any) -> None:
        """
        Handle the successful completion of the event response.

        :param results: The results of handling the event.
        :return: None.
        """
        pass

    @abstractmethod
    async def _handle_failure(self, exception: Exception) -> None:
        """
        Handle the failed completion of the event response.

        :param exception: The exception that occurred during the event handling.
        :return: None.
        """
        pass

    async def execute(self, *args: Any, **kwargs: Any) -> None:
        """
        Execute the event workflow.

        :param args: Positional arguments containing event-specific data.
        :param kwargs: Keyword arguments containing event-specific data.
        :return: None.
        """
        try:
            # Start the event handling process and store the results
            results: Any = await self._handle_event(*args, **kwargs)
        except Exception as exception:
            # Log the exception that occurred during the event handling.
            StdOutLogger.error(source=summarized_repr(self), action="Exception:", msg=f"{repr(exception)}")

            # Handle the failed completion of the event response.
            await self._handle_failure(exception=exception)
        else:
            # Handle the successful completion of the event response.
            await self._handle_success(results=results)
