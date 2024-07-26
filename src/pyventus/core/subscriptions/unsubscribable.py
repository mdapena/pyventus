from abc import ABC, abstractmethod


class Unsubscribable(ABC):
    """
    An abstract base class representing an object that can be unsubscribed from
    a subscribed source.
    """

    @abstractmethod
    def unsubscribe(self) -> None:
        """
        Release or clean up any resources associated with the subscribed source.
        :return: None
        """
        pass
