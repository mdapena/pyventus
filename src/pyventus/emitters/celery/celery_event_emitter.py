import asyncio
import hmac
from hashlib import sha256
from pickle import dumps, loads
from types import ModuleType
from typing import Any, Dict, NamedTuple, Callable, cast, Type

from ..event_emitter import EventEmitter
from ...core.exceptions import PyventusException
from ...linkers import EventLinker

try:  # pragma: no cover
    from celery import Celery
except ImportError:  # pragma: no cover
    raise PyventusException(
        "Optional dependency 'celery' not found."
        "\nPlease install it using 'pip install pyventus[celery]' to use this event emitter."
    )


class CeleryEventEmitter(EventEmitter):
    """
    A class that enables event handling using the powerful Celery distributed task queue system.

    This class extends the base `EventEmitter` class and provides the functionality to enqueue and
    event handlers using `Celery`. Once enqueued, these event handlers are processed asynchronously
    by `Celery` workers. The `CeleryEventEmitter` is particularly useful when dealing with events
    that require resource-intensive tasks.

    The `CeleryEventEmitter` works by utilizing the provided `Queue` instance to enqueue the event
    emissions for asynchronous processing.

    For more information and code examples, please refer to the `CeleryEventEmitter` tutorials at:
    [https://mdapena.github.io/pyventus/tutorials/emitters/celery/](https://mdapena.github.io/pyventus/tutorials/emitters/celery/).
    """

    class Queue:
        """A class representing the Celery task queue used for enqueuing event emissions."""

        class Serializer:
            """`EventEmission` Serializer for Celery Tasks"""

            @staticmethod
            def dumps(obj: EventEmitter.EventEmission) -> Any:
                """
                Serializes the event emission object
                :param obj: The event emission object to be serialized.
                :return: The serialized representation of the event emission object.
                """
                return dumps(obj)  # pragma: no cover

            @staticmethod
            def loads(serialized_obj: Any) -> EventEmitter.EventEmission:
                """
                Deserializes the task payload back to the event emission object.
                :param serialized_obj: The serialized object to be loaded.
                :return: The deserialized event emission object.
                """
                return cast(EventEmitter.EventEmission, loads(serialized_obj))  # pragma: no cover

        class _Payload(NamedTuple):
            """Represents the payload data sent to Celery."""

            serialized_obj: bytes
            """The serialized event emission object."""

            obj_hash: bytes | None
            """The hash of the serialized event emission object."""

            def to_json(self) -> Dict[str, Any]:
                """
                Converts the payload to a JSON-compatible dictionary.
                :return: JSON-compatible dictionary representing the payload.
                """
                return self._asdict()

            @classmethod
            def from_json(cls, **kwargs: Any) -> "CeleryEventEmitter.Queue._Payload":
                """
                Creates a Payload instance from a JSON-compatible dictionary.
                :param kwargs: JSON-compatible dictionary representing the payload.
                :return: Payload instance.
                :raises ValueError: If the JSON data is missing fields or contains extra keys.
                """
                # Get the field names of the named tuple
                tuple_fields: tuple[str, ...] = CeleryEventEmitter.Queue._Payload._fields

                # Check if all the fields are present in the JSON data
                if not set(tuple_fields).issubset(kwargs.keys()):
                    raise PyventusException("Missing fields in JSON data.")

                # Check for extra keys in the JSON data
                extra_keys = set(kwargs.keys()) - set(tuple_fields)
                if extra_keys:
                    raise PyventusException("Extra keys in JSON data: {}".format(extra_keys))

                # Create the named tuple using the JSON data
                return cls(**kwargs)

        def __init__(
            self,
            celery: Celery,
            name: str | None = None,
            secret: str | None = None,
            serializer: Type[Serializer] = Serializer,
        ):
            """
            Initialize the Celery event emitter `Queue`.
            :param celery: The Celery instance used to enqueue and process event emissions.
            :param name: The name of the queue where the event emission will be enqueued.
                Default is None (task_default_queue).
            :param secret: The secret key used for message authentication and integrity validation.
                This key is used for hashing the event emission object and verifying its integrity.
            :param serializer: The serializer class used for serializing and deserializing event
                emission objects.
            :raises PyventusException: If the Celery instance is None, or the secret key is not None
                and empty, or if the content type 'application/x-python-serialize' is not accepted.
            """
            if celery is None:
                raise PyventusException("The 'celery' argument cannot be None.")

            if secret is not None and len(secret) == 0:
                raise PyventusException("The 'secret' argument cannot be empty.")

            if "application/x-python-serialize" not in celery.conf.accept_content:
                raise PyventusException(
                    "Unsupported content type. "
                    "'application/x-python-serialize' is not in the list of accepted content types."
                )

            self._celery: Celery = celery
            """The Celery instance."""

            self._name: str = self._celery.conf.task_default_queue if name is None else name
            """The name of the queue where the event emission will be enqueued."""

            self._secret: bytes | None = secret.encode("utf-8") if secret else None
            """The secret key used for message authentication and integrity validation, encoded as bytes."""

            self._digestmod: str | Callable[[], Any] | ModuleType = sha256
            """The digest algorithm used for hashing."""

            self._serializer: Type[CeleryEventEmitter.Queue.Serializer] = serializer
            """The serializer class used for serializing and deserializing event emission objects."""

            # Registers the event processor method as a Celery task.
            self._celery.task(self._executor, name=self._executor.__name__, queue=self._name)

        def enqueue(self, event_emission: EventEmitter.EventEmission) -> None:
            """
            Enqueues an event emission object for asynchronous processing in Celery.

            This method takes an `EventEmission` object and enqueues it for asynchronous
            execution by Celery workers. If a secret key is provided during initialization,
            the event emission object is first serialized, and its hash is calculated using
            the secret key. This hash is used to verify the integrity of the event emission
            object during processing.

            :param event_emission: The event emission object to be queued for processing.
            :return: None
            """
            # Serialize the event emission object
            serialized_obj: Any = self._serializer.dumps(event_emission)

            # Calculate the hash of the serialized object if a secret key was provided
            obj_hash: Any | None = None
            if self._secret:  # pragma: no cover
                obj_hash = hmac.new(key=self._secret, msg=serialized_obj, digestmod=self._digestmod).digest()

            # Create a payload with the serialized event emission instance and its hash
            payload = CeleryEventEmitter.Queue._Payload(
                serialized_obj=serialized_obj,
                obj_hash=obj_hash,
            )

            # Send the event emission to Celery for execution
            self._celery.send_task(
                self._executor.__name__,
                kwargs=payload.to_json(),
                queue=self._name,
            )

        def _executor(self, **kwargs: Any) -> None:
            """
            Processes the enqueued event emission object.

            This method is the actual Celery task that processes the enqueued event emission.
            It deserializes the event emission object and verifies its integrity.

            :param kwargs: The JSON-compatible dictionary representing the payload.
            :return: None
            """
            # Create a Payload instance from the payload JSON data
            payload = CeleryEventEmitter.Queue._Payload.from_json(**kwargs)

            # Check payload
            if self._secret:  # pragma: no cover
                if not payload.obj_hash:
                    raise PyventusException("Invalid payload structure.")

                # Verify the integrity of the payload
                obj_hash: bytes = hmac.new(
                    key=self._secret, msg=payload.serialized_obj, digestmod=self._digestmod
                ).digest()

                # Compare the calculated hash with the provided payload hash
                if not hmac.compare_digest(payload.obj_hash, obj_hash):
                    raise PyventusException("Payload integrity verification failed.")
            elif payload.obj_hash:  # pragma: no cover
                raise PyventusException("Unexpected payload structure.")

            # Deserialize the event emission object
            event_emission = self._serializer.loads(payload.serialized_obj)

            # Check if the deserialized event emission object is valid
            if event_emission is None:  # pragma: no cover
                raise PyventusException("Failed to deserialize the event emission object.")

            # Run the event emission
            asyncio.run(event_emission())

    def __init__(self, queue: Queue, event_linker: Type[EventLinker] = EventLinker, debug: bool | None = None):
        """
        Initializes an instance of the `CeleryEventEmitter` class.
        :param queue: The celery event task executor used to process the event task.
        :param event_linker: Specifies the type of event linker to use for associating
            events with their respective event handlers. Defaults to `EventLinker`.
        :param debug: Specifies the debug mode for the logger. If `None`, it is
            determined based on the execution environment.
        """
        # Call the parent class' __init__ method to set up the event linker
        super().__init__(event_linker=event_linker, debug=debug)

        # Validate the executor argument
        if queue is None:
            raise PyventusException("The 'queue' argument cannot be None")

        # Store the queue instance
        self._queue: CeleryEventEmitter.Queue = queue
        """The Queue instance used to process the event emission."""

    def _process(self, event_emission: EventEmitter.EventEmission) -> None:
        # Add the event emission to the Celery Queue
        self._queue.enqueue(event_emission=event_emission)
