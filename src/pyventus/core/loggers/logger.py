from .stdout_logger import StdOutLogger


class Logger:
    """
    Logger is a custom logger class that wraps the logging module and provides additional functionality.

    This class extends the functionality of the `StdOutLogger` class and adds additional attributes and methods for
    logging and controlling log behavior. It allows for easy logging of messages, events, and errors, and provides
    options to enable or disable debug mode and specify a custom name to be displayed with log messages.
    """

    # Strict class attributes
    __slots__ = ("_name", "_debug")

    @property
    def debug_enabled(self) -> bool:
        """
        Returns a boolean value indicating whether debug mode is enabled.
        :return: `True` if debug mode is enabled, `False` otherwise.
        """
        return self._debug

    def __init__(self, name: str | None = None, debug: bool = False):
        """
        Initializes a new logger instance.
        :param name: The name of the logger instance.
        :param debug: A flag indicating whether debug mode is enabled.
        """
        self._name: str | None = name
        """ The name of the logger. """

        self._debug = debug
        """ A flag indicating whether or not debug mode is enabled. """

    def error(self, msg: str, action: str | None = None) -> None:
        """
        Logs an ERROR level message.
        :param msg: The message to be logged.
        :param action: The action or method associated with the log. Defaults to None.
        :return: None
        """
        StdOutLogger.error(msg=msg, name=self._name, action=action)

    def warning(self, msg: str, action: str | None = None) -> None:
        """
        Logs a WARNING level message.
        :param msg: The message to be logged.
        :param action: The action or method associated with the log. Defaults to None.
        :return: None
        """
        StdOutLogger.warning(msg=msg, name=self._name, action=action)

    def info(self, msg: str, action: str | None = None) -> None:
        """
        Logs an INFO level message.
        :param msg: The message to be logged.
        :param action: The action or method associated with the log. Defaults to None.
        :return: None
        """
        StdOutLogger.info(msg=msg, name=self._name, action=action)

    def debug(self, msg: str, action: str | None = None) -> None:
        """
        Logs a DEBUG level message.
        :param msg: The message to be logged.
        :param action: The action or method associated with the log. Defaults to None.
        :return: None
        """
        StdOutLogger.debug(msg=msg, name=self._name, action=action)
