import sys
from datetime import datetime
from typing import Any, Callable, Dict, override

from ..utils import validate_callable
from .unsubscribable import Unsubscribable

if sys.version_info >= (3, 11):  # pragma: no cover
    from typing import Self
else:
    from typing_extensions import Self


class Subscription(Unsubscribable):
    """
    A base class that represents a subscription to a source and provides a
    mechanism to release or clean up any associated resources.
    """

    # Attributes for the Subscription
    __slots__ = ("__timestamp", "__teardown_callback")

    @property
    def timestamp(self) -> datetime:
        """
        Retrieves the timestamp when the subscription was created.
        :return: The timestamp when the subscription was created.
        """
        return self.__timestamp

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

    @override
    def unsubscribe(self: Self) -> bool:
        return self.__teardown_callback(self)

    def __getstate__(self) -> Dict[str, Any]:
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

    def __setstate__(self, state: Dict[str, Any]) -> None:
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

    def __str__(self) -> str:  # pragma: no cover
        """
        Return a formatted string representation of the subscription.
        :return: A string representation of the subscription.
        """
        return f"Subscription(timestamp='{self.__timestamp.strftime('%Y-%m-%d %I:%M:%S %p')}')"
