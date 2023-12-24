import asyncio
import hmac
from hashlib import sha256
from pickle import dumps, loads
from types import ModuleType
from typing import Any, Dict, NamedTuple, Callable

from ... import EventEmitter
from ...core.exceptions import PyventusException

try:  # pragma: no cover
    from celery import Celery
except ImportError:  # pragma: no cover
    raise PyventusException(
        "Optional dependency 'celery' not found."
        "\nPlease install it using 'pip install pyventus[celery]' to use this event emitter."
    )


class CeleryEventTaskExecutor:
    """
    A Celery integration for enqueuing and processing event tasks.

    This class registers an event processor task within the provided Celery
    instance. It securely enqueues the given event tasks using a hash mechanism
    for integrity verification.
    """

    class _CeleryEventTaskPayload(NamedTuple):
        """Represents the payload data sent to Celery."""

        serialized_task: bytes
        """Serialized task."""

        task_hash: bytes
        """Hash value of the serialized task."""

        def to_json(self) -> Dict[str, Any]:
            """
            Convert the payload to a JSON-compatible dictionary.
            :return: JSON-compatible dictionary representing the payload.
            """
            return self._asdict()

        @classmethod
        def from_json(cls, **kwargs):
            """
            Create a Payload instance from a JSON-compatible dictionary.
            :param kwargs: JSON-compatible dictionary representing the payload.
            :return: Payload instance.
            :raises ValueError: If the JSON data is missing fields or contains extra keys.
            """
            # Get the field names of the named tuple
            tuple_fields: tuple[str, ...] = CeleryEventTaskExecutor._CeleryEventTaskPayload._fields

            # Check if all the fields are present in the JSON data
            if not set(tuple_fields).issubset(kwargs.keys()):
                raise ValueError("Missing fields in JSON data.")

            # Check for extra keys in the JSON data
            extra_keys = set(kwargs.keys()) - set(tuple_fields)
            if extra_keys:
                raise ValueError("Extra keys in JSON data: {}".format(extra_keys))

            # Create the named tuple using the JSON data
            return cls(**kwargs)

    def __init__(self, celery: Celery, secret: str, queue_name: str | None = None):
        """
        Initialize the `CeleryEventTaskExecutor`.
        :param celery: The Celery instance used to enqueue and process event tasks.
        :param secret: The secret key used for message authentication and integrity validation.
            This key is used for hashing the event task and verifying its integrity.
        :param queue_name: The name of the queue where the task will be enqueued.
            Default is None (task_default_queue).
        :raises PyventusException: If the Celery instance or secret key is missing,
            or if the content type 'application/x-python-serialize' is not accepted.
        """
        if celery is None:
            raise PyventusException("The 'celery' argument cannot be None.")

        if not secret:
            raise PyventusException("The 'secret' argument cannot be empty.")

        if "application/x-python-serialize" not in celery.conf.accept_content:
            raise PyventusException(
                "Unsupported content type. "
                "'application/x-python-serialize' is not in the list of accepted content types."
            )

        self.__celery: Celery = celery
        """The Celery instance."""

        self.__queue_name: str = self.__celery.conf.task_default_queue if queue_name is None else queue_name
        """The name of the queue where the task will be enqueued."""

        self.__secret: bytes = secret.encode("utf-8")
        """The secret key used for message authentication and integrity validation, encoded as bytes."""

        self.__digestmod: str | Callable[[], Any] | ModuleType = sha256
        """The digest algorithm used for hashing."""

        # Registers the event processor method as a Celery task.
        self.__celery.task(self._event_processor, name=self._event_processor.__name__, queue=self.__queue_name)

    def enqueue(self, task: EventEmitter.EventTask) -> None:
        """
        Enqueues an event task for asynchronous processing.

        This method takes an `EventTask` object and enqueues it for asynchronous
        execution by Celery workers. It first serializes the event task and then
        calculates its HMAC hash using the secret key. This hash is used to
        verify the integrity of the even task.

        :param task: The event task to queue for processing.
        :return: None
        """
        # Serialize the event task
        serialized_task: bytes = dumps(task)

        # Calculate the hash of the serialized task using the secret key
        task_hash: bytes = hmac.new(key=self.__secret, msg=serialized_task, digestmod=self.__digestmod).digest()

        # Create a payload object with the serialized task and its hash
        payload = CeleryEventTaskExecutor._CeleryEventTaskPayload(
            serialized_task=serialized_task,
            task_hash=task_hash,
        )

        # Send the event task to Celery for execution
        self.__celery.send_task(
            self._event_processor.__name__,
            kwargs=payload.to_json(),
            queue=self.__queue_name,
        )

    def _event_processor(self, **kwargs) -> None:
        """
        Processes the event task execution.
        :param kwargs: The JSON-compatible dictionary representing the event task payload.
        :return: None
        :raises PyventusException: If the event task hash is invalid or fails to deserialize.
        """
        # Build the payload
        payload = CeleryEventTaskExecutor._CeleryEventTaskPayload.from_json(**kwargs)

        # Calculate the hash of the event task using the secret key
        task_hash: bytes = hmac.new(key=self.__secret, msg=payload.serialized_task, digestmod=self.__digestmod).digest()

        # Compare the calculated hash with the provided payload hash
        if not hmac.compare_digest(payload.task_hash, task_hash):
            raise PyventusException("Event task hash mismatch. The provided event task is invalid.")

        # Deserialize the event task
        task: EventEmitter.EventTask = loads(payload.serialized_task)

        # Check if the deserialized task is valid
        if task is None or not isinstance(task, EventEmitter.EventTask):
            raise PyventusException("Failed to deserialize event task.")

        # Run the event task
        asyncio.run(task())
