from collections.abc import Callable
from datetime import datetime
from typing import Any

from typing_extensions import Self, override

from ..utils import attributes_repr, get_callable_name, validate_callable
from .unsubscribable import Unsubscribable


class Subscription(Unsubscribable):
    """
    A base class that represents a subscription to a source.

    **Notes:**

    -   This class encapsulates the subscription lifecycle and provides a
        mechanism for releasing or cleaning up any associated resources.
    """

    # Attributes for the Subscription
    __slots__ = ("__timestamp", "__teardown_callback")

    def __init__(self, teardown_callback: Callable[[Self], bool]) -> None:
        """
        Initialize an instance of `Subscription`.

        :param teardown_callback: A callback function invoked during the
            unsubscription process to perform cleanup or teardown operations
            associated with the subscription. It should return `True` if the
            cleanup was successful, or `False` if the teardown has already been
            executed and the subscription is no longer active.
        """
        # Validate the teardown callback
        validate_callable(teardown_callback)

        # Initialize attributes
        self.__timestamp: datetime = datetime.now()
        self.__teardown_callback: Callable[[Self], bool] = teardown_callback

    def __repr__(self) -> str:
        """
        Retrieve a string representation of the instance.

        :return: A string representation of the instance.
        """
        return attributes_repr(
            timestamp=self.__timestamp.strftime("%Y-%m-%d %I:%M:%S %p"),
            teardown_callback=get_callable_name(self.__teardown_callback),
        )

    @property
    def timestamp(self) -> datetime:
        """
        Retrieve the timestamp when the subscription was created.

        :return: The timestamp when the subscription was created.
        """
        return self.__timestamp

    @override
    def unsubscribe(self: Self) -> bool:
        return self.__teardown_callback(self)

    def __getstate__(self) -> dict[str, Any]:
        """
        Prepare the object state for serialization.

        This method is called when the object is pickled. It returns a dictionary
        containing the attributes that should be serialized. Only the attributes
        that are necessary for reconstructing the object in another process or
        context are included to improve efficiency and avoid issues with
        contextually irrelevant attributes.

        :return: A dictionary containing the serialized state of the object.
        """
        # Include only the attributes that are necessary for serialization
        # Attributes like __teardown_callback are not included as they are
        # context-specific and do not make sense in another scope/process.
        return {"__timestamp": self.__timestamp}

    def __setstate__(self, state: dict[str, Any]) -> None:
        """
        Restore the object from the serialized state.

        This method is called when the object is unpickled. It takes a dictionary
        containing the serialized state and restores the object's attributes.
        Additionally, it sets default values for attributes that were not serialized,
        ensuring the object remains in a valid state after deserialization.

        :param state: A dictionary containing the serialized state of the object.
        :return: None
        """
        # Restore the attributes from the serialized state
        self.__timestamp = state["__timestamp"]

        # Set default values for attributes that were not serialized
        self.__teardown_callback = lambda sub: False
