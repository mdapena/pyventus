from collections.abc import Callable


class StdOutColors:
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

    DEFAULT_TEXT: Callable[[str], str] = lambda text: f"{StdOutColors.DEFAULT}{text}"
    PURPLE_TEXT: Callable[[str], str] = lambda text: f"{StdOutColors.PURPLE}{text}{StdOutColors.DEFAULT}"
    YELLOW_TEXT: Callable[[str], str] = lambda text: f"{StdOutColors.YELLOW}{text}{StdOutColors.DEFAULT}"
    BLUE_TEXT: Callable[[str], str] = lambda text: f"{StdOutColors.BLUE}{text}{StdOutColors.DEFAULT}"
    RED_TEXT: Callable[[str], str] = lambda text: f"{StdOutColors.RED}{text}{StdOutColors.DEFAULT}"
    CYAN_TEXT: Callable[[str], str] = lambda text: f"{StdOutColors.CYAN}{text}{StdOutColors.DEFAULT}"
    GREEN_TEXT: Callable[[str], str] = lambda text: f"{StdOutColors.GREEN}{text}{StdOutColors.DEFAULT}"
    BOLD_TEXT: Callable[[str], str] = lambda text: f"{StdOutColors.BOLD}{text}{StdOutColors.DEFAULT}"
    UNDERLINE_TEXT: Callable[[str], str] = lambda text: f"{StdOutColors.UNDERLINE}{text}{StdOutColors.DEFAULT}"
