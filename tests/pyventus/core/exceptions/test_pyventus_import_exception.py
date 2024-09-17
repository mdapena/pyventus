import pytest
from pyventus import PyventusImportException


class TestPyventusImportException:
    # =================================
    # Test Cases for creation
    # =================================

    @pytest.mark.parametrize(
        ["import_name", "is_optional", "is_dependency"],
        [
            ("pyventus", False, False),
            ("pyventus", True, False),
            ("pyventus", False, True),
            ("pyventus", True, True),
        ],
    )
    def test_creation_with_arguments(self, import_name: str, is_optional: bool, is_dependency: bool) -> None:
        # Arrange/Act
        exception = PyventusImportException(import_name, is_optional=is_optional, is_dependency=is_dependency)

        # Assert
        assert exception is not None
        assert isinstance(exception, PyventusImportException)
        assert exception.errors is not None and len(exception.errors) > 0
        assert exception.is_optional == is_optional
        assert exception.is_dependency == is_dependency

    # =================================
    # Test Cases for propagation
    # =================================

    def test_error_propagation(self) -> None:
        # Arrange/Act/Assert
        with pytest.raises(PyventusImportException):
            raise PyventusImportException("pyventus")
