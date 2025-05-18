from logging import (
    CRITICAL,
    DEBUG,
    ERROR,
    INFO,
    NOTSET,
    WARNING,
    Formatter,
    Logger,
    StreamHandler,
    getLogger,
)
from sys import stdout
from types import TracebackType
from typing import TypeAlias

from ...core.constants import StdOutColors

_SysExcInfoType: TypeAlias = tuple[type[BaseException], BaseException, TracebackType | None] | tuple[None, None, None]
"""A type alias representing the supported types of exception information that can be returned by `sys.exc_info()`."""

ExcInfoType: TypeAlias = None | bool | _SysExcInfoType | BaseException
"""A type alias representing the supported types of exception information that can be used in logging methods."""


class StdOutLogger:
    """
    A simple interface for logging messages to the standard output in the Pyventus library.

    **Notes:**

    -   This interface manages the logger setup and ensures that log messages are consistent.
    """

    LOGGER: Logger = getLogger(name="Pyventus")
    """The logger instance of the Pyventus library."""

    LOG_LEVELCOLOR_KEY: str = "levelcolor"
    """The key used to store the color associated with the log level in the log records' extra attributes."""

    LOG_COLORS: dict[int, str] = {
        NOTSET: StdOutColors.DEFAULT,
        CRITICAL: StdOutColors.RED,
        ERROR: StdOutColors.RED,
        WARNING: StdOutColors.YELLOW,
        INFO: StdOutColors.GREEN,
        DEBUG: StdOutColors.PURPLE,
    }
    """A mapping of log levels to their corresponding color codes for console output."""

    @classmethod
    def config(cls, level: int = DEBUG) -> None:
        """
        Configure the Pyventus logger with the specified log level and a standard output stream handler.

        The stream handler is configured only once to prevent duplicate handlers.

        :param level: The logging level to set for the logger. Defaults to DEBUG.
        :return: None.
        """
        # Set the log level for the logger.
        cls.LOGGER.setLevel(level)

        # Avoid adding duplicate handlers if any are already attached.
        if len(cls.LOGGER.handlers) > 0:
            return

        # Create and configure a stdout stream handler.
        stdout_handler = StreamHandler(stream=stdout)
        stdout_handler.setFormatter(
            fmt=Formatter(
                datefmt="%Y-%m-%d %I:%M:%S %p",
                fmt=(
                    f"%(levelcolor)s[%(name)s] {StdOutColors.DEFAULT}%(process)05d (%(thread)05d) %(levelcolor)s• "
                    f"{StdOutColors.DEFAULT}%(asctime)s %(levelcolor)s%(levelname)8s {StdOutColors.DEFAULT}%(message)s"
                ),
                defaults={
                    cls.LOG_LEVELCOLOR_KEY: cls.LOG_COLORS[NOTSET],
                },
            )
        )

        # Add the stream handler to the logger.
        cls.LOGGER.addHandler(hdlr=stdout_handler)

    @classmethod
    def build_msg(
        cls,
        msg: str,
        source: str | None = None,
        action: str | None = None,
        levelcolor: str = LOG_COLORS[NOTSET],
    ) -> str:
        """
        Build a log message string with the specified message, source, action, and levelcolor.

        :param msg: The log message.
        :param source: The source of the log message. Defaults to None.
        :param action: The action or method associated with the log. Defaults to None.
        :param levelcolor: The color associated with the log level. Defaults to NOTSET.
        :return: The formatted log message string.
        """
        return (
            f"{'[' + (source if source else 'StdOutLogger(ClassReference)') + ']'} {levelcolor}"
            f"{(action if action[-1] == ' ' else action + ' ') if action else 'Message: '}"
            f"{StdOutColors.DEFAULT}{msg % {cls.LOG_LEVELCOLOR_KEY: levelcolor}}"
        )

    @classmethod
    def critical(
        cls, msg: str, source: str | None = None, action: str | None = None, exc_info: ExcInfoType = None
    ) -> None:
        """
        Log a CRITICAL level message.

        :param msg: The message to be logged.
        :param source: The source of the log message. Defaults to None.
        :param action: The action or method associated with the log. Defaults to None.
        :param exc_info: Exception information to be logged. Defaults to None.
        :return: None.
        """
        cls.LOGGER.critical(
            msg=cls.build_msg(
                msg=msg,
                source=source,
                action=action,
                levelcolor=cls.LOG_COLORS[CRITICAL],
            ),
            extra={
                cls.LOG_LEVELCOLOR_KEY: cls.LOG_COLORS[CRITICAL],
            },
            exc_info=exc_info,
        )

    @classmethod
    def error(
        cls, msg: str, source: str | None = None, action: str | None = None, exc_info: ExcInfoType = None
    ) -> None:
        """
        Log an ERROR level message.

        :param msg: The message to be logged.
        :param source: The source of the log message. Defaults to None.
        :param action: The action or method associated with the log. Defaults to None.
        :param exc_info: Exception information to be logged. Defaults to None.
        :return: None.
        """
        cls.LOGGER.error(
            msg=cls.build_msg(
                msg=msg,
                source=source,
                action=action,
                levelcolor=cls.LOG_COLORS[ERROR],
            ),
            extra={
                cls.LOG_LEVELCOLOR_KEY: cls.LOG_COLORS[ERROR],
            },
            exc_info=exc_info,
        )

    @classmethod
    def warning(cls, msg: str, source: str | None = None, action: str | None = None) -> None:
        """
        Log a WARNING level message.

        :param msg: The message to be logged.
        :param source: The source of the log message. Defaults to None.
        :param action: The action or method associated with the log. Defaults to None.
        :return: None.
        """
        cls.LOGGER.warning(
            msg=cls.build_msg(
                msg=msg,
                source=source,
                action=action,
                levelcolor=cls.LOG_COLORS[WARNING],
            ),
            extra={
                cls.LOG_LEVELCOLOR_KEY: cls.LOG_COLORS[WARNING],
            },
        )

    @classmethod
    def info(cls, msg: str, source: str | None = None, action: str | None = None) -> None:
        """
        Log an INFO level message.

        :param msg: The message to be logged.
        :param source: The source of the log message. Defaults to None.
        :param action: The action or method associated with the log. Defaults to None.
        :return: None.
        """
        cls.LOGGER.info(
            msg=cls.build_msg(
                msg=msg,
                source=source,
                action=action,
                levelcolor=cls.LOG_COLORS[INFO],
            ),
            extra={
                cls.LOG_LEVELCOLOR_KEY: cls.LOG_COLORS[INFO],
            },
        )

    @classmethod
    def debug(cls, msg: str, source: str | None = None, action: str | None = None) -> None:
        """
        Log a DEBUG level message.

        :param msg: The message to be logged.
        :param source: The source of the log message. Defaults to None.
        :param action: The action or method associated with the log. Defaults to None.
        :return: None.
        """
        cls.LOGGER.debug(
            msg=cls.build_msg(
                msg=msg,
                source=source,
                action=action,
                levelcolor=cls.LOG_COLORS[DEBUG],
            ),
            extra={
                cls.LOG_LEVELCOLOR_KEY: cls.LOG_COLORS[DEBUG],
            },
        )


# Initialize the Pyventus logger with
# default settings and a stream handler.
StdOutLogger.config()
