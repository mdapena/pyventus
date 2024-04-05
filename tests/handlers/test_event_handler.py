import asyncio
from threading import current_thread, main_thread

from _pytest.python_api import raises

from pyventus import EventHandler, PyventusException
from tests import EventFixtures
from .. import CallbackFixtures, CallbackDefinitions


class TestEventHandler:

    def test_callback_validation(self):
        # ----------------------------------------------
        # Happy path tests (Arrange | Act | Assert)
        # ----------

        sync_instance = CallbackDefinitions.Sync()
        async_instance = CallbackDefinitions.Async()
        no_callable = CallbackDefinitions.NoCallable()

        # Sync
        EventHandler.validate_callback(callback=CallbackDefinitions.Sync.function)
        EventHandler.validate_callback(callback=CallbackDefinitions.Sync.static_method)
        EventHandler.validate_callback(callback=CallbackDefinitions.Sync.class_method)
        EventHandler.validate_callback(callback=sync_instance.instance_method)
        EventHandler.validate_callback(callback=sync_instance)

        # Async
        EventHandler.validate_callback(callback=CallbackDefinitions.Async.function)
        EventHandler.validate_callback(callback=CallbackDefinitions.Async.static_method)
        EventHandler.validate_callback(callback=CallbackDefinitions.Async.class_method)
        EventHandler.validate_callback(callback=async_instance.instance_method)
        EventHandler.validate_callback(callback=async_instance)

        # ----------------------------------------------
        # Error path tests (Arrange | Act | Assert)
        # ----------
        with raises(PyventusException):
            EventHandler.validate_callback(callback=no_callable)

        with raises(PyventusException):
            EventHandler.validate_callback(callback=True)

        with raises(PyventusException):
            EventHandler.validate_callback(callback=None)

    def test_async_check(self):
        # ----------------------------------------------
        # Happy path tests (Arrange | Act | Assert)
        # ----------

        sync_instance = CallbackDefinitions.Sync()
        async_instance = CallbackDefinitions.Async()
        no_callable = CallbackDefinitions.NoCallable()

        # Sync
        assert not EventHandler.is_async(callback=CallbackDefinitions.Sync.function)
        assert not EventHandler.is_async(callback=CallbackDefinitions.Sync.static_method)
        assert not EventHandler.is_async(callback=CallbackDefinitions.Sync.class_method)
        assert not EventHandler.is_async(callback=sync_instance.instance_method)
        assert not EventHandler.is_async(callback=sync_instance)

        # Async
        assert EventHandler.is_async(callback=CallbackDefinitions.Async.function)
        assert EventHandler.is_async(callback=CallbackDefinitions.Async.static_method)
        assert EventHandler.is_async(callback=CallbackDefinitions.Async.class_method)
        assert EventHandler.is_async(callback=async_instance.instance_method)
        assert EventHandler.is_async(callback=async_instance)

        # ----------------------------------------------
        # Error path tests (Arrange | Act | Assert)
        # ----------
        with raises(PyventusException):
            EventHandler.is_async(callback=no_callable)

        with raises(PyventusException):
            EventHandler.is_async(callback=True)

        with raises(PyventusException):
            EventHandler.is_async(callback=None)

    def test_get_callback_name(self):
        # ----------------------------------------------
        # Happy path tests (Arrange | Act | Assert)
        # ----------

        sync_instance = CallbackDefinitions.Sync()
        async_instance = CallbackDefinitions.Async()

        # Sync
        assert CallbackDefinitions.Sync.function.__name__ == EventHandler.get_callback_name(
            callback=CallbackDefinitions.Sync.function
        )
        assert CallbackDefinitions.Sync.static_method.__name__ == EventHandler.get_callback_name(
            callback=CallbackDefinitions.Sync.static_method
        )
        assert CallbackDefinitions.Sync.class_method.__name__ == EventHandler.get_callback_name(
            callback=CallbackDefinitions.Sync.class_method
        )
        assert sync_instance.instance_method.__name__ == EventHandler.get_callback_name(
            callback=sync_instance.instance_method
        )
        assert type(sync_instance).__name__ == EventHandler.get_callback_name(callback=sync_instance)

        # Async
        assert CallbackDefinitions.Async.function.__name__ == EventHandler.get_callback_name(
            callback=CallbackDefinitions.Async.function
        )
        assert CallbackDefinitions.Async.static_method.__name__ == EventHandler.get_callback_name(
            callback=CallbackDefinitions.Async.static_method
        )
        assert CallbackDefinitions.Async.class_method.__name__ == EventHandler.get_callback_name(
            callback=CallbackDefinitions.Async.class_method
        )
        assert async_instance.instance_method.__name__ == EventHandler.get_callback_name(
            callback=async_instance.instance_method
        )
        assert type(async_instance).__name__ == EventHandler.get_callback_name(callback=async_instance)

    def test_once_flag(self):
        # ----------------------------------------------
        # Happy path tests (Arrange | Act | Assert)
        # ----------
        assert EventHandler(once=True, force_async=False, event_callback=CallbackFixtures.Sync()).once
        assert not EventHandler(once=False, force_async=False, event_callback=CallbackFixtures.Sync()).once

        # ----------------------------------------------
        # Error path tests (Arrange | Act | Assert)
        # ----------
        with raises(PyventusException):
            EventHandler(
                once="True",
                force_async=False,
                event_callback=CallbackFixtures.Sync(),
            )

    def test_force_async_flag(self):
        # ----------------------------------------------
        # Happy path tests (Arrange | Act | Assert)
        # ----------
        assert EventHandler(once=False, force_async=True, event_callback=CallbackFixtures.Sync()).force_async
        assert not EventHandler(once=False, force_async=False, event_callback=CallbackFixtures.Sync()).force_async

        # ----------------------------------------------
        # Happy path tests (Arrange | Act | Assert)
        # ----------
        with raises(PyventusException):
            EventHandler(
                once=False,
                force_async="True",
                event_callback=CallbackFixtures.Sync(),
            )

    def test_event_callback(self):
        # ----------------------------------------------
        # Happy path tests (Arrange | Act | Assert)
        # ----------
        int_param = 2
        str_param = "param1"
        event_param = EventFixtures.DtcEvent2(attr1="", attr2={})
        list_param = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        dict_param = {"key1": "value1"}
        success_callback = CallbackFixtures.Sync()
        failure_callback = CallbackFixtures.Async()

        # Async/Sync event callbacks
        sync_event_callback = CallbackFixtures.Sync()
        async_event_callback = CallbackFixtures.Async()

        event_handler1 = EventHandler(
            once=False,
            force_async=False,
            event_callback=sync_event_callback,
            success_callback=success_callback,
            failure_callback=failure_callback,
        )
        event_handler2 = EventHandler(
            once=False,
            force_async=False,
            event_callback=async_event_callback,
            success_callback=success_callback,
            failure_callback=failure_callback,
        )

        asyncio.run(event_handler1())
        asyncio.run(event_handler2(int_param, event_param, dict_param, param4=str_param, param5=list_param))

        assert (
            event_handler1 is not None
            and event_handler1._event_callback is sync_event_callback
            and event_handler1._success_callback is success_callback
            and event_handler1._failure_callback is failure_callback
            and sync_event_callback.call_count == 1
        )
        assert (
            event_handler2 is not None
            and event_handler2._event_callback is async_event_callback
            and event_handler2._success_callback is success_callback
            and event_handler2._failure_callback is failure_callback
            and async_event_callback.call_count == 1
            and async_event_callback.args == (int_param, event_param, dict_param)
            and async_event_callback.kwargs == {"param4": str_param, "param5": list_param}
        )
        assert success_callback.call_count == 2 and failure_callback.call_count == 0

    def test_success_callback(self):
        # ----------------------------------------------
        # Happy path tests (Arrange | Act | Assert)
        # ----------
        return_value = ["string", 2, 2.3, object(), ("str", {"key": "value"})]
        event_callback = CallbackFixtures.Sync(return_value=return_value)
        failure_callback = CallbackFixtures.Async()

        # Async/Sync success callbacks
        sync_success_callback = CallbackFixtures.Sync()
        async_success_callback = CallbackFixtures.Async()

        event_handler1 = EventHandler(
            once=False,
            force_async=False,
            event_callback=event_callback,
            success_callback=sync_success_callback,
            failure_callback=failure_callback,
        )
        event_handler2 = EventHandler(
            once=False,
            force_async=False,
            event_callback=event_callback,
            success_callback=async_success_callback,
            failure_callback=failure_callback,
        )

        asyncio.run(event_handler1())
        asyncio.run(event_handler2())

        assert (
            event_handler1 is not None
            and event_handler1._event_callback is event_callback
            and event_handler1._success_callback is sync_success_callback
            and event_handler1._failure_callback is failure_callback
            and sync_success_callback.call_count == 1
            and sync_success_callback.args == (return_value,)
            and not sync_success_callback.kwargs
        )
        assert (
            event_handler2 is not None
            and event_handler2._event_callback is event_callback
            and event_handler2._success_callback is async_success_callback
            and event_handler2._failure_callback is failure_callback
            and async_success_callback.call_count == 1
            and async_success_callback.args == (return_value,)
            and not async_success_callback.kwargs
        )
        assert event_callback.call_count == 2 and failure_callback.call_count == 0

    def test_failure_callback(self):
        # ----------------------------------------------
        # Happy path tests (Arrange | Act | Assert)
        # ----------
        value_error = ValueError("Something went wrong!")
        event_callback = CallbackFixtures.Sync(raise_exception=value_error)
        success_callback = CallbackFixtures.Sync()

        # Async/Sync failure callbacks
        sync_failure_callback = CallbackFixtures.Sync()
        async_failure_callback = CallbackFixtures.Async()

        event_handler1 = EventHandler(
            once=False,
            force_async=False,
            event_callback=event_callback,
            success_callback=success_callback,
            failure_callback=sync_failure_callback,
        )
        event_handler2 = EventHandler(
            once=False,
            force_async=False,
            event_callback=event_callback,
            success_callback=success_callback,
            failure_callback=async_failure_callback,
        )

        asyncio.run(event_handler1())
        asyncio.run(event_handler2())

        assert (
            event_handler1 is not None
            and event_handler1._event_callback is event_callback
            and event_handler1._success_callback is success_callback
            and event_handler1._failure_callback is sync_failure_callback
            and sync_failure_callback.call_count == 1
            and sync_failure_callback.args == (value_error,)
            and not sync_failure_callback.kwargs
        )
        assert (
            event_handler2 is not None
            and event_handler2._event_callback is event_callback
            and event_handler2._success_callback is success_callback
            and event_handler2._failure_callback is async_failure_callback
            and async_failure_callback.call_count == 1
            and async_failure_callback.args == (value_error,)
            and not async_failure_callback.kwargs
        )
        assert event_callback.call_count == 2 and success_callback.call_count == 0

    def test_force_async_behavior(self):
        # ----------------------------------------------
        # Happy path tests (Arrange | Act | Assert)
        # ----------
        class CustomException(Exception):
            def __init__(self, same_thread: bool):
                self.same_thread: bool = same_thread
                super().__init__("Custom Exception!")

        def check_different_thread_no_params() -> None:
            assert not (current_thread() == main_thread())

        def check_same_thread(results: bool | Exception):
            same_thread: bool = results.same_thread if isinstance(results, CustomException) else results
            assert current_thread() == main_thread()
            assert same_thread

        def check_different_thread(results: bool | Exception):
            same_thread: bool = results.same_thread if isinstance(results, CustomException) else results
            assert not (current_thread() == main_thread())
            assert not same_thread

        def sync_event_callback(raise_exception: bool) -> bool | Exception:
            same_thread: bool = current_thread() == main_thread()
            if raise_exception:
                raise CustomException(same_thread)
            else:
                return same_thread

        async def async_event_callback() -> None:
            assert current_thread() == main_thread()

        # Test force_async on True and with sync event_callback (Different thread)
        event_handler1 = EventHandler(
            once=False,
            force_async=True,
            event_callback=sync_event_callback,
            success_callback=check_different_thread,
            failure_callback=check_different_thread,
        )
        asyncio.run(event_handler1(raise_exception=False))
        asyncio.run(event_handler1(raise_exception=True))

        # Test force_async on False and with sync event_callback (Same thread)
        event_handler2 = EventHandler(
            once=False,
            force_async=False,
            event_callback=sync_event_callback,
            success_callback=check_same_thread,
            failure_callback=check_same_thread,
        )

        asyncio.run(event_handler2(raise_exception=False))
        asyncio.run(event_handler2(raise_exception=True))

        # Test force_async with async event_callback and without return value

        event_handler3 = EventHandler(
            once=False,
            force_async=True,
            event_callback=async_event_callback,
            success_callback=check_different_thread_no_params,
        )
        asyncio.run(event_handler3())
