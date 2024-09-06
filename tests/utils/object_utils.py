from typing import Any


def get_private_attr(obj: object, name: str) -> Any:
    """
    Retrieve a private attribute from an object.

    This function allows access to private attributes (those prefixed with '__')
    of a given object. It raises a ValueError if the object is None or if the
    attribute name is empty. If the attribute name does not start with '__',
    it retrieves the attribute directly.

    :param obj: The object from which to retrieve the attribute.
    :param name: The name of the attribute to retrieve.
    :return: The value of the requested attribute.
    :raises ValueError: If the object is None or the attribute name is empty.
    """

    if obj is None:
        raise ValueError("Object cannot be None.")

    if not name:
        raise ValueError("Attribute name cannot be empty.")

    # Directly return the attribute if it does not start with '__'
    if not name.startswith("__"):
        return getattr(obj, name)

    # If the name ends with '__', it is likely a special method or attribute
    if name.endswith("__"):
        return getattr(obj, name)

    # Access the private attribute using name mangling
    return getattr(obj, f"_{type(obj).__name__}{name}")
