from typing import List


class PyeelibException(Exception):
    """
    Custom exception class for the Pyeelib library.

    This class inherits from the base Exception class in Python, allowing it to be raised as an exception
    when needed. It serves as a specific exception type for the Pyeelib library, providing a way to handle
    and identify exceptions that occur within the library.
    """

    def __init__(self, errors: str | List[str] = None):
        """
        Initializes a new `PyeelibException` instance.
        :param errors: The error messages associated with the exception. Defaults to None.
        """
        self.errors: str | List[str] = errors if errors else self.__class__.__name__
        super().__init__(errors)
