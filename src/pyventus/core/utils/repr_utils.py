from typing import Any


def formatted_repr(instance: object, info: str | None = None) -> str:
    """
    Generate a formatted string representation of an object instance.

    This function provides a consistent format for representing an object, including
    its class name, memory address, and any additional context. It is designed to help
    standardize the output of `__repr__` methods across different classes, making it
    easier to identify and debug object instances.

    :param instance: The object to be represented. It should be an instance of any class.
    :param info: Optional string providing extra information about the object. Defaults to `None`.
    :return: A formatted string representation of the object, structured as:
        "<`ClassName` object at `MemoryAddress` with (`Info`)>".
    """
    return f"<{instance.__class__.__name__} at 0x{id(instance):016X}{f' with {info}' if info else ''}>"


def attributes_repr(**kwargs: Any) -> str:
    """
    Create a formatted string representation of specified attributes.

    :param kwargs: Keyword arguments representing attribute names and their corresponding values.
    :return: A string formatted as "key1=value1, key2=value2, ..." that provides a concise
        overview of the attributes.
    """
    return ", ".join(f"{key}={value!r}" for key, value in kwargs.items())
