import asyncio
from dataclasses import dataclass
from unittest.mock import patch

import pytest
from _pytest.python_api import raises

from src.pyventus.core.exceptions import PyventusException
from src.pyventus.emitters.asyncio import AsyncioEventEmitter
from src.pyventus.events import Event
from src.pyventus.linkers import EventLinker


# region: Custom Events
@dataclass(frozen=True)
class EmailEvent(Event):
    email: str
    message: str


class TestAsyncioEmitter:

    # region: Callbacks
    def callback_without_params(self):
        pass

    async def callback_with_params(self, email: str, message: str):
        pass

    def callback_with_event_params(self, event: EmailEvent):
        pass

    async def callback_with_exception_params(self, exception: Exception):
        pass

    def callback_with_args_params(self, *args):
        pass

    async def callback_with_kwargs_params(self, **kwargs):
        pass

    async def callback_with_multi_params(self, *args, **kwargs):
        pass

    def callback_that_raise_exception(self):
        raise PyventusException("Sync callback with exceptions")

    # endregion

    def test_creation(self, clean_event_linker: bool):
        event_emitter = AsyncioEventEmitter()
        assert event_emitter is not None

    def test_creation_with_invalid_params(self, clean_event_linker: bool):
        with raises(PyventusException):
            AsyncioEventEmitter(event_linker=None)

    @pytest.mark.asyncio
    async def test_emit_exception_raised(self, clean_event_linker):
        # Arrange
        event_emitter = AsyncioEventEmitter()

        # Act and Assert
        with raises(PyventusException):
            event_emitter.emit(None)
        with raises(PyventusException):
            event_emitter.emit(Event)
        with raises(PyventusException):
            event_emitter.emit(Exception)

        # Arrange
        with patch.object(self, 'callback_with_exception_params') as callback_with_exception_params:
            EventLinker.subscribe('RaiseException', callback=self.callback_that_raise_exception)
            EventLinker.subscribe(Exception, callback=self.callback_with_exception_params, once=True)

            # Act
            event_emitter.emit('RaiseException')
            event_emitter.emit('RaiseException')
            event_emitter.emit('RaiseException')

            while event_emitter.background_futures:  # Wait for all futures to complete
                await asyncio.gather(*event_emitter.background_futures, return_exceptions=True)

            # Assert
            callback_with_exception_params.assert_called_once()

    @pytest.mark.asyncio
    async def test_emit_with_event_subscribers(self, clean_event_linker):
        # Arrange
        event_emitter = AsyncioEventEmitter()
        with patch.object(self, 'callback_without_params') as callback_without_params:
            event_listener_1 = EventLinker.subscribe(Event, callback=self.callback_without_params, once=True)
            event_listener_2 = EventLinker.subscribe('Empty', Event, callback=self.callback_without_params)
            event_listener_3 = EventLinker.subscribe('Empty', callback=self.callback_without_params)

            # Act
            event_emitter.emit(Event())
            while event_emitter.background_futures:  # Wait for all futures to complete
                await asyncio.gather(*event_emitter.background_futures, return_exceptions=True)

            # Assert
            assert callback_without_params.call_count == 2
            assert len(EventLinker.get_events_by_listener(event_listener=event_listener_1)) == 0
            assert len(EventLinker.get_events_by_listener(event_listener=event_listener_2)) == 2
            assert len(EventLinker.get_events_by_listener(event_listener=event_listener_3)) == 1

            # Act
            event_emitter.emit('Empty')

            # Wait for all futures to complete
            while event_emitter.background_futures:
                await asyncio.gather(*event_emitter.background_futures, return_exceptions=True)

            # Assert
            assert callback_without_params.call_count == 4

    @pytest.mark.asyncio
    async def test_emit_without_params(self, clean_event_linker):
        # Arrange
        event_emitter = AsyncioEventEmitter()
        with patch.object(self, 'callback_without_params') as callback_without_params:
            EventLinker.subscribe('Event1', callback=self.callback_without_params)

            # Act
            event_emitter.emit('Event1')
            while event_emitter.background_futures:  # Wait for all futures to complete
                await asyncio.gather(*event_emitter.background_futures, return_exceptions=True)

            # Assert
            callback_without_params.assert_called_once_with()

    @pytest.mark.asyncio
    async def test_emit_with_event_params(self, clean_event_linker):
        # Arrange
        event_emitter = AsyncioEventEmitter()
        with patch.object(self, 'callback_with_event_params') as callback_with_event_params:
            EventLinker.subscribe(EmailEvent, callback=self.callback_with_event_params)
            event_1 = EmailEvent(email="email@email.com", message="Email message!")

            # Act
            event_emitter.emit(event_1)
            while event_emitter.background_futures:  # Wait for all futures to complete
                await asyncio.gather(*event_emitter.background_futures, return_exceptions=True)

            # Assert
            callback_with_event_params.assert_called_with(event_1)
            assert callback_with_event_params.call_count == 1

            # Act
            event_emitter.emit('EmailEvent', event_1)
            while event_emitter.background_futures:  # Wait for all futures to complete
                await asyncio.gather(*event_emitter.background_futures, return_exceptions=True)

            # Assert
            callback_with_event_params.assert_called_with(event_1)
            assert callback_with_event_params.call_count == 2

    @pytest.mark.asyncio
    async def test_emit_with_exception_params(self, clean_event_linker):
        # Arrange
        event_emitter = AsyncioEventEmitter()
        with patch.object(self, 'callback_with_exception_params') as callback_with_exception_params:
            EventLinker.subscribe(ValueError, callback=self.callback_with_exception_params)
            exception = ValueError("Something went wrong!")

            # Act
            event_emitter.emit(exception)
            while event_emitter.background_futures:  # Wait for all futures to complete
                await asyncio.gather(*event_emitter.background_futures, return_exceptions=True)

            # Assert
            callback_with_exception_params.assert_called_with(exception)
            assert callback_with_exception_params.call_count == 1

            # Act
            event_emitter.emit('ValueError', exception)
            while event_emitter.background_futures:  # Wait for all futures to complete
                await asyncio.gather(*event_emitter.background_futures, return_exceptions=True)

            # Assert
            callback_with_exception_params.assert_called_with(exception)
            assert callback_with_exception_params.call_count == 2

    @pytest.mark.asyncio
    async def test_emit_with_args_params(self, clean_event_linker):
        # Arrange
        event_emitter = AsyncioEventEmitter()
        with patch.object(self, 'callback_with_args_params') as sync_callback_with_args_params:
            EventLinker.subscribe('Event4', callback=self.callback_with_args_params)
            event = EmailEvent(email="email@email.com", message="Email message!")
            text = "Another param"

            # Act
            event_emitter.emit('Event4', event, text)
            while event_emitter.background_futures:  # Wait for all futures to complete
                await asyncio.gather(*event_emitter.background_futures, return_exceptions=True)

            # Assert
            sync_callback_with_args_params.assert_called_with(event, text)
            assert sync_callback_with_args_params.call_count == 1

    @pytest.mark.asyncio
    async def test_emit_with_kwargs_params(self, clean_event_linker):
        # Arrange
        event_emitter = AsyncioEventEmitter()
        with patch.object(self, 'callback_with_kwargs_params') as callback_with_kwargs_params:
            EventLinker.subscribe('Event5', callback=self.callback_with_kwargs_params)
            event = EmailEvent(email="email@email.com", message="Email message!")
            text = "Another param"

            # Act and Assert
            with raises(Exception):
                event_emitter.emit('Event5', event=event, text=text)

            # Act
            event_emitter.emit('Event5', event_1=event, text=text)
            while event_emitter.background_futures:  # Wait for all futures to complete
                await asyncio.gather(*event_emitter.background_futures, return_exceptions=True)

            # Assert
            callback_with_kwargs_params.assert_called_with(event_1=event, text=text)
            assert callback_with_kwargs_params.call_count == 1

    @pytest.mark.asyncio
    async def test_emit_with_multi_params(self, clean_event_linker):
        # Arrange
        event_emitter = AsyncioEventEmitter()
        with patch.object(self, 'callback_with_multi_params') as callback_with_multi_params:
            EventLinker.subscribe('Event6', callback=self.callback_with_multi_params)
            event = EmailEvent(email="email@email.com", message="Email message!")
            text = "Another param"

            # Act
            event_emitter.emit('Event6', event, text=text)
            while event_emitter.background_futures:  # Wait for all futures to complete
                await asyncio.gather(*event_emitter.background_futures, return_exceptions=True)

            # Assert
            callback_with_multi_params.assert_called_with(event, text=text)
            assert callback_with_multi_params.call_count == 1

    @pytest.mark.asyncio
    async def test_emit_with_sync_and_async_callbacks(self, clean_event_linker):
        # Arrange
        event_emitter = AsyncioEventEmitter()
        with patch.object(self, 'callback_with_args_params') as callback_with_args_params:
            with patch.object(self, 'callback_with_kwargs_params') as callback_with_kwargs_params:
                EventLinker.subscribe(Event, callback=self.callback_with_args_params)
                EventLinker.subscribe(Event, Exception, callback=self.callback_with_args_params, once=True)
                EventLinker.subscribe('Event', ValueError, callback=self.callback_with_kwargs_params)
                EventLinker.subscribe(Exception, callback=self.callback_with_kwargs_params)

                # Act
                event_emitter.emit(ValueError("Value error!"))
                while event_emitter.background_futures:  # Wait for all futures to complete
                    await asyncio.gather(*event_emitter.background_futures, return_exceptions=True)

                # Assert
                assert callback_with_args_params.call_count == 1
                assert callback_with_kwargs_params.call_count == 2

                # Act
                event_emitter.emit(TypeError("Type error!"))
                while event_emitter.background_futures:  # Wait for all futures to complete
                    await asyncio.gather(*event_emitter.background_futures, return_exceptions=True)

                # Assert
                assert callback_with_args_params.call_count == 1
                assert callback_with_kwargs_params.call_count == 3

                # Act
                event_emitter.emit(Event())
                while event_emitter.background_futures:  # Wait for all futures to complete
                    await asyncio.gather(*event_emitter.background_futures, return_exceptions=True)

                # Assert
                assert callback_with_args_params.call_count == 2
                assert callback_with_kwargs_params.call_count == 4

                # Act and Assert
                with raises(PyventusException):
                    event_emitter.emit('')
                assert callback_with_args_params.call_count == 2
                assert callback_with_kwargs_params.call_count == 4

                # Act
                event_emitter.emit(EmailEvent(email="email@email.com", message="Email message!"))
                while event_emitter.background_futures:  # Wait for all futures to complete
                    await asyncio.gather(*event_emitter.background_futures, return_exceptions=True)

                # Assert
                assert callback_with_args_params.call_count == 3
                assert callback_with_kwargs_params.call_count == 5

    @pytest.mark.asyncio
    async def test_execution_exceptions(self, clean_event_linker):
        # Arrange
        event_emitter = AsyncioEventEmitter()

        def _execute_with_exception():
            raise ValueError("Something went wrong here!")

        # Act and Assert
        with raises(ValueError):
            with patch.object(event_emitter, '_execute', new_callable=_execute_with_exception) as mock_execute:
                event_emitter.emit('EmptyEvent')

    @pytest.mark.asyncio
    async def test_with_custom_event_linkers(self, clean_event_linker):
        # Arrange
        class CustomEventLinker(EventLinker):
            pass

        event_emitter_1 = AsyncioEventEmitter(event_linker=EventLinker)
        event_emitter_2 = AsyncioEventEmitter(event_linker=CustomEventLinker)
        with patch.object(self, 'callback_with_multi_params') as callback_with_multi_params:
            CustomEventLinker.subscribe(Event, callback=self.callback_with_multi_params)
            EventLinker.subscribe(Event, callback=self.callback_with_multi_params)

            # Act
            event_emitter_1.emit('Any')
            while event_emitter_1.background_futures:  # Wait for all futures to complete
                await asyncio.gather(*event_emitter_1.background_futures, return_exceptions=True)

            # Assert
            assert callback_with_multi_params.call_count == 1

            # Act
            event_emitter_2.emit('Another')
            while event_emitter_2.background_futures:  # Wait for all futures to complete
                await asyncio.gather(*event_emitter_2.background_futures, return_exceptions=True)

            # Assert
            assert callback_with_multi_params.call_count == 2
