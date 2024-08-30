from collections import namedtuple
from pickle import dumps, loads
from typing import Any

import pytest
from pyventus import PyventusException
from pyventus.events import EventSubscriber

from ...fixtures.callable_fixtures import CallableMock


class TestEventSubscriber:
    # =================================
    # Test Cases for creation
    # =================================

    def test_creation_with_valid_input(self) -> None:
        # Arrange/Act
        subscriber = EventSubscriber(
            teardown_callback=lambda sub: True,
            event_callback=lambda: None,
            success_callback=None,
            failure_callback=None,
            force_async=False,
            once=False,
        )

        # Assert
        assert subscriber
        assert subscriber.once is False

    # =================================

    def test_creation_with_invalid_input(self) -> None:
        # Arrange/Act/Assert
        with pytest.raises(PyventusException):
            EventSubscriber(
                teardown_callback=lambda sub: True,
                event_callback=lambda: None,
                success_callback=None,
                failure_callback=None,
                force_async=False,
                once="False",  # type: ignore[arg-type]
            )

        # Arrange/Act/Assert
        with pytest.raises(PyventusException):
            EventSubscriber(
                teardown_callback=lambda sub: True,
                event_callback=None,  # type: ignore[arg-type]
                success_callback=None,
                failure_callback=None,
                force_async=False,
                once=False,
            )

    # =================================
    # Test Cases for execution
    # =================================

    # Define a named tuple for better readability of test cases
    ExecutionTestCase = namedtuple(
        "ExecutionTestCase", ["event_callback", "success_callback", "failure_callback", "args", "kwargs"]
    )

    @pytest.mark.parametrize(
        ExecutionTestCase._fields,
        [
            # Test without success and failure callbacks
            # =================================
            ExecutionTestCase(
                event_callback=CallableMock.Random(),
                success_callback=None,
                failure_callback=None,
                args=(),
                kwargs={},
            ),
            ExecutionTestCase(
                event_callback=CallableMock.Random(),
                success_callback=None,
                failure_callback=None,
                args=("str", 0),
                kwargs={"str": ...},
            ),
            ExecutionTestCase(
                event_callback=CallableMock.Random(return_value=...),
                success_callback=None,
                failure_callback=None,
                args=(),
                kwargs={},
            ),
            ExecutionTestCase(
                event_callback=CallableMock.Random(return_value=[0, 1]),
                success_callback=None,
                failure_callback=None,
                args=("str", 0),
                kwargs={"str": ...},
            ),
            ExecutionTestCase(
                event_callback=CallableMock.Random(raise_exception=KeyError()),
                success_callback=None,
                failure_callback=None,
                args=(),
                kwargs={},
            ),
            ExecutionTestCase(
                event_callback=CallableMock.Random(raise_exception=ValueError()),
                success_callback=None,
                failure_callback=None,
                args=("str", 0),
                kwargs={"str": ...},
            ),
            ExecutionTestCase(
                event_callback=CallableMock.Random(return_value=..., raise_exception=KeyError()),
                success_callback=None,
                failure_callback=None,
                args=(),
                kwargs={},
            ),
            ExecutionTestCase(
                event_callback=CallableMock.Random(return_value=[0, 1], raise_exception=ValueError()),
                success_callback=None,
                failure_callback=None,
                args=("str", 0),
                kwargs={"str": ...},
            ),
            # Testing with event and success callbacks
            # =================================
            ExecutionTestCase(
                event_callback=CallableMock.Random(),
                success_callback=CallableMock.Random(),
                failure_callback=None,
                args=(),
                kwargs={},
            ),
            ExecutionTestCase(
                event_callback=CallableMock.Random(),
                success_callback=CallableMock.Random(),
                failure_callback=None,
                args=("str", 0),
                kwargs={"str": ...},
            ),
            ExecutionTestCase(
                event_callback=CallableMock.Random(return_value=...),
                success_callback=CallableMock.Random(),
                failure_callback=None,
                args=(),
                kwargs={},
            ),
            ExecutionTestCase(
                event_callback=CallableMock.Random(return_value=[0, 1]),
                success_callback=CallableMock.Random(),
                failure_callback=None,
                args=("str", 0),
                kwargs={"str": ...},
            ),
            ExecutionTestCase(
                event_callback=CallableMock.Random(raise_exception=KeyError()),
                success_callback=CallableMock.Random(),
                failure_callback=None,
                args=(),
                kwargs={},
            ),
            ExecutionTestCase(
                event_callback=CallableMock.Random(raise_exception=ValueError()),
                success_callback=CallableMock.Random(),
                failure_callback=None,
                args=("str", 0),
                kwargs={"str": ...},
            ),
            ExecutionTestCase(
                event_callback=CallableMock.Random(return_value=..., raise_exception=KeyError()),
                success_callback=CallableMock.Random(),
                failure_callback=None,
                args=(),
                kwargs={},
            ),
            ExecutionTestCase(
                event_callback=CallableMock.Random(return_value=[0, 1], raise_exception=ValueError()),
                success_callback=CallableMock.Random(),
                failure_callback=None,
                args=("str", 0),
                kwargs={"str": ...},
            ),
            ExecutionTestCase(  # Test with event and failure callbacks
                event_callback=CallableMock.Random(),
                success_callback=None,
                failure_callback=CallableMock.Random(),
                args=(),
                kwargs={},
            ),
            ExecutionTestCase(
                event_callback=CallableMock.Random(),
                success_callback=None,
                failure_callback=CallableMock.Random(),
                args=("str", 0),
                kwargs={"str": ...},
            ),
            ExecutionTestCase(
                event_callback=CallableMock.Random(return_value=...),
                success_callback=None,
                failure_callback=CallableMock.Random(),
                args=(),
                kwargs={},
            ),
            ExecutionTestCase(
                event_callback=CallableMock.Random(return_value=[0, 1]),
                success_callback=None,
                failure_callback=CallableMock.Random(),
                args=("str", 0),
                kwargs={"str": ...},
            ),
            ExecutionTestCase(
                event_callback=CallableMock.Random(raise_exception=KeyError()),
                success_callback=None,
                failure_callback=CallableMock.Random(),
                args=(),
                kwargs={},
            ),
            ExecutionTestCase(
                event_callback=CallableMock.Random(raise_exception=ValueError()),
                success_callback=None,
                failure_callback=CallableMock.Random(),
                args=("str", 0),
                kwargs={"str": ...},
            ),
            ExecutionTestCase(
                event_callback=CallableMock.Random(return_value=..., raise_exception=KeyError()),
                success_callback=None,
                failure_callback=CallableMock.Random(),
                args=(),
                kwargs={},
            ),
            ExecutionTestCase(
                event_callback=CallableMock.Random(return_value=[0, 1], raise_exception=ValueError()),
                success_callback=None,
                failure_callback=CallableMock.Random(),
                args=("str", 0),
                kwargs={"str": ...},
            ),
            # Test with event, success and failure callbacks
            # =================================
            ExecutionTestCase(
                event_callback=CallableMock.Random(),
                success_callback=CallableMock.Random(),
                failure_callback=CallableMock.Random(),
                args=(),
                kwargs={},
            ),
            ExecutionTestCase(
                event_callback=CallableMock.Random(),
                success_callback=CallableMock.Random(),
                failure_callback=CallableMock.Random(),
                args=("str", 0),
                kwargs={"str": ...},
            ),
            ExecutionTestCase(
                event_callback=CallableMock.Random(return_value=...),
                success_callback=CallableMock.Random(),
                failure_callback=CallableMock.Random(),
                args=(),
                kwargs={},
            ),
            ExecutionTestCase(
                event_callback=CallableMock.Random(return_value=[0, 1]),
                success_callback=CallableMock.Random(),
                failure_callback=CallableMock.Random(),
                args=("str", 0),
                kwargs={"str": ...},
            ),
            ExecutionTestCase(
                event_callback=CallableMock.Random(raise_exception=KeyError()),
                success_callback=CallableMock.Random(),
                failure_callback=CallableMock.Random(),
                args=(),
                kwargs={},
            ),
            ExecutionTestCase(
                event_callback=CallableMock.Random(raise_exception=ValueError()),
                success_callback=CallableMock.Random(),
                failure_callback=CallableMock.Random(),
                args=("str", 0),
                kwargs={"str": ...},
            ),
            ExecutionTestCase(
                event_callback=CallableMock.Random(return_value=..., raise_exception=KeyError()),
                success_callback=CallableMock.Random(),
                failure_callback=CallableMock.Random(),
                args=(),
                kwargs={},
            ),
            ExecutionTestCase(
                event_callback=CallableMock.Random(return_value=[0, 1], raise_exception=ValueError()),
                success_callback=CallableMock.Random(),
                failure_callback=CallableMock.Random(),
                args=("str", 0),
                kwargs={"str": ...},
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_execution(
        self,
        event_callback: CallableMock.Base,
        success_callback: CallableMock.Base,
        failure_callback: CallableMock.Base,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> None:
        # Arrange: Create an EventSubscriber instance with the provided callbacks
        subscriber = EventSubscriber(
            teardown_callback=lambda sub: True,
            event_callback=event_callback,
            success_callback=success_callback,
            failure_callback=failure_callback,
            force_async=False,
            once=False,
        )

        # Act: Execute the subscriber with the provided arguments and keyword arguments
        await subscriber.execute(*args, **kwargs)

        # Assert: Verify that the event callback was called exactly once
        assert event_callback.call_count == 1
        assert event_callback.last_args == args
        assert event_callback.last_kwargs == kwargs

        # Check the behavior based on whether the event callback raised an exception
        if event_callback.exception is None:
            # If no exception, check success callback behavior
            if success_callback:
                assert success_callback.call_count == 1
                assert success_callback.last_kwargs == {}
                assert success_callback.last_args == (
                    (event_callback.return_value,) if event_callback.return_value else ()
                )

            # Failure callback should not be called
            if failure_callback:
                assert failure_callback.call_count == 0
        else:
            # If an exception was raised, check failure callback behavior
            if failure_callback:
                assert failure_callback.call_count == 1
                assert failure_callback.last_kwargs == {}
                assert failure_callback.last_args == (event_callback.exception,)

            # Success callback should not be called
            if success_callback:
                assert success_callback.call_count == 0

    # =================================

    @pytest.mark.asyncio
    async def test_execution_when_success_callback_raises_exception(self) -> None:
        # Arrange
        subscriber = EventSubscriber(
            teardown_callback=lambda sub: True,
            event_callback=CallableMock.Random(return_value="str"),
            success_callback=CallableMock.Random(raise_exception=ValueError()),
            failure_callback=CallableMock.Random(),
            force_async=False,
            once=False,
        )

        # Act/Assert
        with pytest.raises(ValueError):
            await subscriber.execute()

    # =================================

    @pytest.mark.asyncio
    async def test_execution_when_failure_callback_raises_exception(self) -> None:
        # Arrange
        subscriber = EventSubscriber(
            teardown_callback=lambda sub: True,
            event_callback=CallableMock.Random(raise_exception=KeyError()),
            success_callback=CallableMock.Random(),
            failure_callback=CallableMock.Random(raise_exception=ValueError()),
            force_async=False,
            once=False,
        )

        # Act/Assert
        with pytest.raises(ValueError):
            await subscriber.execute()

    # =================================

    def test_pickle_serialization(self) -> None:
        # Arrange
        teardown_callback = CallableMock.Sync(return_value=False)
        event_callback = CallableMock.Random()
        subscriber = EventSubscriber(
            teardown_callback=teardown_callback,
            event_callback=event_callback,
            success_callback=None,
            failure_callback=None,
            force_async=True,
            once=True,
        )

        # Act
        data = dumps(subscriber)
        restored = loads(data)

        # Assert
        for attr in EventSubscriber.__slots__:
            attr_name: str = f"_{type(restored).__name__}{attr}" if attr.startswith("__") else attr
            assert hasattr(restored, attr_name)
