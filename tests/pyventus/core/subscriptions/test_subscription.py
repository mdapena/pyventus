from pickle import dumps, loads
from typing import Any

import pytest
from pyventus import PyventusException
from pyventus.core.subscriptions.subscription import Subscription

from ....fixtures import CallableMock
from ....utils import get_private_attr


class TestSubscription:
    # =================================
    # Test Cases for creation
    # =================================

    def test_creation_with_valid_input(self) -> None:
        # Arrange/Act
        subscription = Subscription(teardown_callback=lambda s: True)

        # Assert
        assert subscription is not None
        assert isinstance(subscription, Subscription)
        assert subscription.timestamp is get_private_attr(subscription, "__timestamp")

    # =================================

    @pytest.mark.parametrize(
        ["teardown_callback", "exception"],
        [
            (None, PyventusException),
            (True, PyventusException),
            (object, PyventusException),
            (object(), PyventusException),
        ],
    )
    def test_creation_with_invalid_input(self, teardown_callback: Any, exception: type[Exception]) -> None:
        # Arrange/Act/Assert
        with pytest.raises(exception):
            Subscription(teardown_callback=teardown_callback)

    # =================================
    # Test Cases for unsubscribe
    # =================================

    def test_unsubscribe_execution(self) -> None:
        # Arrange
        teardown_callback = CallableMock.Sync(return_value=True)
        subscription = Subscription(teardown_callback=teardown_callback)

        # Act
        subscription.unsubscribe()

        # Assert
        assert teardown_callback.call_count == 1
        assert teardown_callback.last_args == (subscription,)

    # =================================

    def test_unsubscribe_with_exceptions(self) -> None:
        # Arrange
        teardown_callback = CallableMock.Sync(return_value=False, raise_exception=ValueError())
        subscription = Subscription(teardown_callback=teardown_callback)

        # Act
        with pytest.raises(ValueError):
            subscription.unsubscribe()

        # Assert
        assert teardown_callback.call_count == 1
        assert teardown_callback.last_args == (subscription,)

    # =================================

    @pytest.mark.parametrize(
        ["expected"],
        [(True,), (False,)],
    )
    def test_unsubscribe_return_value(self, expected: bool) -> None:
        # Arrange
        teardown_callback = CallableMock.Sync(return_value=expected)
        subscription = Subscription(teardown_callback=teardown_callback)

        # Act
        return_value = subscription.unsubscribe()

        # Assert
        assert teardown_callback.call_count == 1
        assert teardown_callback.last_args == (subscription,)
        assert return_value is expected

    # =================================
    # Test Cases for Serialization/Deserialization
    # =================================

    def test_pickle_serialization_and_deserialization(self) -> None:
        # Arrange
        teardown_callback = CallableMock.Sync(return_value=False)
        subscription = Subscription(teardown_callback=teardown_callback)

        # Act
        data = dumps(subscription)
        restored = loads(data)

        # Assert
        for attr in Subscription.__slots__:
            attr_name: str = f"_{type(restored).__name__}{attr}" if attr.startswith("__") else attr
            assert hasattr(restored, attr_name)
