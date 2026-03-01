from typing import Generic, TypeVar, final

from typing_extensions import override

from ...core.processing.asyncio.asyncio_processing_service import AsyncIOProcessingService
from ...core.utils.repr_utils import attributes_repr, formatted_repr
from ..subscribers.subscriber import Subscriber
from .observable import Observable

_OutT = TypeVar("_OutT", covariant=True)
"""A generic type representing the value that will be streamed through the observable."""


class ObservableStream(Generic[_OutT], Observable[_OutT]):
    """
    An observable subclass that encapsulates a flow of data and offers a mechanism for streaming its entries reactively.

    **Notes:**

    -   The `ObservableStream` class is a data flow-centric observable that focuses exclusively on the stream of its
        entries over time.

    -   Data streaming is managed through a queue, ensuring that the order of entries is preserved and that no
        inconsistent notifications are generated.

    -   Data is streamed to subscribers in a lazy manner, allowing them to receive incremental notifications
        as they occur.
    """

    # Attributes for the ObservableStream.
    __slots__ = ("__processing_service",)

    def __init__(self, debug: bool | None = None) -> None:
        """
        Initialize an instance of `ObservableStream`.

        :param debug: Specifies the debug mode for the logger. If `None`, the mode is determined based on the
            execution environment.
        """
        # Initialize the base Observable class with the specified debug mode.
        super().__init__(debug=debug)

        # Create an AsyncIO processing service to manage data entries and notifications.
        # The enforce_submission_order option is enabled to ensure that entries are processed sequentially.
        self.__processing_service: AsyncIOProcessingService = AsyncIOProcessingService(enforce_submission_order=True)

    @override
    def __repr__(self) -> str:
        return formatted_repr(
            instance=self,
            info=(
                attributes_repr(
                    processing_service=self.__processing_service,
                )
                + f", {super().__repr__()}"
            ),
        )

    async def wait_for_tasks(self) -> None:
        """
        Wait for all background tasks in the current asyncio loop associated with the `ObservableStream` to complete.

        :return: None.
        """
        await self.__processing_service.wait_for_tasks()

    @final  # Prevent overriding in subclasses to maintain the integrity of the `_OutT` type.
    def next(self, value: _OutT) -> None:  # type: ignore[misc]
        """
        Push a value entry to the stream and notify all subscribers.

        :param value: The value entry to be pushed to the stream.
        :return: None.
        """
        with self._thread_lock:
            subscribers: tuple[Subscriber[_OutT], ...] = tuple(self._subscribers)
        self.__processing_service.submit(self._emit_next, value, subscribers)

    def error(self, exception: Exception) -> None:
        """
        Push an error entry to the stream and notify all subscribers.

        :param exception: The error entry to be pushed to the stream.
        :return: None.
        """
        with self._thread_lock:
            subscribers: tuple[Subscriber[_OutT], ...] = tuple(self._subscribers)
        self.__processing_service.submit(self._emit_error, exception, subscribers)

    def complete(self) -> None:
        """
        Push a completion entry to the stream and notify all subscribers.

        Once the notification is sent, all notified subscribers will be removed.

        :return: None.
        """
        with self._thread_lock:
            subscribers: tuple[Subscriber[_OutT], ...] = tuple(self._subscribers)
            self._subscribers.clear()
        self.__processing_service.submit(self._emit_complete, subscribers)
