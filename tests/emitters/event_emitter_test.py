from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Type, Generator, List, Dict

from _pytest.python_api import raises

from pyventus import EventEmitter, EventLinker, PyventusException
from .. import CallbackFixtures, EventFixtures


class EventEmitterTest(ABC):
    """A set of pre-configured tests for subclasses of EventEmitter."""

    @staticmethod
    @contextmanager
    def run_emission_test(event_emitter: EventEmitter, event_linker: Type[EventLinker] = EventLinker) -> Generator:
        """
        Context manager for performing tests to check if the event emission is working
        properly using both synchronous and asynchronous callbacks.

        The `run_emission_test` function is a context manager that allows you to perform tests
        on event emission behavior. When used with a `with` statement, you should complete the
        necessary actions to propagate the events that were linked and emitted within the
        `run_emission_test` function before the yield statement. These actions might include
        triggering events, calling relevant functions, or waiting for event propagation to
        complete.

        After the execution of the code section inside the `with` statement, the control is
        returned to the `run_emission_test` function. At this point, the function can proceed
        to perform the assertions to validate the expected behavior of the callbacks.

        Usage:
        ```Python
        with EventEmitterTest.emission_test(event_emitter):
            # Wait for all events to propagate
        ```

        :param event_emitter: The event emitter object responsible for emitting events.
        :param event_linker: The event linker class to be used for linking events and
            callbacks. Defaults to EventLinker.
        :return: A generator object for the test.
        """

        # Clear event linker
        event_linker.remove_all()

        # Test emission when empty
        event_emitter.emit(EventFixtures.EmptyEvent())

        # Create a dummy event linker for testing purposes
        class __DummyEventLinker(EventLinker, max_event_handlers=1):
            pass  # pragma: no cover

        # ----------------------------------------------
        # Arrange
        # ----------

        int_param: int = 2
        str_param: str = "param1"
        event_param: object = EventFixtures.EmptyEvent()
        list_param: List[int] = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        dict_param: Dict[str, str] = {"key1": "value1"}
        custom_event1 = EventFixtures.DtcEvent1(attr1="attr1")
        custom_event2 = EventFixtures.DtcEvent2(attr1="attr1", attr2={"attr2": "attr"})
        custom_event_with_validation = EventFixtures.DtcWithValidation(attr1="att", attr2=7.65)
        custom_exception1 = EventFixtures.CustomException1("Custom Exception 1 raised!")
        custom_exception2 = EventFixtures.CustomException2("Custom Exception 2 raised!")
        return_value: object = EventFixtures.EmptyEvent()

        # Callbacks
        cb_without_params: CallbackFixtures.Base = CallbackFixtures.Sync()
        cb_with_two_params: CallbackFixtures.Base = CallbackFixtures.Async()
        cb_with_args: CallbackFixtures.Base = CallbackFixtures.Sync()
        cb_with_kwargs: CallbackFixtures.Base = CallbackFixtures.Async()
        cb_with_custom_event1: CallbackFixtures.Base = CallbackFixtures.Sync()
        cb_with_custom_event2_and_extras: CallbackFixtures.Base = CallbackFixtures.Async()
        cb_with_custom_event_validated: CallbackFixtures.Base = CallbackFixtures.Sync()
        cb_with_event: CallbackFixtures.Base = CallbackFixtures.Async()
        cb_with_custom_exception1: CallbackFixtures.Base = CallbackFixtures.Sync()
        cb_with_custom_exception2_and_extras: CallbackFixtures.Base = CallbackFixtures.Async()
        cb_with_exception: CallbackFixtures.Base = CallbackFixtures.Sync()
        cb_with_args_and_kwargs: CallbackFixtures.Base = CallbackFixtures.Async()

        cb_with_return_value: CallbackFixtures.Base = CallbackFixtures.Sync(return_value=return_value)
        cb_with_raise_exception: CallbackFixtures.Base = CallbackFixtures.Async(raise_exception=custom_exception1)

        # Success and failure callbacks
        default_success_callback = event_linker.get_default_success_callback()
        success_callback: CallbackFixtures.Base = (
            default_success_callback if default_success_callback else CallbackFixtures.Async()
        )
        default_failure_callback = event_linker.get_default_failure_callback()
        failure_callback: CallbackFixtures.Base = (
            default_failure_callback if default_failure_callback else CallbackFixtures.Sync()
        )

        # String Events
        event_linker.subscribe("StringEventWithoutParams", event_callback=cb_without_params.__call__, force_async=True)
        event_linker.subscribe("StringEventWithoutParams", "AnotherStringEvent", event_callback=cb_without_params)
        event_linker.subscribe("StringEventWithTwoParams", event_callback=cb_with_two_params, force_async=True)
        event_linker.subscribe("StringEventWithArgs", event_callback=cb_with_args)
        event_linker.subscribe("StringEventWithKwargs", event_callback=cb_with_kwargs, once=True)

        # Events
        event_linker.subscribe(EventFixtures.DtcEvent1, event_callback=cb_with_custom_event1)
        event_linker.subscribe(EventFixtures.DtcEvent2, event_callback=cb_with_custom_event2_and_extras)
        event_linker.subscribe(EventFixtures.DtcWithValidation, event_callback=cb_with_custom_event_validated)
        event_linker.subscribe(
            EventFixtures.DtcEvent1, EventFixtures.DtcEvent2, event_callback=cb_with_event, once=True
        )

        # Exception Events
        event_linker.subscribe(EventFixtures.CustomException1, event_callback=cb_with_custom_exception1)
        event_linker.subscribe(EventFixtures.CustomException2, event_callback=cb_with_custom_exception2_and_extras)
        event_linker.subscribe(TypeError, EventFixtures.CustomException1, event_callback=cb_with_exception, once=True)

        # Test success callback execution
        with event_linker.once("StringEventWithSuccessCallback") as linker:
            linker.on_event(cb_with_return_value)
            linker.on_success(success_callback)
            linker.on_failure(failure_callback)

        # Test failure callback execution
        with event_linker.on("StringEventWithFailureCallback", force_async=True) as linker:
            linker.on_event(cb_with_raise_exception)
            linker.on_success(success_callback)
            linker.on_failure(failure_callback)

        # Test Error Handling
        with event_linker.on("ErrorHandling") as linker:
            linker.on_event(CallbackFixtures.Sync())
            linker.on_success(CallbackFixtures.Async(raise_exception=ValueError("Something went wrong!")))
            linker.on_failure(failure_callback)

        with event_linker.on("ErrorHandling") as linker:
            linker.on_event(CallbackFixtures.Sync(raise_exception=ValueError("Something went wrong!")))
            linker.on_success(success_callback)
            linker.on_failure(CallbackFixtures.Async(raise_exception=ValueError("Something went wrong!")))

        # Any Event
        event_linker.subscribe(..., event_callback=cb_with_args_and_kwargs)

        # Different namespace
        __DummyEventLinker.subscribe(..., event_callback=cb_with_args_and_kwargs)

        # ----------------------------------------------
        # Act
        # ----------

        # String events
        event_emitter.emit("AnotherStringEvent")
        event_emitter.emit("StringEventWithoutParams")
        event_emitter.emit("StringEventWithTwoParams", dict_param, param2=event_param)
        event_emitter.emit("StringEventWithTwoParams", dict_param, param2=event_param)
        event_emitter.emit("StringEventWithArgs", int_param, str_param, dict_param)
        event_emitter.emit("StringEventWithKwargs", param1=int_param, param2=str_param, param3=list_param)
        event_emitter.emit("StringEventWithKwargs", str_param, param2=int_param, param3=dict_param)
        event_emitter.emit("UnsubscribedEvent", int_param, param2=dict_param)

        with raises(PyventusException):
            event_emitter.emit("")

        # Events
        event_emitter.emit(custom_event1)
        event_emitter.emit(custom_event2, int_param, str_param, param3=event_param, param4=list_param)
        event_emitter.emit(custom_event_with_validation)
        event_emitter.emit(EventFixtures.EmptyEvent())

        with raises(PyventusException):
            event_emitter.emit(None)
        with raises(PyventusException):
            event_emitter.emit(EventFixtures.EmptyEvent)
        with raises(PyventusException):
            event_emitter.emit(EventFixtures.DtcWithValidation(attr1="at", attr2=2.3))

        # Exception events
        event_emitter.emit(custom_exception1)
        event_emitter.emit(custom_exception2, int_param, str_param, param2=event_param, param3=list_param)
        event_emitter.emit(Exception())

        try:
            EventFixtures.DtcWithValidation(attr1="at", attr2=7)
        except PyventusException as e:
            event_emitter.emit(e)

        with raises(PyventusException):
            event_emitter.emit(Exception)

        # Events with success and failure callbacks
        event_emitter.emit("StringEventWithSuccessCallback")
        event_emitter.emit("StringEventWithSuccessCallback")
        event_emitter.emit("StringEventWithFailureCallback")
        event_emitter.emit("ErrorHandling")

        # Wait for all events to propagate
        yield

        # ----------------------------------------------
        # Assert
        # ----------

        assert cb_without_params.call_count == 3

        assert cb_with_two_params.call_count == 2
        assert cb_with_two_params.args == (dict_param,)
        assert cb_with_two_params.kwargs == {"param2": event_param}

        assert cb_with_args.call_count == 1
        assert cb_with_args.args == (int_param, str_param, dict_param)
        assert not cb_with_args.kwargs

        assert cb_with_kwargs.call_count == 1
        assert not cb_with_kwargs.args
        assert cb_with_kwargs.kwargs == {"param1": int_param, "param2": str_param, "param3": list_param}

        assert cb_with_custom_event1.call_count == 1
        assert cb_with_custom_event1.args == (custom_event1,)
        assert not cb_with_custom_event1.kwargs

        assert cb_with_custom_event2_and_extras.call_count == 1
        assert cb_with_custom_event2_and_extras.args == (custom_event2, int_param, str_param)
        assert cb_with_custom_event2_and_extras.kwargs == {"param3": event_param, "param4": list_param}

        assert cb_with_custom_event_validated.call_count == 1
        assert cb_with_custom_event_validated.args == (custom_event_with_validation,)
        assert not cb_with_custom_event_validated.kwargs

        assert cb_with_event.call_count == 1
        assert cb_with_event.args == (custom_event1,)
        assert not cb_with_event.kwargs

        assert cb_with_custom_exception1.call_count == 1
        assert cb_with_custom_exception1.args == (custom_exception1,)
        assert not cb_with_custom_exception1.kwargs

        assert cb_with_custom_exception2_and_extras.call_count == 1
        assert cb_with_custom_exception2_and_extras.args == (custom_exception2, int_param, str_param)
        assert cb_with_custom_exception2_and_extras.kwargs == {"param2": event_param, "param3": list_param}

        assert cb_with_exception.call_count == 1
        assert cb_with_exception.args == (custom_exception1,)
        assert not cb_with_exception.kwargs

        assert cb_with_return_value.call_count == 1
        assert not cb_with_return_value.args
        assert not cb_with_return_value.kwargs
        assert cb_with_return_value.return_value == return_value

        assert success_callback.call_count == 1
        assert success_callback.args == (return_value,)
        assert not success_callback.kwargs

        assert cb_with_raise_exception.call_count == 1
        assert not cb_with_raise_exception.args
        assert not cb_with_raise_exception.kwargs

        assert failure_callback.call_count == 1
        assert failure_callback.args == (custom_exception1,)
        assert not failure_callback.kwargs

        assert cb_with_args_and_kwargs.call_count == 20

    @abstractmethod
    def test_emission_in_sync_context(self, *args, **kwargs) -> None:
        """
        Performs tests to check if the event emission is working properly within a (SYNC) context.
        """
        pass

    @abstractmethod
    def test_emission_in_sync_context_with_custom_event_linker(self, *args, **kwargs) -> None:
        """
        Performs tests to check if the event emission is working properly within a (SYNC) context
        and using a custom event linker.
        """
        pass

    @abstractmethod
    async def test_emission_in_async_context(self, *args, **kwargs) -> None:
        """
        Performs tests to check if the event emission is working properly within an (ASYNC) context.
        """
        pass

    @abstractmethod
    async def test_emission_in_async_context_with_custom_event_linker(self, *args, **kwargs) -> None:
        """
        Performs tests to check if the event emission is working properly within an (ASYNC) context
        and using a custom event linker.
        """
        pass
