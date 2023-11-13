import logging
import sys
from abc import ABC

from src.pyventex.core.constants import StdOutColors


class StdOutLogger(ABC):
    """
    StdOutLogger is a simple logging interface for logging operations to the standard output.

    This class provides a straightforward logging interface for writing log messages to the standard output.
    """

    class Handler:
        """ Inner class representing a logger handler. """

        @classmethod
        def get_color_by_level(cls, level: int):
            """
            Returns the color code associated with the specified log level.
            :param level: The log level for which to retrieve the color code.
            :return: The color code associated with the log level.
            """
            if level == logging.INFO:
                return StdOutColors.GREEN
            elif level == logging.DEBUG:
                return StdOutColors.PURPLE
            elif level == logging.WARNING:
                return StdOutColors.YELLOW
            elif level == logging.ERROR:
                return StdOutColors.RED
            return StdOutColors.DEFAULT

        @classmethod
        def get_stream_handler_by_level(cls, level: int) -> logging.StreamHandler:
            """
            Returns a stream handler configured with the specified log level.
            :param level: The log level to set for the stream handler.
            :return: The configured stream handler.
            """
            # Determine the color based on the log level
            level_color: str = cls.get_color_by_level(level=level)

            # Define the logger format
            logger_format: str = f"{level_color}[Logger]  " + \
                                 f"{StdOutColors.DEFAULT}%(asctime)s " + \
                                 f"{level_color}%(levelname)8s" + \
                                 f"{level_color} %(message)s"

            # Create a formatter with the logger format
            formatter = logging.Formatter(logger_format, datefmt="%Y-%m-%d %H:%M:%S %p")

            # Create a stream handler using sys.stdout as the stream
            stream_handler = logging.StreamHandler(stream=sys.stdout)

            # Set the formatter for the stream handler
            stream_handler.setFormatter(fmt=formatter)

            # Return the configured stream handler
            return stream_handler

        @classmethod
        def build_log(cls, level: int, msg: str, name: str | None = None, action: str | None = None) -> str:
            """
            Builds a log message string with the specified log level, message, name, and action.
            :param level: The log level of the message.
            :param msg: The log message.
            :param name: The name of the logger or class associated with the log. Defaults to None.
            :param action: The action or method associated with the log. Defaults to None.
            :return: The formatted log message string.
            """
            # Determine the color based on the log level
            level_color: str = cls.get_color_by_level(level=level)

            # Build the log message string
            log: str = f"{StdOutColors.DEFAULT}[{name if name else 'StdOutLogger'}]" + \
                       f"{level_color} {action if action else 'Message: '}" + \
                       f"{StdOutColors.DEFAULT}{msg}"
            return log

    # Configure loggers for each logging level
    __error_logger = logging.getLogger(name='error_logger')
    __error_logger.setLevel(level=logging.ERROR)

    __warning_logger = logging.getLogger(name='warning_logger')
    __warning_logger.setLevel(level=logging.WARNING)

    __info_logger = logging.getLogger(name='info_logger')
    __info_logger.setLevel(level=logging.INFO)

    __debug_logger = logging.getLogger(name='debug_logger')
    __debug_logger.setLevel(level=logging.DEBUG)

    # Add stream handlers to each logger
    __error_logger.addHandler(hdlr=Handler.get_stream_handler_by_level(level=__error_logger.level))
    __warning_logger.addHandler(hdlr=Handler.get_stream_handler_by_level(level=__warning_logger.level))
    __info_logger.addHandler(hdlr=Handler.get_stream_handler_by_level(level=__info_logger.level))
    __debug_logger.addHandler(hdlr=Handler.get_stream_handler_by_level(level=__debug_logger.level))

    @classmethod
    def error(cls, msg: str, name: str | None = None, action: str | None = None) -> None:
        """
        Logs an ERROR level message.
        :param msg: The message to be logged.
        :param name: The name of the logger or class associated with the log. Defaults to None.
        :param action: The action or method associated with the log. Defaults to None.
        :return: None
        """
        cls.__error_logger.error(cls.Handler.build_log(level=logging.ERROR, msg=msg, name=name, action=action))

    @classmethod
    def warning(cls, msg: str, name: str | None = None, action: str | None = None) -> None:
        """
        Logs a WARNING level message.
        :param msg: The message to be logged.
        :param name: The name of the logger or class associated with the log. Defaults to None.
        :param action: The action or method associated with the log. Defaults to None.
        :return: None
        """
        cls.__warning_logger.warning(cls.Handler.build_log(level=logging.WARNING, msg=msg, name=name, action=action))

    @classmethod
    def info(cls, msg: str, name: str | None = None, action: str | None = None) -> None:
        """
        Logs an INFO level message.
        :param msg: The message to be logged.
        :param name: The name of the logger or class associated with the log. Defaults to None.
        :param action: The action or method associated with the log. Defaults to None.
        :return: None
        """
        cls.__info_logger.info(cls.Handler.build_log(level=logging.INFO, msg=msg, name=name, action=action))

    @classmethod
    def debug(cls, msg: str, name: str | None = None, action: str | None = None) -> None:
        """
        Logs a DEBUG level message.
        :param msg: The message to be logged.
        :param name: The name of the logger or class associated with the log. Defaults to None.
        :param action: The action or method associated with the log. Defaults to None.
        :return: None
        """
        cls.__debug_logger.debug(cls.Handler.build_log(level=logging.DEBUG, msg=msg, name=name, action=action))
