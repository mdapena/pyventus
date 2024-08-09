from asyncio import get_running_loop


def is_loop_running() -> bool:
    """
    Determines whether there is currently an active asyncio event loop.
    :return: `True` if an event loop is running, `False` otherwise.
    """
    try:
        get_running_loop()
        return True
    except RuntimeError:
        return False
