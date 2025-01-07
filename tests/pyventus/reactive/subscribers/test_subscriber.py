from pickle import dumps, loads
from typing import Any

import pytest
from pyventus import PyventusException
from pyventus.reactive import Subscriber

from ....fixtures import CallableMock, DummyCallable
from ....utils import has_private_attr


class TestSubscriber:
    # =================================
    # Test Cases for creation
    # =================================

    @pytest.mark.parametrize(
        ["next_callback", "error_callback", "complete_callback"],
        [
            (CallableMock.Sync(), None, None),
            (None, CallableMock.Async(), None),
            (None, None, CallableMock.Async()),
            (CallableMock.Async(), None, CallableMock.Sync()),
            (CallableMock.Async(), CallableMock.Sync(), None),
            (None, CallableMock.Sync(), CallableMock.Async()),
        ],
    )
    def test_creation_with_valid_input(
        self, next_callback: CallableMock.Base, error_callback: CallableMock.Base, complete_callback: CallableMock.Base
    ) -> None:
        # Arrange/Act
        subscriber = Subscriber[Any](
            teardown_callback=lambda sub: True,
            next_callback=next_callback,
            error_callback=error_callback,
            complete_callback=complete_callback,
            force_async=False,
        )

        # Assert
        assert subscriber is not None
        assert isinstance(subscriber, Subscriber)
        assert subscriber.has_next_callback is bool(next_callback is not None)
        assert subscriber.has_error_callback is bool(error_callback is not None)
        assert subscriber.has_complete_callback is bool(complete_callback is not None)

    # =================================

    @pytest.mark.parametrize(
        ["next_callback", "error_callback", "complete_callback", "exception"],
        [
            (None, None, None, PyventusException),
            (DummyCallable.Sync.Generator.func, None, None, PyventusException),
            (None, DummyCallable.Async.Generator.func, None, PyventusException),
            (None, None, DummyCallable.Async.Generator.func, PyventusException),
        ],
    )
    def test_creation_with_invalid_input(
        self, next_callback: Any, error_callback: Any, complete_callback: Any, exception: type[Exception]
    ) -> None:
        # Arrange/Act/Assert
        with pytest.raises(exception):
            Subscriber[Any](
                teardown_callback=lambda sub: True,
                next_callback=next_callback,
                error_callback=error_callback,
                complete_callback=complete_callback,
                force_async=False,
            )

    # =================================
    # Test Cases for the Next method execution.
    # =================================

    @pytest.mark.parametrize(
        ["next_callback"],
        [
            (None,),
            (CallableMock.Sync(),),
            (CallableMock.Async(),),
        ],
    )
    async def test_next_method_execution(self, next_callback: CallableMock.Base | None) -> None:
        # Arrange
        value: Any = object()
        error_callback: CallableMock.Base = CallableMock.Sync()
        complete_callback: CallableMock.Base = CallableMock.Async()
        subscriber = Subscriber[Any](
            teardown_callback=lambda sub: True,
            next_callback=next_callback,
            error_callback=error_callback,
            complete_callback=complete_callback,
            force_async=False,
        )

        # Act
        await subscriber.next(value)

        # Assert
        if next_callback:
            assert next_callback.call_count == 1
            assert next_callback.last_args == (value,)
            assert next_callback.last_kwargs == {}
        assert error_callback.call_count == 0
        assert complete_callback.call_count == 0

    # =================================
    # Test Cases for the Error method execution.
    # =================================

    @pytest.mark.parametrize(
        ["error_callback"],
        [
            (None,),
            (CallableMock.Sync(),),
            (CallableMock.Async(),),
        ],
    )
    async def test_error_method_execution(self, error_callback: CallableMock.Base | None) -> None:
        # Arrange
        exception: Exception = ValueError()
        next_callback: CallableMock.Base = CallableMock.Async()
        complete_callback: CallableMock.Base = CallableMock.Sync()
        subscriber = Subscriber[Any](
            teardown_callback=lambda sub: True,
            next_callback=next_callback,
            error_callback=error_callback,
            complete_callback=complete_callback,
            force_async=False,
        )

        # Act
        await subscriber.error(exception)

        # Assert
        if error_callback:
            assert error_callback.call_count == 1
            assert error_callback.last_args == (exception,)
            assert error_callback.last_kwargs == {}
        assert next_callback.call_count == 0
        assert complete_callback.call_count == 0

    # =================================
    # Test Cases for the Complete method execution.
    # =================================

    @pytest.mark.parametrize(
        ["complete_callback"],
        [
            (None,),
            (CallableMock.Sync(),),
            (CallableMock.Async(),),
        ],
    )
    async def test_complete_method_execution(self, complete_callback: CallableMock.Base | None) -> None:
        # Arrange
        next_callback: CallableMock.Base = CallableMock.Async()
        error_callback: CallableMock.Base = CallableMock.Sync()
        subscriber = Subscriber[Any](
            teardown_callback=lambda sub: True,
            next_callback=next_callback,
            error_callback=error_callback,
            complete_callback=complete_callback,
            force_async=False,
        )

        # Act
        await subscriber.complete()

        # Assert
        if complete_callback:
            assert complete_callback.call_count == 1
            assert complete_callback.last_args == ()
            assert complete_callback.last_kwargs == {}
        assert next_callback.call_count == 0
        assert error_callback.call_count == 0

    # =================================
    # Test Cases for Serialization/Deserialization
    # =================================

    def test_pickle_serialization_and_deserialization(self) -> None:
        # Arrange
        subscriber = Subscriber(
            teardown_callback=CallableMock.Sync(return_value=False),
            next_callback=CallableMock.Sync(),
            error_callback=None,
            complete_callback=None,
            force_async=True,
        )

        # Act
        data = dumps(subscriber)
        restored = loads(data)

        # Assert
        for attr in Subscriber.__slots__:
            assert (
                hasattr(restored, attr)
                if not attr.startswith("__") or attr.endswith("__")
                else has_private_attr(restored, attr)
            )
