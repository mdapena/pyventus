import asyncio
from typing import Callable

from _pytest.python_api import raises

from pyventus import Event, EventHandler, PyventusException
from .. import CallbackFixtures


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
            EventHandler(event_callback=CallbackFixtures.Sync(), success_callback=invalid_callback())

        # Act|Assert
        with raises(PyventusException):
            EventHandler(event_callback=CallbackFixtures.Sync(), failure_callback=invalid_callback())

    def test_once_time_listener_flag(self):
        # Arrange|Act|Assert
        assert EventHandler(event_callback=CallbackFixtures.Sync(), once=True).once
        assert not EventHandler(event_callback=CallbackFixtures.Sync(), once=False).once

    def test_creation_with_sync_callback(self):
        # Arrange
        sync_callback = CallbackFixtures.Sync()

        def sync_event_callback() -> None:
            print("Event received!")

        # Act
        event_handler1 = EventHandler(event_callback=sync_callback, success_callback=sync_event_callback)
        asyncio.run(event_handler1())

        # Assert
        assert event_handler1 is not None
        assert sync_callback.call_count == 1
        assert sync_callback.__class__.__name__ == EventHandler.get_callback_name(sync_callback)
        assert sync_event_callback.__name__ == EventHandler.get_callback_name(sync_event_callback)
        assert EventHandler.get_callback_name(None)

    def test_creation_with_async_callback(self):
        # Arrange
        async_callback = CallbackFixtures.Async()

        async def async_event_callback() -> None:
            print("Event received!")

        # Act
        event_handler1 = EventHandler(event_callback=async_callback, success_callback=async_event_callback)
        asyncio.run(event_handler1())

        # Assert
        assert event_handler1 is not None
        assert async_callback.call_count == 1
        assert async_callback.__class__.__name__ == EventHandler.get_callback_name(async_callback)
        assert async_event_callback.__name__ == EventHandler.get_callback_name(async_event_callback)

    def test_event_callback_execution(self):
        # Arrange
        int_param = 2
        str_param = "param1"
        event_param = Event()
        list_param = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        dict_param = {"key1": "value1"}

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
        assert event_callback.kwargs == {"param4": str_param, "param5": list_param}

    def test_success_callback_execution(self):
        # Arrange
        return_value = ["string", 2, 2.3, object(), ("str", {"key": "value"})]
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
        value_error = ValueError("Something went wrong!")
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
            pass  # pragma: no cover

        # Arrange
        failure_callback = CallbackFixtures.Async()
        event_handler = EventHandler(
            event_callback=callback_without_params,
            failure_callback=failure_callback,
        )

        # Act
        asyncio.run(event_handler("String!"))

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

    def test_callable_validation_and_is_async_method(self):
        # Arrange
        class AsyncClass:
            async def __call__(self):
                pass  # pragma: no cover

            @staticmethod
            async def static_async():
                pass  # pragma: no cover

            @classmethod
            async def cls_async(cls):
                pass  # pragma: no cover

            async def self_async(self):
                pass  # pragma: no cover

        class SyncClass:
            def __call__(self):
                pass  # pragma: no cover

            @staticmethod
            def static_sync():
                pass  # pragma: no cover

            @classmethod
            def cls_sync(cls):
                pass  # pragma: no cover

            def self_sync(self):
                pass  # pragma: no cover

        class ClassNoCall:
            pass  # pragma: no cover

        async def async_func():
            pass  # pragma: no cover

        def sync_func():
            pass  # pragma: no cover

        async_object = AsyncClass()
        sync_object = SyncClass()

        # Act | Assert
        with raises(PyventusException):
            EventHandler.validate_callback(callback=ClassNoCall())  # type: ignore

        EventHandler.validate_callback(callback=async_object)
        EventHandler.validate_callback(callback=async_object.self_async)
        EventHandler.validate_callback(callback=AsyncClass.cls_async)
        EventHandler.validate_callback(callback=AsyncClass.static_async)

        EventHandler.validate_callback(callback=sync_object)
        EventHandler.validate_callback(callback=sync_object.self_sync)
        EventHandler.validate_callback(callback=SyncClass.cls_sync)
        EventHandler.validate_callback(callback=SyncClass.static_sync)

        EventHandler.validate_callback(callback=async_func)
        EventHandler.validate_callback(callback=sync_func)

        assert EventHandler.is_async(callback=async_object)
        assert EventHandler.is_async(callback=async_object.self_async)
        assert EventHandler.is_async(callback=AsyncClass.cls_async)
        assert EventHandler.is_async(callback=AsyncClass.static_async)

        assert not EventHandler.is_async(callback=sync_object)
        assert not EventHandler.is_async(callback=sync_object.self_sync)
        assert not EventHandler.is_async(callback=SyncClass.cls_sync)
        assert not EventHandler.is_async(callback=SyncClass.static_sync)

        assert EventHandler.is_async(callback=async_func)
        assert not EventHandler.is_async(callback=sync_func)

        with raises(PyventusException):
            EventHandler.is_async(AsyncClass)
