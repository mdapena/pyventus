import asyncio
from typing import Callable
from unittest.mock import patch

from _pytest.python_api import raises

from src.pyventus.core.exceptions import PyventusException
from src.pyventus.events import Event
from src.pyventus.listeners import EventListener


class TestEventListener:

    # region: Callbacks
    def callback_without_params(self):
        pass

    def callback_with_multi_params(self, *args, **kwargs):
        pass

    def callback_with_event_param(self, event: Event):
        pass

    async def callback_with_two_params(self, email: str, message: str):
        pass

    # endregion

    def test_creation_with_sync_callback(self):
        # Arrange|Act
        event_listener: EventListener = EventListener(callback=self.callback_with_event_param)

        # Assert
        assert event_listener is not None
        assert asyncio.iscoroutinefunction(event_listener.__call__)

    def test_creation_with_async_callback(self):
        # Arrange|Act
        event_listener: EventListener = EventListener(callback=self.callback_with_two_params)

        # Assert
        assert event_listener is not None
        assert asyncio.iscoroutinefunction(event_listener.__call__)

    def test_creation_with_invalid_callback(self):
        # Arrange
        def invalid_callback() -> Callable:
            pass

        # Act|Assert
        with raises(PyventusException):
            EventListener(callback=invalid_callback())

    def test_once_time_listener_flag(self):
        # Arrange|Act|Assert
        assert EventListener(callback=self.callback_with_event_param, once=True).once
        assert not EventListener(callback=self.callback_with_event_param, once=False).once

    def test_callback_with_args(self):
        with patch.object(self, 'callback_with_event_param') as mock_callback_with_event_param:
            # Arrange
            event_listener: EventListener = EventListener(callback=self.callback_with_event_param)
            event: Event = Event()

            # Act
            asyncio.run(event_listener(event))

            # Assert
            mock_callback_with_event_param.assert_called_once_with(event)

    def test_callback_with_kwargs(self):
        with patch.object(self, 'callback_with_event_param') as mock_callback_with_event_param:
            # Arrange
            event_listener: EventListener = EventListener(callback=self.callback_with_event_param)
            event: Event = Event()

            # Act
            asyncio.run(event_listener(event=event))

            # Assert
            mock_callback_with_event_param.assert_called_once_with(event=event)

    def test_callback_with_invalid_params(self):
        with raises(Exception):
            # Arrange
            event_listener: EventListener = EventListener(callback=self.callback_with_event_param)

            # Act|Assert
            asyncio.run(event_listener())

    def test_callback_with_two_params(self):
        with patch.object(self, 'callback_with_two_params') as mock_callback_with_two_params:
            # Arrange
            event_listener: EventListener = EventListener(callback=self.callback_with_two_params)
            _email: str = 'email@email.com'
            _message: str = 'Email message'

            # Act
            asyncio.run(event_listener(_email, _message))

            # Assert
            mock_callback_with_two_params.assert_called_with(_email, _message)
            assert mock_callback_with_two_params.call_count == 1

            # Act
            asyncio.run(event_listener(email=_email, message=_message))

            # Assert
            mock_callback_with_two_params.assert_called_with(email=_email, message=_message)
            assert mock_callback_with_two_params.call_count == 2

    def test_callback_with_two_invalid_params(self):
        with raises(Exception):
            # Arrange
            event_listener: EventListener = EventListener(callback=self.callback_with_two_params)

            # Act|Assert
            asyncio.run(event_listener('email@email.com', _message='Email message'))

    def test_callback_without_params(self):
        with patch.object(self, 'callback_without_params') as mock_callback_without_params:
            # Arrange
            event_listener: EventListener = EventListener(callback=self.callback_without_params)

            # Act
            asyncio.run(event_listener())

            # Assert
            mock_callback_without_params.assert_called_once_with()

    def test_callback_with_multi_params(self):
        with patch.object(self, 'callback_with_multi_params') as mock_callback_with_multi_params:
            # Arrange
            event_listener: EventListener = EventListener(callback=self.callback_with_multi_params)
            exception: Exception = Exception("Something went wrong")
            first_name: str = "John"
            last_name: str = "Browning"

            # Test with *args and **kwargs
            asyncio.run(event_listener(first_name, last_name=last_name))
            mock_callback_with_multi_params.assert_called_with(first_name, last_name=last_name)
            assert mock_callback_with_multi_params.call_count == 1

            # Test with empty arguments
            asyncio.run(event_listener())
            mock_callback_with_multi_params.assert_called_with()
            assert mock_callback_with_multi_params.call_count == 2

            # Test with *args with exceptions
            asyncio.run(event_listener(exception))
            mock_callback_with_multi_params.assert_called_with(exception)
            assert mock_callback_with_multi_params.call_count == 3

    def test_with_multiple_listener_and_one_callback(self):
        with patch.object(self, 'callback_with_event_param') as mock_callback_with_event_param:
            # Arrange
            event_listener1: EventListener = EventListener(callback=self.callback_with_event_param)
            event_listener2: EventListener = EventListener(callback=self.callback_with_event_param)
            event1: Event = Event()
            event2: Event = Event()

            # Act
            asyncio.run(event_listener1(event1))
            asyncio.run(event_listener2(event2))

            # Assert
            assert event_listener1 != event_listener2
            assert mock_callback_with_event_param.call_count == 2
