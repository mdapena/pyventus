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

from ...core.constants import StdOutColors


class StdOutLogger:
    """A simple logging interface for writing log messages to standard output."""

    LOGGER: Logger = getLogger(name="Pyventus")
    """The logger instance for the Pyventus library."""

    LOG_LEVELCOLOR_KEY: str = "levelcolor"
    """The key used to store the color associated with the log level in the log records' extra attributes."""

    LOG_COLORS: dict[int, str] = {
        NOTSET: StdOutColors.DEFAULT,
        INFO: StdOutColors.GREEN,
        DEBUG: StdOutColors.PURPLE,
        WARNING: StdOutColors.YELLOW,
        ERROR: StdOutColors.RED,
        CRITICAL: StdOutColors.RED,
    }
    """A mapping of log levels to their corresponding color codes for console output."""

    @classmethod
    def config(cls, level: int = DEBUG) -> None:
        """
        Configure the logger with the specified log level.

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
        Build a log message string with the specified log level, message, source, and action.

        :param msg: The log message.
        :param source: The source of the log message. Defaults to None.
        :param action: The action or method associated with the log. Defaults to None.
        :param levelcolor: The color associated with the log level. Defaults to NOTSET.
        :return: The formatted log message string.
        """
        # Build the log message string.
        return (
            f"{'[' + (source if source else 'StdOutLogger(ClassReference)') + ']'} {levelcolor}"
            f"{(action if action[-1] == ' ' else action + ' ') if action else 'Message: '}"
            f"{StdOutColors.DEFAULT}{msg}"
        )

    @classmethod
    def critical(
        cls,
        msg: str,
        source: str | None = None,
        action: str | None = None,
    ) -> None:
        """
        Log a CRITICAL level message.

        :param msg: The message to be logged.
        :param source: The source of the log message. Defaults to None.
        :param action: The action or method associated with the log. Defaults to None.
        :return: None.
        """
        cls.LOGGER.error(
            msg=cls.build_msg(
                msg=msg,
                source=source,
                action=action,
                levelcolor=cls.LOG_COLORS[CRITICAL],
            ),
            extra={
                cls.LOG_LEVELCOLOR_KEY: cls.LOG_COLORS[CRITICAL],
            },
        )

    @classmethod
    def error(
        cls,
        msg: str,
        source: str | None = None,
        action: str | None = None,
    ) -> None:
        """
        Log an ERROR level message.

        :param msg: The message to be logged.
        :param source: The source of the log message. Defaults to None.
        :param action: The action or method associated with the log. Defaults to None.
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
