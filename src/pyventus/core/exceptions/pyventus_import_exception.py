from .pyventus_exception import PyventusException


class PyventusImportException(PyventusException):
    """
    A custom Pyventus exception for handling missing imports within the package.

    **Notes:**

    -   This class provides a robust mechanism for handling and identifying potential
        import exceptions within the Pyventus package.

    -   This class inherits from the base `PyventusException` class, allowing it to be
        raised as needed.
    """

    def __init__(self, import_name: str, *, is_optional: bool = False, is_dependency: bool = False) -> None:
        """
        Initialize an instance of `PyventusImportException`.

        :param import_name: The name of the missing import.
        :param is_optional: A flag indicating whether the missing import is optional
            or required for the package to work. Defaults to `False` (required).
        :param is_dependency: A flag indicating whether the missing import is an
            external dependency or not. Defaults to `False` (local import).
        """
        # Store the import name and properties.
        self.import_name: str = import_name
        self.is_optional: bool = is_optional
        self.is_dependency: bool = is_dependency

        # Initialize the base PyventusException class with the error message.
        super().__init__(
            f"Missing {'optional ' if is_optional else ''}{'dependency' if is_dependency else 'import'}: {import_name}",
        )
