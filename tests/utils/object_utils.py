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
