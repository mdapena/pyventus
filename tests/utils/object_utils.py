from typing import Any


def get_private_attr(obj: object, name: str) -> Any:
    """
    Retrieve a private attribute from an object.

    :param obj: The object from which to retrieve the attribute.
    :param name: The name of the attribute to retrieve.
    :return: The value of the requested attribute.
    """
    # Access the private attribute using name mangling
    return getattr(obj, f"_{type(obj).__name__}{name}")


def has_private_attr(obj: object, name: str) -> bool:
    """
    Determine if an object has a private attribute.

    :param obj: The object to check for the private attribute.
    :param name: The name of the private attribute to check for.
    :return: `True` if the private attribute exists, `False` otherwise.
    """
    # Check if the object has the private attribute using name mangling
    return hasattr(obj, f"_{type(obj).__name__}{name}")
