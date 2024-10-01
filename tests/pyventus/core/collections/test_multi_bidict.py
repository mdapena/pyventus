import pytest
from pyventus.core.collections import MultiBidict


@pytest.fixture
def empty_multibidict() -> MultiBidict[str, str]:
    """Fixture for an empty MultiBidict."""
    return MultiBidict[str, str]()


@pytest.fixture
def populated_multibidict() -> MultiBidict[str, str]:
    """
    Fixture for a MultiBidict with predefined values.

    Bidict = {
        "Apple" : {"Red", "Green"},
        "Banana": {"Yellow"},
        "Grapes": {"Purple", "Green"},
        "Lime": {"Green"},
    }
    """
    mbd = MultiBidict[str, str]()
    mbd.insert("Apple", "Red")
    mbd.insert("Apple", "Green")
    mbd.insert("Banana", "Yellow")
    mbd.insert("Grapes", "Purple")
    mbd.insert("Grapes", "Green")
    mbd.insert("Lime", "Green")
    return mbd


class TestMultiBidict:
    # ========================================
    # Test Cases for is_empty
    # ========================================

    def test_is_empty_when_no_values(self, empty_multibidict: MultiBidict[str, str]) -> None:
        # Arrange, Act, Assert
        assert empty_multibidict.is_empty is True

    # ========================================

    def test_is_empty_when_populated(self, populated_multibidict: MultiBidict[str, str]) -> None:
        # Arrange, Act, Assert
        assert populated_multibidict.is_empty is False

    # ========================================
    # Test Cases for keys
    # ========================================

    def test_keys_when_empty(self, empty_multibidict: MultiBidict[str, str]) -> None:
        # Arrange, Act, Assert
        assert empty_multibidict.keys == set()

    # ========================================

    def test_keys_when_populated(self, populated_multibidict: MultiBidict[str, str]) -> None:
        # Arrange, Act, Assert
        assert populated_multibidict.keys == {"Apple", "Banana", "Grapes", "Lime"}

    # ========================================
    # Test Cases for values
    # ========================================

    def test_values_when_empty(self, empty_multibidict: MultiBidict[str, str]) -> None:
        # Arrange, Act, Assert
        assert empty_multibidict.values == set()

    # ========================================

    def test_values_when_populated(self, populated_multibidict: MultiBidict[str, str]) -> None:
        # Arrange, Act, Assert
        assert populated_multibidict.values == {"Red", "Green", "Yellow", "Purple"}

    # ========================================
    # Test Cases for key_count
    # ========================================

    def test_key_count_when_empty(self, empty_multibidict: MultiBidict[str, str]) -> None:
        # Arrange, Act, Assert
        assert empty_multibidict.key_count == 0

    # ========================================

    def test_key_count_when_populated(self, populated_multibidict: MultiBidict[str, str]) -> None:
        # Arrange, Act, Assert
        assert populated_multibidict.key_count == 4

    # ========================================
    # Test Cases for key_count
    # ========================================

    def test_value_count_when_empty(self, empty_multibidict: MultiBidict[str, str]) -> None:
        # Arrange, Act, Assert
        assert empty_multibidict.value_count == 0

    # ========================================

    def test_value_count_when_populated(self, populated_multibidict: MultiBidict[str, str]) -> None:
        # Arrange, Act, Assert
        assert populated_multibidict.value_count == 4

    # ========================================
    # Test Cases for get_keys_from_values
    # ========================================

    def test_get_keys_from_values_when_empty(self, empty_multibidict: MultiBidict[str, str]) -> None:
        # Arrange, Act, Assert
        assert empty_multibidict.get_keys_from_values({"Any"}) == set()

    # ========================================

    @pytest.mark.parametrize(
        ["values", "expected"],
        [
            (set(), set()),
            ({"Invalid"}, set()),
            ({"Green"}, {"Apple", "Grapes", "Lime"}),
            ({"Red", "Purple"}, {"Apple", "Grapes"}),
            ({"Yellow", "Red", "Orange"}, {"Apple", "Banana"}),
        ],
    )
    def test_get_keys_from_values_when_populated(
        self, values: set[str], expected: set[str], populated_multibidict: MultiBidict[str, str]
    ) -> None:
        # Arrange, Act, Assert
        assert populated_multibidict.get_keys_from_values(values) == expected

    # ========================================
    # Test Cases for get_values_from_keys
    # =================================

    def test_get_values_from_keys_when_empty(self, empty_multibidict: MultiBidict[str, str]) -> None:
        # Arrange, Act, Assert
        assert empty_multibidict.get_values_from_keys({"Any"}) == set()

    # =================================

    @pytest.mark.parametrize(
        ["keys", "expected"],
        [
            (set(), set()),
            ({"Invalid"}, set()),
            ({"Apple"}, {"Red", "Green"}),
            ({"Apple", "Grapes"}, {"Red", "Green", "Purple"}),
            ({"Grapes", "Banana"}, {"Purple", "Green", "Yellow"}),
        ],
    )
    def test_get_values_from_keys_when_populated(
        self, keys: set[str], expected: set[str], populated_multibidict: MultiBidict[str, str]
    ) -> None:
        # Arrange, Act, Assert
        assert populated_multibidict.get_values_from_keys(keys) == expected

    # =================================
    # Test Cases for get_key_count_from_value
    # =================================

    def test_get_key_count_from_value_when_empty(self, empty_multibidict: MultiBidict[str, str]) -> None:
        assert empty_multibidict.get_key_count_from_value("Any") == 0

    # =================================

    @pytest.mark.parametrize(
        ["value", "expected"],
        [
            (None, 0),
            ("Invalid", 0),
            ("Green", 3),
            ("Purple", 1),
        ],
    )
    def test_get_key_count_from_value_when_populated(
        self, value: str, expected: int, populated_multibidict: MultiBidict[str, str]
    ) -> None:
        # Arrange, Act, Assert
        assert populated_multibidict.get_key_count_from_value(value) == expected

    # =================================
    # Test Cases for get_value_count_from_key
    # =================================

    def test_get_value_count_from_key_when_empty(self, empty_multibidict: MultiBidict[str, str]) -> None:
        # Arrange, Act, Assert
        assert empty_multibidict.get_value_count_from_key("Any") == 0

    # =================================

    @pytest.mark.parametrize(
        ["key", "expected"],
        [
            (None, 0),
            ("Invalid", 0),
            ("Grapes", 2),
            ("Banana", 1),
        ],
    )
    def test_get_value_count_from_key_when_populated(
        self, key: str, expected: int, populated_multibidict: MultiBidict[str, str]
    ) -> None:
        # Arrange, Act, Assert
        assert populated_multibidict.get_value_count_from_key(key) == expected

    # =================================
    # Test Cases for contains_key
    # =================================

    def test_contains_key_when_empty(self, empty_multibidict: MultiBidict[str, str]) -> None:
        # Arrange, Act, Assert
        assert empty_multibidict.contains_key("Any") is False

    # =================================

    @pytest.mark.parametrize(
        ["key", "expected"],
        [
            (None, False),
            ("Invalid", False),
            ("Grapes", True),
        ],
    )
    def test_contains_key_when_populated(
        self, key: str, expected: bool, populated_multibidict: MultiBidict[str, str]
    ) -> None:
        # Arrange, Act, Assert
        assert populated_multibidict.contains_key(key) is expected

    # =================================
    # Test Cases for contains_value
    # =================================

    def test_contains_value_when_empty(self, empty_multibidict: MultiBidict[str, str]) -> None:
        # Arrange, Act, Assert
        assert empty_multibidict.contains_value("Any") is False

    # =================================

    @pytest.mark.parametrize(
        ["value", "expected"],
        [
            (None, False),
            ("Invalid", False),
            ("Yellow", True),
        ],
    )
    def test_contains_value_when_populated(
        self, value: str, expected: bool, populated_multibidict: MultiBidict[str, str]
    ) -> None:
        # Arrange, Act, Assert
        assert populated_multibidict.contains_value(value) is expected

    # =================================
    # Test Cases for are_associated
    # =================================

    def test_are_associated_when_empty(self, empty_multibidict: MultiBidict[str, str]) -> None:
        # Arrange, Act, Assert
        assert empty_multibidict.are_associated("Any", "Any") is False

    # =================================

    @pytest.mark.parametrize(
        ["key", "value", "expected"],
        [
            (None, None, False),
            ("Apple", "None", False),
            ("Apple", "Apple", False),
            ("Apple", "Green", True),
            ("Grapes", "Purple", True),
            ("Banana", "Yellow", True),
            ("Grapes", "Red", False),
        ],
    )
    def test_are_associated_when_populated(
        self, key: str, value: str, expected: bool, populated_multibidict: MultiBidict[str, str]
    ) -> None:
        # Arrange, Act, Assert
        assert populated_multibidict.are_associated(key, value) is expected

    # =================================
    # Test Cases for insert
    # =================================

    def test_insert_when_empty(self, empty_multibidict: MultiBidict[str, str]) -> None:
        # Arrange/Act
        empty_multibidict.insert("Apple", "Green")
        empty_multibidict.insert("Apple", "Green")
        empty_multibidict.insert("Apple", "Green")
        empty_multibidict.insert("Apple", "Red")
        empty_multibidict.insert("Apples", "Red and Green")

        # Assert
        assert empty_multibidict.to_dict() == {"Apple": {"Green", "Red"}, "Apples": {"Red and Green"}}

    # =================================

    @pytest.mark.parametrize(
        ["key", "value", "expected_key_count", "expected_value_count"],
        [
            ("Apple", "Green", 4, 4),  # Existing pair; counts unchanged
            ("Banana", "Red", 4, 4),  # Existing key and value, new pair; counts unchanged
            ("Apple", "Blue", 4, 5),  # New value for existing key; value count increases
            ("Orange", "Green", 5, 4),  # New key with existing value; key count increases
            ("Orange", "Orange", 5, 5),  # New key and value; both counts increase
        ],
    )
    def test_insert_when_populated(
        self,
        key: str,
        value: str,
        expected_key_count: int,
        expected_value_count: int,
        populated_multibidict: MultiBidict[str, str],
    ) -> None:
        # Arrange/Act
        populated_multibidict.insert(key, value)

        # Assert
        assert populated_multibidict.are_associated(key, value)
        assert populated_multibidict.key_count == expected_key_count
        assert populated_multibidict.value_count == expected_value_count

    # =================================
    # Test Cases for remove
    # =================================

    def test_remove_when_empty(self, empty_multibidict: MultiBidict[str, str]) -> None:
        # Arrange, Act, Assert
        with pytest.raises(KeyError):
            empty_multibidict.remove("Any", "Any")

    # =================================

    @pytest.mark.parametrize(
        ["key", "value", "expected_key_count", "expected_value_count"],
        [
            ("Apple", "Green", 4, 4),  # Remove shared key and value; counts remain unchanged
            ("Grapes", "Purple", 4, 3),  # Remove shared key with a unique value; value count decreases
            ("Banana", "Yellow", 3, 3),  # Remove unique key-value pair; both counts decrease
            ("Lime", "Green", 3, 4),  # Remove unique key with a shared value; key count decreases
        ],
    )
    def test_remove_when_populated(
        self,
        key: str,
        value: str,
        expected_key_count: int,
        expected_value_count: int,
        populated_multibidict: MultiBidict[str, str],
    ) -> None:
        # Arrange/Act
        populated_multibidict.remove(key, value)

        # Assert
        assert not populated_multibidict.are_associated(key, value)
        assert populated_multibidict.key_count == expected_key_count
        assert populated_multibidict.value_count == expected_value_count

    # =================================
    # Test Cases for remove_key
    # =================================

    def test_remove_key_when_empty(self, empty_multibidict: MultiBidict[str, str]) -> None:
        # Arrange, Act, Assert
        with pytest.raises(KeyError):
            empty_multibidict.remove_key("Any")

    # =================================

    @pytest.mark.parametrize(
        ["key", "expected_key_count", "expected_value_count"],
        [
            ("Apple", 3, 3),  # Remove key with one unique value; both counts decrease
            ("Banana", 3, 3),  # Remove unique key-value pair; both counts decrease
            ("Lime", 3, 4),  # Remove unique key with a shared value; only the key count decreases
        ],
    )
    def test_remove_key_when_populated(
        self,
        key: str,
        expected_key_count: int,
        expected_value_count: int,
        populated_multibidict: MultiBidict[str, str],
    ) -> None:
        # Arrange/Act
        populated_multibidict.remove_key(key)

        # Assert
        assert populated_multibidict.key_count == expected_key_count
        assert populated_multibidict.value_count == expected_value_count

    # =================================
    # Test Cases for remove_value
    # =================================

    def test_remove_value_when_empty(self, empty_multibidict: MultiBidict[str, str]) -> None:
        # Arrange, Act, Assert
        with pytest.raises(KeyError):
            empty_multibidict.remove_value("Any")

    # =================================

    @pytest.mark.parametrize(
        ["value", "expected_key_count", "expected_value_count"],
        [
            ("Red", 4, 3),  # Remove unique value with shared key; value count decreases
            ("Green", 3, 3),  # Remove shared value with one unique key; both counts decrease
            ("Yellow", 3, 3),  # Remove unique key-value pair; both counts decrease
        ],
    )
    def test_remove_value_when_populated(
        self,
        value: str,
        expected_key_count: int,
        expected_value_count: int,
        populated_multibidict: MultiBidict[str, str],
    ) -> None:
        # Arrange/Act
        populated_multibidict.remove_value(value)

        # Assert
        assert populated_multibidict.key_count == expected_key_count
        assert populated_multibidict.value_count == expected_value_count

    # =================================
    # Test Cases for pop_key
    # =================================

    def test_pop_key_when_empty(self, empty_multibidict: MultiBidict[str, str]) -> None:
        # Arrange, Act, Assert
        with pytest.raises(KeyError):
            empty_multibidict.pop_key("Any")

    # =================================

    @pytest.mark.parametrize(
        ["key", "expected", "expected_key_count", "expected_value_count"],
        [
            ("Apple", {"Green", "Red"}, 3, 3),
            ("Banana", {"Yellow"}, 3, 3),
            ("Lime", {"Green"}, 3, 4),
        ],
    )
    def test_pop_key_when_populated(
        self,
        key: str,
        expected: set[str],
        expected_key_count: int,
        expected_value_count: int,
        populated_multibidict: MultiBidict[str, str],
    ) -> None:
        # Arrange/Act
        keys = populated_multibidict.pop_key(key)

        # Assert
        assert keys == expected
        assert populated_multibidict.key_count == expected_key_count
        assert populated_multibidict.value_count == expected_value_count

    # =================================
    # Test Cases for pop_value
    # =================================

    def test_pop_value_when_empty(self, empty_multibidict: MultiBidict[str, str]) -> None:
        # Arrange, Act, Assert
        with pytest.raises(KeyError):
            empty_multibidict.pop_value("Any")

    # =================================

    @pytest.mark.parametrize(
        ["value", "expected", "expected_key_count", "expected_value_count"],
        [
            ("Red", {"Apple"}, 4, 3),
            ("Green", {"Apple", "Grapes", "Lime"}, 3, 3),
            ("Yellow", {"Banana"}, 3, 3),
        ],
    )
    def test_pop_value_when_populated(
        self,
        value: str,
        expected: set[str],
        expected_key_count: int,
        expected_value_count: int,
        populated_multibidict: MultiBidict[str, str],
    ) -> None:
        # Arrange/Act
        values = populated_multibidict.pop_value(value)

        # Assert
        assert values == expected
        assert populated_multibidict.key_count == expected_key_count
        assert populated_multibidict.value_count == expected_value_count

    # =================================
    # Test Cases for clear
    # =================================

    def test_clear_when_empty(self, empty_multibidict: MultiBidict[str, str]) -> None:
        empty_multibidict.clear()
        assert empty_multibidict.is_empty

    # =================================

    def test_clear_when_populated(self, populated_multibidict: MultiBidict[str, str]) -> None:
        # Arrange/Act
        populated_multibidict.clear()

        # Assert
        assert populated_multibidict.is_empty

    # =================================
    # Test Cases for to_dict
    # =================================

    def test_to_dict_when_empty(self, empty_multibidict: MultiBidict[str, str]) -> None:
        assert empty_multibidict.to_dict() == {}

    # =================================

    def test_to_dict_when_populated(self, populated_multibidict: MultiBidict[str, str]) -> None:
        # Arrange, Act, Assert
        assert populated_multibidict.to_dict() == {
            "Apple": {"Red", "Green"},
            "Banana": {"Yellow"},
            "Grapes": {"Purple", "Green"},
            "Lime": {"Green"},
        }

    # =================================

    def test_to_dict_returns_shallow_copy(self) -> None:
        # Arrange
        object1 = object()
        object2 = object()
        multibidict = MultiBidict[str, object]()
        multibidict.insert("key1", object1)
        dict_copy = multibidict.to_dict()

        # Act
        dict_copy["key1"].add(object2)

        # Assert
        assert object1 in dict_copy["key1"]
        assert object2 in dict_copy["key1"]
        assert object1 in multibidict.get_values_from_keys({"key1"})
        assert object2 not in multibidict.get_values_from_keys({"key1"})
        assert dict_copy != multibidict.to_dict()
