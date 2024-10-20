from typing import Generic, TypeVar

from ..utils import attributes_repr, formatted_repr

_KT = TypeVar("_KT")
"""A generic type variable that represents the keys in a MultiBidict."""

_VT = TypeVar("_VT")
"""A generic type variable that represents the values in a MultiBidict."""


class MultiBidict(Generic[_KT, _VT]):
    """
    A generic multikeyed, multivalued bidirectional dictionary.

    **Notes:**

    -   This class provides a flexible mapping structure that enables efficient
        lookups, updates, and deletions of keys and their corresponding values.

    -   Although this class uses a bidirectional mapping structure, its memory
        footprint remains minimal due to the use of references between keys and
        values instead of duplication, which limits the impact to the additional
        dictionary and set data structures.

    -   Most methods in this class operate with an average time complexity of O(1),
        ensuring high efficiency. However, the performance of removal operations
        may vary depending on the relationships between keys and values.

    -   This class is not inherently designed for concurrent access; therefore,
        thread safety considerations should be taken into account when using it
        in multithreaded environments.
    """

    # Attributes for the MultiBidict
    __slots__ = ("__fwd_dict", "__inv_dict")

    def __init__(self) -> None:
        """
        Initialize an instance of `MultiBidict`.

        This constructor sets up two dictionaries: one for storing
        the forward mapping of keys to values and another for the
        inverse mapping of values to keys. Both dictionaries are
        initialized as empty.
        """
        # Initialize the main dictionary and its inverse
        self.__fwd_dict: dict[_KT, set[_VT]] = {}
        self.__inv_dict: dict[_VT, set[_KT]] = {}

    def __repr__(self) -> str:
        """
        Retrieve a string representation of the instance.

        :return: A string representation of the instance.
        """
        return formatted_repr(
            instance=self,
            info=attributes_repr(
                fwd_dict=self.__fwd_dict,
                inv_dict=self.__inv_dict,
            ),
        )

    @property
    def is_empty(self) -> bool:
        """
        Determine whether the dictionary is empty.

        :return: `True` if the dictionary is empty, `False` otherwise.
        """
        return not self.__fwd_dict

    @property
    def keys(self) -> set[_KT]:
        """
        Retrieve all keys from the dictionary.

        :return: A set of all keys in the dictionary.
        """
        return set(self.__fwd_dict.keys())

    @property
    def values(self) -> set[_VT]:
        """
        Retrieve all values from the dictionary.

        :return: A set of all values in the dictionary.
        """
        return set(self.__inv_dict.keys())

    @property
    def key_count(self) -> int:
        """
        Retrieve the number of unique keys in the dictionary.

        :return: The total count of keys in the dictionary.
        """
        return len(self.__fwd_dict)

    @property
    def value_count(self) -> int:
        """
        Retrieve the number of unique values in the dictionary.

        :return: The total count of values in the dictionary.
        """
        return len(self.__inv_dict)

    def get_keys_from_values(self, values: set[_VT]) -> set[_KT]:
        """
        Retrieve a set of keys associated with the specified values.

        :param values: A set of values for which to retrieve the associated keys.
        :return: A set of keys associated with the given values.
            Unregistered values are ignored.
        """
        return {key for value in values for key in self.__inv_dict.get(value, [])}

    def get_values_from_keys(self, keys: set[_KT]) -> set[_VT]:
        """
        Retrieve a set of values associated with the specified keys.

        :param keys: A set of keys for which to retrieve the associated values.
        :return: A set of values associated with the given keys.
            Unregistered keys are ignored.
        """
        return {value for key in keys for value in self.__fwd_dict.get(key, [])}

    def get_key_count_from_value(self, value: _VT) -> int:
        """
        Retrieve the number of keys associated with the specified value.

        :param value: The value for which to count the associated keys.
        :return: The count of keys associated with the specified value,
            or 0 if the value is not found.
        """
        return len(self.__inv_dict[value]) if value in self.__inv_dict else 0

    def get_value_count_from_key(self, key: _KT) -> int:
        """
        Return the number of values associated with a given key.

        :param key: The key for which to count the associated values.
        :return: The count of values associated with the specified key,
            or 0 if the key is not found.
        """
        return len(self.__fwd_dict[key]) if key in self.__fwd_dict else 0

    def contains_key(self, key: _KT) -> bool:
        """
        Determine if the specified key is present in the dictionary.

        :param key: The key to be checked.
        :return: `True` if the key is found, `False` otherwise.
        """
        return key in self.__fwd_dict

    def contains_value(self, value: _VT) -> bool:
        """
        Determine if the specified value is present in the dictionary.

        :param value: The value to be checked.
        :return: `True` if the value is found, `False` otherwise.
        """
        return value in self.__inv_dict

    def are_associated(self, key: _KT, value: _VT) -> bool:
        """
        Determine whether the given key is associated with the specified value.

        :param key: The key for which the association is being checked.
        :param value: The value for which the association is being checked.
        :return: `True` if the value is associated with the key, `False` otherwise.
        """
        # Ensure that both the key and value are registered
        if key not in self.__fwd_dict or value not in self.__inv_dict:
            return False

        # Check if the value is associated with the key
        return value in self.__fwd_dict[key]

    def insert(self, key: _KT, value: _VT) -> None:
        """
        Insert the given value with the specified key into the dictionary.

        :param key: The key to which the value will be associated.
        :param value: The value to be inserted for the key.
        :return: None.
        """
        # Add the value to the key's set
        if key not in self.__fwd_dict:
            self.__fwd_dict[key] = set()
        self.__fwd_dict[key].add(value)

        # Add the key to the value's set
        if value not in self.__inv_dict:
            self.__inv_dict[value] = set()
        self.__inv_dict[value].add(key)

    def remove(self, key: _KT, value: _VT) -> None:
        """
        Remove the specified value from the given key.

        :param key: The key from which the value will be removed.
        :param value: The value to be removed from the key.
        :return: None.
        :raises KeyError: If the key or value is
            not registered or associated.
        """
        # Remove the value from the key's set
        self.__fwd_dict[key].remove(value)

        # If the key has no remaining values,
        # remove it from the dictionary
        if not self.__fwd_dict[key]:
            self.__fwd_dict.pop(key)

        # Remove the key from the value's set
        self.__inv_dict[value].remove(key)

        # If the value is no longer associated with
        # any key, remove it from the inverse dictionary
        if not self.__inv_dict[value]:
            self.__inv_dict.pop(value)

    def remove_key(self, key: _KT) -> None:
        """
        Remove the specified key from the dictionary.

        :param key: The key to be removed from the dictionary.
        :return: None.
        :raises KeyError: If the key is not registered.
        """
        # Remove the key and retrieve its associated values
        values: set[_VT] = self.__fwd_dict.pop(key)

        # Remove the key from each value's set
        for value in values:
            self.__inv_dict[value].remove(key)

            # If the value is no longer associated with any
            # keys, remove it from the inverse dictionary
            if not self.__inv_dict[value]:
                self.__inv_dict.pop(value)

    def remove_value(self, value: _VT) -> None:
        """
        Remove the specified value from the dictionary.

        :param value: The value to be removed from the dictionary.
        :return: None.
        :raises KeyError: If the value is not registered.
        """
        # Remove the value and retrieve its associated keys
        keys: set[_KT] = self.__inv_dict.pop(value)

        # Remove the value from each key's set
        for key in keys:
            self.__fwd_dict[key].remove(value)

            # If the key is no longer associated with
            # any values, remove it from the dictionary
            if not self.__fwd_dict[key]:
                self.__fwd_dict.pop(key)

    def pop_key(self, key: _KT) -> set[_VT]:
        """
        Remove the specified key from the dictionary and returns the associated values.

        :param key: The key to be removed.
        :return: A set of values associated with the removed key.
        :raises KeyError: If the key is not found in the dictionary.
        """
        # Remove the key and retrieve its associated values
        values: set[_VT] = self.__fwd_dict.pop(key)

        # Remove the key from each value's set
        for value in values:
            self.__inv_dict[value].remove(key)

            # If the value is no longer associated with any
            # keys, remove it from the inverse dictionary
            if not self.__inv_dict[value]:
                self.__inv_dict.pop(value)

        # Return the set of values
        return values

    def pop_value(self, value: _VT) -> set[_KT]:
        """
        Remove the specified value from the dictionary and returns the associated keys.

        :param value: The value to be removed.
        :return: A set of keys associated with the removed value.
        :raises KeyError: If the value is not found in the dictionary.
        """
        # Remove the value and retrieve its associated keys
        keys: set[_KT] = self.__inv_dict.pop(value)

        # Remove the value from each key's set
        for key in keys:
            self.__fwd_dict[key].remove(value)

            # If the key is no longer associated with
            # any values, remove it from the dictionary
            if not self.__fwd_dict[key]:
                self.__fwd_dict.pop(key)

        # Return the set of keys
        return keys

    def clear(self) -> None:
        """
        Clear the dictionary by removing all keys and values.

        :return: None.
        """
        self.__fwd_dict.clear()
        self.__inv_dict.clear()

    def to_dict(self) -> dict[_KT, set[_VT]]:
        """
        Retrieve a shallow copy of the dictionary.

        :return: A shallow copy of the main dictionary, where
            each key is mapped to a set of its associated values.
        """
        return {key: values.copy() for key, values in self.__fwd_dict.items()}
