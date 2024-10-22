import pytest
from pyventus import PyventusException


class TestPyventusException:
    # =================================
    # Test Cases for creation
    # =================================

    def test_creation_without_arguments(self) -> None:
        # Arrange/Act
        exception = PyventusException()

        # Assert
        assert exception is not None
        assert isinstance(exception, PyventusException)
        assert exception.errors == exception.__class__.__name__

    # =================================

    def test_creation_with_arguments(self) -> None:
        # Arrange
        errors: str | list[str] = "Test exception!"

        # Act
        exception = PyventusException(errors)

        # Assert
        assert exception is not None
        assert isinstance(exception, PyventusException)
        assert exception.errors == errors

    # =================================
    # Test Cases for propagation
    # =================================

    def test_error_propagation(self) -> None:
        # Arrange/Act/Assert
        with pytest.raises(PyventusException):
            raise PyventusException("Test exception!")
