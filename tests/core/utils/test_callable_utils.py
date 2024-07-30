from _pytest.python_api import raises

from pyventus import PyventusException
from pyventus.core.utils import validate_callable, get_callable_name, is_callable_async, is_callable_generator
from ... import CallbackDefinitions


class TestCallbackUtils:
    def test_validate_callback(self):
        # ----------------------------------------------
        # Happy path tests (Arrange | Act | Assert)
        # ----------

        # Sync callbacks
        sync_instance = CallbackDefinitions.Sync()

        validate_callable(CallbackDefinitions.Sync.function)
        validate_callable(CallbackDefinitions.Sync.static_method)
        validate_callable(CallbackDefinitions.Sync.class_method)
        validate_callable(sync_instance.instance_method)
        validate_callable(sync_instance)

        # Sync generator callbacks
        sync_generator_instance = CallbackDefinitions.SyncGenerator()

        validate_callable(CallbackDefinitions.SyncGenerator.function)
        validate_callable(CallbackDefinitions.SyncGenerator.static_method)
        validate_callable(CallbackDefinitions.SyncGenerator.class_method)
        validate_callable(sync_generator_instance.instance_method)
        validate_callable(sync_generator_instance)

        # Async callbacks
        async_instance = CallbackDefinitions.Async()

        validate_callable(CallbackDefinitions.Async.function)
        validate_callable(CallbackDefinitions.Async.static_method)
        validate_callable(CallbackDefinitions.Async.class_method)
        validate_callable(async_instance.instance_method)
        validate_callable(async_instance)

        # Async generator callbacks
        async_generator_instance = CallbackDefinitions.AsyncGenerator()

        validate_callable(CallbackDefinitions.AsyncGenerator.function)
        validate_callable(CallbackDefinitions.AsyncGenerator.static_method)
        validate_callable(CallbackDefinitions.AsyncGenerator.class_method)
        validate_callable(async_generator_instance.instance_method)
        validate_callable(async_generator_instance)

        # ----------------------------------------------
        # Error path tests (Arrange | Act | Assert)
        # ----------
        no_callable = CallbackDefinitions.NoCallable()
        with raises(PyventusException):
            validate_callable(no_callable)

        with raises(PyventusException):
            validate_callable(True)

        with raises(PyventusException):
            validate_callable(None)

    def test_get_callback_name(self):
        # ----------------------------------------------
        # Happy path tests (Arrange | Act | Assert)
        # ----------

        sync_instance = CallbackDefinitions.Sync()
        async_instance = CallbackDefinitions.Async()

        # Sync
        assert CallbackDefinitions.Sync.function.__name__ == get_callable_name(CallbackDefinitions.Sync.function)
        assert CallbackDefinitions.Sync.static_method.__name__ == get_callable_name(
            CallbackDefinitions.Sync.static_method
        )
        assert CallbackDefinitions.Sync.class_method.__name__ == get_callable_name(
            CallbackDefinitions.Sync.class_method
        )
        assert sync_instance.instance_method.__name__ == get_callable_name(sync_instance.instance_method)
        assert type(sync_instance).__name__ == get_callable_name(sync_instance)

        # Async
        assert CallbackDefinitions.Async.function.__name__ == get_callable_name(CallbackDefinitions.Async.function)
        assert CallbackDefinitions.Async.static_method.__name__ == get_callable_name(
            CallbackDefinitions.Async.static_method
        )
        assert CallbackDefinitions.Async.class_method.__name__ == get_callable_name(
            CallbackDefinitions.Async.class_method
        )
        assert async_instance.instance_method.__name__ == get_callable_name(async_instance.instance_method)
        assert type(async_instance).__name__ == get_callable_name(async_instance)

        assert "None" == get_callable_name(None)

    def test_is_callback_async(self):
        # ----------------------------------------------
        # Happy path tests (Arrange | Act | Assert)
        # ----------

        # Sync callbacks
        sync_instance = CallbackDefinitions.Sync()

        assert not is_callable_async(CallbackDefinitions.Sync.function)
        assert not is_callable_async(CallbackDefinitions.Sync.static_method)
        assert not is_callable_async(CallbackDefinitions.Sync.class_method)
        assert not is_callable_async(sync_instance.instance_method)
        assert not is_callable_async(sync_instance)

        # Sync generator callbacks
        sync_generator_instance = CallbackDefinitions.SyncGenerator()

        assert not is_callable_async(CallbackDefinitions.SyncGenerator.function)
        assert not is_callable_async(CallbackDefinitions.SyncGenerator.static_method)
        assert not is_callable_async(CallbackDefinitions.SyncGenerator.class_method)
        assert not is_callable_async(sync_generator_instance.instance_method)
        assert not is_callable_async(sync_generator_instance)

        # Async callbacks
        async_instance = CallbackDefinitions.Async()

        assert is_callable_async(CallbackDefinitions.Async.function)
        assert is_callable_async(CallbackDefinitions.Async.static_method)
        assert is_callable_async(CallbackDefinitions.Async.class_method)
        assert is_callable_async(async_instance.instance_method)
        assert is_callable_async(async_instance)

        # Async generator callbacks
        async_generator_instance = CallbackDefinitions.AsyncGenerator()

        assert is_callable_async(CallbackDefinitions.AsyncGenerator.function)
        assert is_callable_async(CallbackDefinitions.AsyncGenerator.static_method)
        assert is_callable_async(CallbackDefinitions.AsyncGenerator.class_method)
        assert is_callable_async(async_generator_instance.instance_method)
        assert is_callable_async(async_generator_instance)

        # No callable
        no_callable = CallbackDefinitions.NoCallable()

        assert not is_callable_async(no_callable)

    def test_is_callback_generator(self):
        # ----------------------------------------------
        # Happy path tests (Arrange | Act | Assert)
        # ----------

        # Sync callbacks
        sync_instance = CallbackDefinitions.Sync()

        assert not is_callable_generator(CallbackDefinitions.Sync.function)
        assert not is_callable_generator(CallbackDefinitions.Sync.static_method)
        assert not is_callable_generator(CallbackDefinitions.Sync.class_method)
        assert not is_callable_generator(sync_instance.instance_method)
        assert not is_callable_generator(sync_instance)

        # Sync generator callbacks
        sync_generator_instance = CallbackDefinitions.SyncGenerator()

        assert is_callable_generator(CallbackDefinitions.SyncGenerator.function)
        assert is_callable_generator(CallbackDefinitions.SyncGenerator.static_method)
        assert is_callable_generator(CallbackDefinitions.SyncGenerator.class_method)
        assert is_callable_generator(sync_generator_instance.instance_method)
        assert is_callable_generator(sync_generator_instance)

        # Async callbacks
        async_instance = CallbackDefinitions.Async()

        assert not is_callable_generator(CallbackDefinitions.Async.function)
        assert not is_callable_generator(CallbackDefinitions.Async.static_method)
        assert not is_callable_generator(CallbackDefinitions.Async.class_method)
        assert not is_callable_generator(async_instance.instance_method)
        assert not is_callable_generator(async_instance)

        # Async generator callbacks
        async_generator_instance = CallbackDefinitions.AsyncGenerator()

        assert is_callable_generator(CallbackDefinitions.AsyncGenerator.function)
        assert is_callable_generator(CallbackDefinitions.AsyncGenerator.static_method)
        assert is_callable_generator(CallbackDefinitions.AsyncGenerator.class_method)
        assert is_callable_generator(async_generator_instance.instance_method)
        assert is_callable_generator(async_generator_instance)

        # No callable
        no_callable = CallbackDefinitions.NoCallable()

        assert not is_callable_generator(no_callable)
