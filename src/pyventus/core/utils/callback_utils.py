from inspect import (
    isfunction,
    isclass,
    isbuiltin,
    ismethod,
    iscoroutinefunction,
    isgeneratorfunction,
    isasyncgenfunction,
)
from typing import Callable, Any

from ..exceptions import PyventusException


def validate_callback(callback: Callable[..., Any]) -> None:
    """
    Validates whether the provided callback is a valid callable object.
    :param callback: The callback to be validated.
    :return: None
    :raises PyventusException: If the callback is not a callable object.
    """
    if not callable(callback):
        raise PyventusException(
            f"'{callback.__name__ if hasattr(callback, '__name__') else callback}' is not a callable object."
        )


def get_callback_name(callback: Callable[..., Any]) -> str:
    """
    Retrieves the name of the provided callback.
    :param callback: The callback object.
    :return: The name of the callback as a string.
    """
    if callback is not None and hasattr(callback, "__name__"):
        return callback.__name__
    elif callback is not None and hasattr(callback, "__class__"):
        return type(callback).__name__
    else:
        return "None"


def is_callback_async(callback: Callable[..., Any]) -> bool:
    """
    Checks whether the provided callback is an asynchronous function or method.
    :param callback: The callback to be checked.
    :return: `True` if the callback is an asynchronous function or method, `False` otherwise.
    """
    if ismethod(callback) or isfunction(callback) or isbuiltin(callback):
        return iscoroutinefunction(callback) or isasyncgenfunction(callback)
    elif not isclass(callback) and hasattr(callback, "__call__"):  # A callable class instance
        return iscoroutinefunction(callback.__call__) or isasyncgenfunction(callback.__call__)
    else:
        return False


def is_callback_generator(callback: Callable[..., Any]) -> bool:
    """
    Checks whether the provided callback is a generator.
    :param callback: The callback to be checked.
    :return:`True` if the callback is a generator, `False` otherwise.
    """
    if ismethod(callback) or isfunction(callback) or isbuiltin(callback):
        return isgeneratorfunction(callback) or isasyncgenfunction(callback)
    elif not isclass(callback) and hasattr(callback, "__call__"):  # A callable class instance
        return isgeneratorfunction(callback.__call__) or isasyncgenfunction(callback.__call__)
    else:
        return False
