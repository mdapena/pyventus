from abc import ABC


class StdOutColors(ABC):
    """A utility class for ANSI escape codes that add color and style to console text output."""

    DEFAULT: str = "\033[0m"
    PURPLE: str = "\033[35m"
    YELLOW: str = "\033[33m"
    BLUE: str = "\033[34m"
    RED: str = "\033[31m"
    CYAN: str = "\033[36m"
    GREEN: str = "\033[32m"
    BOLD: str = "\033[1m"
    UNDERLINE: str = "\033[4m"
