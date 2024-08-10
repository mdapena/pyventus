from datetime import datetime

import pytest

from pyventus.core.exceptions.pyventus_exception import PyventusException
from pyventus.core.subscriptions.subscription import Subscription

from ...fixtures.callable_fixtures import CallableMock


class TestSubscription:

    # ==========================
    # Test Cases for creation
    # ==========================

    def test_creation_with_valid_input(self) -> None:
        # Arrange/Act
        subscription = Subscription(teardown_callback=lambda s: True)

        # Assert
        assert subscription
        assert isinstance(subscription.timestamp, datetime)

    # ==========================

    def test_creation_with_invalid_input(self) -> None:
        # Arrange, Act, Assert
        with pytest.raises(PyventusException):
            Subscription(teardown_callback=None)

    # ==========================
    # Test Cases for unsubscribe
    # ==========================

    def test_unsubscribe_execution(self) -> None:
        # Arrange
        teardown_callback = CallableMock.Sync(return_value=True)
        subscription = Subscription(teardown_callback=teardown_callback)

        # Act
        subscription.unsubscribe()

        # Assert
        assert teardown_callback.call_count == 1
        assert teardown_callback.last_args == (subscription,)

    # ==========================

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

    # ==========================

    def test_unsubscribe_return_value(self) -> None:
        # Arrange
        teardown_callback = CallableMock.Sync(return_value=True)
        subscription = Subscription(teardown_callback=teardown_callback)

        # Act
        return_value = subscription.unsubscribe()

        # Assert
        assert teardown_callback.call_count == 1
        assert teardown_callback.last_args == (subscription,)
        assert teardown_callback.return_value is return_value
