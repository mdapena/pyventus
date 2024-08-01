from abc import ABC, abstractmethod


class Unsubscribable(ABC):
    """
    An abstract base class representing an object that can be unsubscribed from
    a subscribed source.
    """

    @abstractmethod
    def unsubscribe(self) -> bool:
        """
        Release or clean up any resources associated with the subscribed source.
        :return: `True` if the unsubscribe operation was successful; `False` if it was already unsubscribed.
        :raises Exception: Any exception raised during the unsubscription process.
        """
        pass
