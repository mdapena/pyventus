class PyventusException(Exception):
    """
    A custom exception class for the Pyventus package.

    **Notes:**

    -   This class provides a robust mechanism for handling and identifying potential
        exceptions within the Pyventus package.

    -   This class inherits from the base `Exception` class in Python, allowing it to be
        raised as needed.
    """

    def __init__(self, errors: str | list[str] | None = None):
        """
        Initialize an instance of `PyventusException`.

        :param errors: The error messages associated with the exception. Defaults to `None`.
        """
        self.errors: str | list[str] = errors if errors else self.__class__.__name__
        super().__init__(errors)
