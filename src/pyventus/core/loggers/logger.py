from ..utils import attributes_repr, formatted_repr
from .stdout_logger import StdOutLogger


class Logger:
    """A custom logger class that wraps the `StdOutLogger` and provides additional functionality."""

    # Attributes for the Logger
    __slots__ = ("__name", "__debug")

    def __init__(self, name: str | None = None, debug: bool = False):
        """
        Initialize an instance of `Logger`.

        :param name: The name of the logger instance.
        :param debug: A flag indicating whether debug mode is enabled.
        """
        self.__name: str | None = name
        self.__debug = debug

    def __repr__(self) -> str:  # pragma: no cover
        """
        Retrieve a string representation of the instance.

        :return: A string representation of the instance.
        """
        return formatted_repr(
            instance=self,
            info=attributes_repr(
                name=self.__name,
                debug=self.__debug,
            ),
        )

    @property
    def debug_enabled(self) -> bool:
        """
        Return a boolean value indicating whether debug mode is enabled.

        :return: `True` if debug mode is enabled, `False` otherwise.
        """
        return self.__debug

    def error(self, msg: str, action: str | None = None) -> None:
        """
        Log an ERROR level message.

        :param msg: The message to be logged.
        :param action: The action or method associated with the log. Defaults to None.
        :return: None.
        """
        StdOutLogger.error(msg=msg, name=self.__name, action=action)

    def warning(self, msg: str, action: str | None = None) -> None:
        """
        Log a WARNING level message.

        :param msg: The message to be logged.
        :param action: The action or method associated with the log. Defaults to None.
        :return: None.
        """
        StdOutLogger.warning(msg=msg, name=self.__name, action=action)

    def info(self, msg: str, action: str | None = None) -> None:
        """
        Log an INFO level message.

        :param msg: The message to be logged.
        :param action: The action or method associated with the log. Defaults to None.
        :return: None.
        """
        StdOutLogger.info(msg=msg, name=self.__name, action=action)

    def debug(self, msg: str, action: str | None = None) -> None:
        """
        Log a DEBUG level message.

        :param msg: The message to be logged.
        :param action: The action or method associated with the log. Defaults to None.
        :return: None.
        """
        StdOutLogger.debug(msg=msg, name=self.__name, action=action)
