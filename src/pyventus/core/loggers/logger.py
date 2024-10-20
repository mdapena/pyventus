from ..utils import attributes_repr, formatted_repr, summarized_repr
from .stdout_logger import StdOutLogger


class Logger:
    """A custom logger class that wraps the `StdOutLogger` and provides additional functionality."""

    # Attributes for the Logger
    __slots__ = ("__source", "__debug")

    def __init__(self, source: str | type | object | None = None, debug: bool = False):
        """
        Initialize an instance of `Logger`.

        :param source: The source of the log message, which can be a string, type, or object. Defaults to None.
        :param debug: A flag indicating whether debug mode is enabled.
        """
        # Variable to hold the name of the source.
        source_name: str

        # Determine the name of the source based on its type.
        if source is None:
            source_name = summarized_repr(self)
        elif isinstance(source, str):
            source_name = source
        elif isinstance(source, type):
            source_name = f"{source.__name__}(ClassReference)"
        else:
            source_name = summarized_repr(source)

        # Store the determined source name and debug flag.
        self.__source: str = source_name
        self.__debug = debug

    def __repr__(self) -> str:
        """
        Retrieve a string representation of the instance.

        :return: A string representation of the instance.
        """
        return formatted_repr(
            instance=self,
            info=attributes_repr(
                source=self.__source,
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
        StdOutLogger.error(msg=msg, source=self.__source, action=action)

    def warning(self, msg: str, action: str | None = None) -> None:
        """
        Log a WARNING level message.

        :param msg: The message to be logged.
        :param action: The action or method associated with the log. Defaults to None.
        :return: None.
        """
        StdOutLogger.warning(msg=msg, source=self.__source, action=action)

    def info(self, msg: str, action: str | None = None) -> None:
        """
        Log an INFO level message.

        :param msg: The message to be logged.
        :param action: The action or method associated with the log. Defaults to None.
        :return: None.
        """
        StdOutLogger.info(msg=msg, source=self.__source, action=action)

    def debug(self, msg: str, action: str | None = None) -> None:
        """
        Log a DEBUG level message.

        :param msg: The message to be logged.
        :param action: The action or method associated with the log. Defaults to None.
        :return: None.
        """
        StdOutLogger.debug(msg=msg, source=self.__source, action=action)
