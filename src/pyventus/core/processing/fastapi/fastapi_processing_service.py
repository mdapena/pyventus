from typing import Any

from typing_extensions import override

from ...exceptions import PyventusException, PyventusImportException
from ...utils import attributes_repr, formatted_repr
from ..processing_service import ProcessingService, ProcessingServiceCallbackType

try:  # pragma: no cover
    from fastapi import BackgroundTasks
except ImportError:  # pragma: no cover
    raise PyventusImportException(import_name="fastapi", is_optional=True, is_dependency=True) from None


class FastAPIProcessingService(ProcessingService):
    """
    A processing service that utilizes the FastAPI's `BackgroundTasks` to handle the execution of calls.

    **Notes:**

    -   This service is specifically designed for FastAPI applications and leverages FastAPI's `BackgroundTasks`
        to handle the callbacks' execution. This is useful for operations that need to happen after a request, but
        that the client doesn't really have to be waiting for the operation to complete before receiving the response.
    """

    # Attributes for the FastAPIProcessingService
    __slots__ = ("__background_tasks",)

    def __init__(self, background_tasks: BackgroundTasks) -> None:
        """
        Initialize an instance of `FastAPIProcessingService`.

        :param background_tasks: The FastAPI `BackgroundTasks` object used to handle callbacks' execution.
        :return: None.
        """
        # Validate the background_tasks instance.
        if background_tasks is None or not isinstance(background_tasks, BackgroundTasks):
            raise PyventusException("The 'background_tasks' argument must be an instance of the BackgroundTasks.")

        # Store the BackgroundTasks instance.
        self.__background_tasks: BackgroundTasks = background_tasks

    def __repr__(self) -> str:
        """
        Retrieve a string representation of the instance.

        :return: A string representation of the instance.
        """
        return formatted_repr(
            instance=self,
            info=attributes_repr(
                background_tasks=self.__background_tasks,
            ),
        )

    @override
    def submit(self, callback: ProcessingServiceCallbackType, *args: Any, **kwargs: Any) -> None:
        # Add the callback to the background_tasks instance as a new task to be executed.
        self.__background_tasks.add_task(callback, *args, **kwargs)
