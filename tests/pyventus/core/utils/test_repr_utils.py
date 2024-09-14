from pyventus.core.utils import attributes_repr, formatted_repr


class TestReprUtils:
    # =================================
    # Test Cases for formatted_repr
    # =================================

    def test_formatted_repr(self) -> None:
        # Arrange
        class Inner: ...

        inner = Inner()
        expected: str = f"<{Inner.__name__} at 0x{id(inner):016X}>"

        # Act
        res = formatted_repr(inner)

        # Assert
        assert res == expected

    # =================================
    # Test Cases for attributes_repr
    # =================================

    def test_attributes_repr(self) -> None:
        # Arrange
        expected: str = "attr1='val1', attr2=b'val2', attr3=None"

        # Act
        res = attributes_repr(attr1="val1", attr2=b"val2", attr3=None)

        # Assert
        assert res == expected
