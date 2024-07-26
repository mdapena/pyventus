from _pytest.python_api import raises

from pyventus import PyventusException
from pyventus.core.utils import validate_callback, get_callback_name, is_callback_async, is_callback_generator
from ... import CallbackDefinitions


class TestCallbackUtils:
    def test_validate_callback(self):
        # ----------------------------------------------
        # Happy path tests (Arrange | Act | Assert)
        # ----------

        # Sync callbacks
        sync_instance = CallbackDefinitions.Sync()

        validate_callback(callback=CallbackDefinitions.Sync.function)
        validate_callback(callback=CallbackDefinitions.Sync.static_method)
        validate_callback(callback=CallbackDefinitions.Sync.class_method)
        validate_callback(callback=sync_instance.instance_method)
        validate_callback(callback=sync_instance)

        # Sync generator callbacks
        sync_generator_instance = CallbackDefinitions.SyncGenerator()

        validate_callback(callback=CallbackDefinitions.SyncGenerator.function)
        validate_callback(callback=CallbackDefinitions.SyncGenerator.static_method)
        validate_callback(callback=CallbackDefinitions.SyncGenerator.class_method)
        validate_callback(callback=sync_generator_instance.instance_method)
        validate_callback(callback=sync_generator_instance)

        # Async callbacks
        async_instance = CallbackDefinitions.Async()

        validate_callback(callback=CallbackDefinitions.Async.function)
        validate_callback(callback=CallbackDefinitions.Async.static_method)
        validate_callback(callback=CallbackDefinitions.Async.class_method)
        validate_callback(callback=async_instance.instance_method)
        validate_callback(callback=async_instance)

        # Async generator callbacks
        async_generator_instance = CallbackDefinitions.AsyncGenerator()

        validate_callback(callback=CallbackDefinitions.AsyncGenerator.function)
        validate_callback(callback=CallbackDefinitions.AsyncGenerator.static_method)
        validate_callback(callback=CallbackDefinitions.AsyncGenerator.class_method)
        validate_callback(callback=async_generator_instance.instance_method)
        validate_callback(callback=async_generator_instance)

        # ----------------------------------------------
        # Error path tests (Arrange | Act | Assert)
        # ----------
        no_callable = CallbackDefinitions.NoCallable()
        with raises(PyventusException):
            validate_callback(callback=no_callable)

        with raises(PyventusException):
            validate_callback(callback=True)

        with raises(PyventusException):
            validate_callback(callback=None)

    def test_get_callback_name(self):
        # ----------------------------------------------
        # Happy path tests (Arrange | Act | Assert)
        # ----------

        sync_instance = CallbackDefinitions.Sync()
        async_instance = CallbackDefinitions.Async()

        # Sync
        assert CallbackDefinitions.Sync.function.__name__ == get_callback_name(
            callback=CallbackDefinitions.Sync.function
        )
        assert CallbackDefinitions.Sync.static_method.__name__ == get_callback_name(
            callback=CallbackDefinitions.Sync.static_method
        )
        assert CallbackDefinitions.Sync.class_method.__name__ == get_callback_name(
            callback=CallbackDefinitions.Sync.class_method
        )
        assert sync_instance.instance_method.__name__ == get_callback_name(callback=sync_instance.instance_method)
        assert type(sync_instance).__name__ == get_callback_name(callback=sync_instance)

        # Async
        assert CallbackDefinitions.Async.function.__name__ == get_callback_name(
            callback=CallbackDefinitions.Async.function
        )
        assert CallbackDefinitions.Async.static_method.__name__ == get_callback_name(
            callback=CallbackDefinitions.Async.static_method
        )
        assert CallbackDefinitions.Async.class_method.__name__ == get_callback_name(
            callback=CallbackDefinitions.Async.class_method
        )
        assert async_instance.instance_method.__name__ == get_callback_name(callback=async_instance.instance_method)
        assert type(async_instance).__name__ == get_callback_name(callback=async_instance)

        assert "None" == get_callback_name(callback=None)

    def test_is_callback_async(self):
        # ----------------------------------------------
        # Happy path tests (Arrange | Act | Assert)
        # ----------

        # Sync callbacks
        sync_instance = CallbackDefinitions.Sync()

        assert not is_callback_async(callback=CallbackDefinitions.Sync.function)
        assert not is_callback_async(callback=CallbackDefinitions.Sync.static_method)
        assert not is_callback_async(callback=CallbackDefinitions.Sync.class_method)
        assert not is_callback_async(callback=sync_instance.instance_method)
        assert not is_callback_async(callback=sync_instance)

        # Sync generator callbacks
        sync_generator_instance = CallbackDefinitions.SyncGenerator()

        assert not is_callback_async(callback=CallbackDefinitions.SyncGenerator.function)
        assert not is_callback_async(callback=CallbackDefinitions.SyncGenerator.static_method)
        assert not is_callback_async(callback=CallbackDefinitions.SyncGenerator.class_method)
        assert not is_callback_async(callback=sync_generator_instance.instance_method)
        assert not is_callback_async(callback=sync_generator_instance)

        # Async callbacks
        async_instance = CallbackDefinitions.Async()

        assert is_callback_async(callback=CallbackDefinitions.Async.function)
        assert is_callback_async(callback=CallbackDefinitions.Async.static_method)
        assert is_callback_async(callback=CallbackDefinitions.Async.class_method)
        assert is_callback_async(callback=async_instance.instance_method)
        assert is_callback_async(callback=async_instance)

        # Async generator callbacks
        async_generator_instance = CallbackDefinitions.AsyncGenerator()

        assert is_callback_async(callback=CallbackDefinitions.AsyncGenerator.function)
        assert is_callback_async(callback=CallbackDefinitions.AsyncGenerator.static_method)
        assert is_callback_async(callback=CallbackDefinitions.AsyncGenerator.class_method)
        assert is_callback_async(callback=async_generator_instance.instance_method)
        assert is_callback_async(callback=async_generator_instance)

        # No callable
        no_callable = CallbackDefinitions.NoCallable()

        assert not is_callback_async(callback=no_callable)

    def test_is_callback_generator(self):
        # ----------------------------------------------
        # Happy path tests (Arrange | Act | Assert)
        # ----------

        # Sync callbacks
        sync_instance = CallbackDefinitions.Sync()

        assert not is_callback_generator(callback=CallbackDefinitions.Sync.function)
        assert not is_callback_generator(callback=CallbackDefinitions.Sync.static_method)
        assert not is_callback_generator(callback=CallbackDefinitions.Sync.class_method)
        assert not is_callback_generator(callback=sync_instance.instance_method)
        assert not is_callback_generator(callback=sync_instance)

        # Sync generator callbacks
        sync_generator_instance = CallbackDefinitions.SyncGenerator()

        assert is_callback_generator(callback=CallbackDefinitions.SyncGenerator.function)
        assert is_callback_generator(callback=CallbackDefinitions.SyncGenerator.static_method)
        assert is_callback_generator(callback=CallbackDefinitions.SyncGenerator.class_method)
        assert is_callback_generator(callback=sync_generator_instance.instance_method)
        assert is_callback_generator(callback=sync_generator_instance)

        # Async callbacks
        async_instance = CallbackDefinitions.Async()

        assert not is_callback_generator(callback=CallbackDefinitions.Async.function)
        assert not is_callback_generator(callback=CallbackDefinitions.Async.static_method)
        assert not is_callback_generator(callback=CallbackDefinitions.Async.class_method)
        assert not is_callback_generator(callback=async_instance.instance_method)
        assert not is_callback_generator(callback=async_instance)

        # Async generator callbacks
        async_generator_instance = CallbackDefinitions.AsyncGenerator()

        assert is_callback_generator(callback=CallbackDefinitions.AsyncGenerator.function)
        assert is_callback_generator(callback=CallbackDefinitions.AsyncGenerator.static_method)
        assert is_callback_generator(callback=CallbackDefinitions.AsyncGenerator.class_method)
        assert is_callback_generator(callback=async_generator_instance.instance_method)
        assert is_callback_generator(callback=async_generator_instance)

        # No callable
        no_callable = CallbackDefinitions.NoCallable()

        assert not is_callback_generator(callback=no_callable)
