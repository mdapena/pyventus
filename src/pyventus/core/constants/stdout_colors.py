class StdOutColors:
    """
    StdOutColors is a utility class for defining ANSI escape codes for colored text output in the console.

    This class provides ANSI escape codes for various colors and text formatting options that can be used to
    add color and style to the console output. The defined class attributes represent different color and formatting
    options such as purple, yellow, blue, red, cyan, green, bold, and underline.
    """

    DEFAULT: str = "\033[0m"
    PURPLE: str = "\033[35m"
    YELLOW: str = "\033[33m"
    BLUE: str = "\033[34m"
    RED: str = "\033[31m"
    CYAN: str = "\033[36m"
    GREEN: str = "\033[32m"
    BOLD: str = "\033[1m"
    UNDERLINE: str = "\033[4m"
