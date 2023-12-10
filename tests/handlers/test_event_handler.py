import asyncio
from typing import Callable, Any, List, Dict
from unittest.mock import patch

from _pytest.python_api import raises

from src.pyventus.core.exceptions import PyventusException
from src.pyventus.events import Event
from src.pyventus.handlers import EventHandler
from tests import CallbackFixtures


class TestEventHandler:

    def test_creation_with_invalid_callbacks(self):
        # Arrange
        def invalid_callback() -> Callable:
            return 1  # type: ignore

        # Act|Assert
        with raises(PyventusException):
            EventHandler(event_callback=invalid_callback())

        # Act|Assert
        with raises(PyventusException):
            EventHandler(event_callback=lambda x: x, success_callback=invalid_callback())

        # Act|Assert
        with raises(PyventusException):
            EventHandler(event_callback=lambda x: x, failure_callback=invalid_callback())

    def test_once_time_listener_flag(self):
        # Arrange|Act|Assert
        assert EventHandler(event_callback=lambda x: x, once=True).once
        assert not EventHandler(event_callback=lambda x: x, once=False).once

    def test_creation_with_sync_callback(self):
        # Arrange
        sync_callback = CallbackFixtures.Sync()

        # Act
        event_handler = EventHandler(event_callback=sync_callback)
        asyncio.run(event_handler())

        # Assert
        assert event_handler is not None
        assert sync_callback.call_count == 1

    def test_creation_with_async_callback(self):
        # Arrange
        async_callback = CallbackFixtures.Async()

        # Act
        event_handler = EventHandler(event_callback=async_callback)
        asyncio.run(event_handler())

        # Assert
        assert event_handler is not None
        assert async_callback.call_count == 1

    def test_event_callback_execution(self):
        # Arrange
        int_param = 2
        str_param = 'param1'
        event_param = Event()
        list_param = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        dict_param = {'key1': 'value1'}

        event_callback = CallbackFixtures.Sync()
        event_handler = EventHandler(event_callback=event_callback)

        # Act
        asyncio.run(event_handler())

        # Assert
        assert event_callback.call_count == 1
        assert not event_callback.args
        assert not event_callback.kwargs

        # Act
        asyncio.run(event_handler(int_param, event_param, dict_param, param4=str_param, param5=list_param))

        # Assert
        assert event_callback.call_count == 2
        assert event_callback.args == (int_param, event_param, dict_param)
        assert event_callback.kwargs == {'param4': str_param, 'param5': list_param}

    def test_success_callback_execution(self):
        # Arrange
        return_value = ['string', 2, 2.3, object(), ('str', {'key': 'value'})]
        event_callback = CallbackFixtures.Async(return_value=return_value)
        event_callback_without_return_value = CallbackFixtures.Sync()
        success_callback = CallbackFixtures.Sync()
        failure_callback = CallbackFixtures.Async()

        # Act
        event_handler1 = EventHandler(
            event_callback=event_callback_without_return_value,
            success_callback=success_callback,
            failure_callback=failure_callback,
        )
        asyncio.run(event_handler1())

        # Assert
        assert event_handler1

        assert event_callback_without_return_value.call_count == 1
        assert not event_callback_without_return_value.args
        assert not event_callback_without_return_value.kwargs

        assert success_callback.call_count == 1
        assert not success_callback.args
        assert not success_callback.kwargs

        assert failure_callback.call_count == 0

        # Act
        event_handler2 = EventHandler(
            event_callback=event_callback,
            success_callback=success_callback,
            failure_callback=failure_callback,
        )
        asyncio.run(event_handler2())

        # Assert
        assert event_handler2

        assert event_callback.call_count == 1
        assert not event_callback.args
        assert not event_callback.kwargs

        assert success_callback.call_count == 2
        assert success_callback.args == (return_value,)
        assert not success_callback.kwargs

        assert failure_callback.call_count == 0

    def test_failure_callback_execution(self):
        # Arrange
        value_error = ValueError('Something went wrong!')
        event_callback = CallbackFixtures.Async(raise_exception=value_error)
        success_callback = CallbackFixtures.Sync()
        failure_callback = CallbackFixtures.Async()

        # Act
        event_handler1 = EventHandler(
            event_callback=event_callback,
            success_callback=success_callback,
        )
        asyncio.run(event_handler1())

        # Assert
        assert event_handler1

        assert event_callback.call_count == 1
        assert not event_callback.args
        assert not event_callback.kwargs

        assert success_callback.call_count == 0
        assert failure_callback.call_count == 0

        # Act
        event_handler2 = EventHandler(
            event_callback=event_callback,
            success_callback=success_callback,
            failure_callback=failure_callback,
        )
        asyncio.run(event_handler2())

        # Assert
        assert event_handler2

        assert event_callback.call_count == 2
        assert not event_callback.args
        assert not event_callback.kwargs

        assert success_callback.call_count == 0

        assert failure_callback.call_count == 1
        assert failure_callback.args == (value_error,)
        assert not failure_callback.kwargs

    def test_callback_with_invalid_params(self):
        def callback_without_params():
            pass

        # Arrange
        failure_callback = CallbackFixtures.Async()
        event_handler = EventHandler(
            event_callback=callback_without_params,
            failure_callback=failure_callback,
        )

        # Act
        asyncio.run(event_handler('String!'))

        # Assert
        assert failure_callback.call_count == 1

    def test_multiple_listener_with_one_callback(self):
        # Arrange
        event_callback = CallbackFixtures.Sync()
        event_handler1 = EventHandler(event_callback=event_callback)
        event_handler2 = EventHandler(event_callback=event_callback)

        # Act
        asyncio.run(event_handler1())
        asyncio.run(event_handler2())

        # Assert
        assert event_handler1 != event_handler2
        assert event_callback.call_count == 2
