import pytest

from src.pyventus.linkers import EventLinker


@pytest.fixture
def clean_event_linker() -> bool:
    """
    Pytest fixture for cleaning up the EventLinker registry.

    This fixture removes all registered event links from the EventLinker registry
    and returns a boolean value indicating whether the cleanup was successful.
    :return: `True`, indicating that the cleanup was successful.
    """
    EventLinker.remove_all()
    return EventLinker.event_registry == {}
