from typing import List


class PyventusException(Exception):
    """
    Custom exception class for the Pyventus package.

    This class inherits from the base Exception class in Python, allowing it to be raised as an exception
    when needed. It serves as a specific exception type for the Pyventus package, providing a way to handle
    and identify exceptions that occur within the package.
    """

    def __init__(self, errors: str | List[str] | None = None):
        """
        Initializes a new `PyventusException` instance.
        :param errors: The error messages associated with the exception. Defaults to None.
        """
        self.errors: str | List[str] = errors if errors else self.__class__.__name__
        super().__init__(errors)
