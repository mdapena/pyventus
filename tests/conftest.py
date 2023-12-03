import pytest
from rq import Queue

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


@pytest.fixture
def rq_queue() -> Queue:
    """
    Creates and returns a RQ (Redis Queue) object for testing purposes.

    **pytest.skip**: If no Redis connection can be established.

    :return: The RQ queue object.
    """
    from fakeredis import FakeStrictRedis

    # Create a new RQ queue object
    return Queue(name='default', connection=FakeStrictRedis(), is_async=False)
