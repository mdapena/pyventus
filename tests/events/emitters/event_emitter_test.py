from abc import ABC, abstractmethod
from collections.abc import Generator
from contextlib import contextmanager
from typing import Generic, TypeVar

import pytest
from pyventus import PyventusException
from pyventus.events import EventEmitter, EventLinker

from ...fixtures import CallableMock, EventFixtures

_E = TypeVar("_E", bound=EventEmitter)


class EventEmitterTest(Generic[_E], ABC):
    """A set of pre-configured tests for subclasses of EventEmitter."""

    @abstractmethod
    def _create_event_emitter(self, event_linker: type[EventLinker]) -> _E:
        pass

    # =================================

    @contextmanager
    def run_emissions_test(self, event_linker: type[EventLinker]) -> Generator[_E, None, None]:
        """
        Context manager for performing tests to check if the event emission is working
        properly using both synchronous and asynchronous callbacks.

        The `run_emissions_test` function is a context manager that allows you to perform tests
        on event emission behavior. When used with a `with` statement, you should complete the
        necessary actions to propagate the events that were linked and emitted within the
        `run_emissions_test` function before the yield statement. These actions might include
        triggering events, calling relevant functions, or waiting for event propagation to
        complete.

        After the execution of the code section inside the `with` statement, the control is
        returned to the `run_emissions_test` function. At this point, the function can proceed
        to perform the assertions to validate the expected behavior of the callbacks.

        Usage:
        ```Python
        with EventEmitterTest.emission_test(event_emitter):
            # Wait for all events to propagate
        ```

        :param event_linker: The event linker class to be used for linking events and
            callbacks. Defaults to EventLinker.
        :return: A generator object for the test.
        """
        # =================================
        # Arrange: Parameters
        # =================================

        int_param: int = 2
        str_param: str = "str"
        dtc_param: object = EventFixtures.EmptyDtc()
        list_param: list[int] = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        dict_param: dict[str, str] = {"key": "value"}
        dtc_immutable = EventFixtures.DtcImmutable(attr1="str", attr2=("1", "2", "3"))
        dtc_mutable = EventFixtures.DtcMutable(attr1=["1", "2", "3"], attr2={"key": "value"})
        dtc_with_val = EventFixtures.DtcWithVal(attr1="str", attr2=7.65)
        custom_exc1: Exception = EventFixtures.CustomExc()
        custom_exc2: Exception = KeyError()

        return_value: object = EventFixtures.EmptyDtc()
        raise_exception: Exception = EventFixtures.CustomExc()

        # =================================
        # Arrange: Callbacks
        # =================================

        cb_without_params: CallableMock.Base = CallableMock.Random()
        cb_with_two_params: CallableMock.Base = CallableMock.Random()

        cb_with_args: CallableMock.Base = CallableMock.Random()
        cb_with_kwargs: CallableMock.Base = CallableMock.Random()
        cb_with_args_and_kwargs: CallableMock.Base = CallableMock.Random()

        cb_with_dtc_immutable: CallableMock.Base = CallableMock.Random()
        cb_with_dtc_mutable_and_extras: CallableMock.Base = CallableMock.Random()
        cb_with_dtc_validated: CallableMock.Base = CallableMock.Random()
        cb_with_dtc: CallableMock.Base = CallableMock.Random()

        cb_with_custom_exc1: CallableMock.Base = CallableMock.Random()
        cb_with_custom_exc2: CallableMock.Base = CallableMock.Random()
        cb_with_exc: CallableMock.Base = CallableMock.Random()

        cb_with_return_value: CallableMock.Base = CallableMock.Random(return_value=return_value)
        cb_with_raise_exception: CallableMock.Base = CallableMock.Random(raise_exception=raise_exception)

        cb_success: CallableMock.Base = CallableMock.Random()
        cb_failure: CallableMock.Base = CallableMock.Random()

        # =================================
        # Arrange: Create a dummy event linker
        # =================================

        class DummyEventLinker(EventLinker, max_subscribers=1): ...

        # =================================
        # Arrange: EventLinker
        # =================================

        # Clear event linker
        event_linker.remove_all()

        # String Events
        event_linker.subscribe("WithoutParams", "Another", event_callback=cb_without_params, once=True)
        event_linker.subscribe("WithTwoParams", event_callback=cb_with_two_params, force_async=True)
        event_linker.subscribe("WithKwargs", event_callback=cb_with_kwargs, once=True)
        event_linker.subscribe("WithArgs", event_callback=cb_with_args)

        # Dataclass Events
        event_linker.subscribe(EventFixtures.DtcImmutable, event_callback=cb_with_dtc_immutable)
        event_linker.subscribe(EventFixtures.DtcMutable, event_callback=cb_with_dtc_mutable_and_extras)
        event_linker.subscribe(EventFixtures.DtcWithVal, event_callback=cb_with_dtc_validated)
        event_linker.subscribe(EventFixtures.DtcImmutable, EventFixtures.DtcWithVal, event_callback=cb_with_dtc)

        # Exception Events
        event_linker.subscribe(EventFixtures.CustomExc, event_callback=cb_with_custom_exc1)
        event_linker.subscribe(type(custom_exc2), event_callback=cb_with_custom_exc2)
        event_linker.subscribe(TypeError, EventFixtures.CustomExc, event_callback=cb_with_exc, once=True)

        # Test success callback execution
        with event_linker.once("WithSuccessCallback") as ctx:
            ctx.on_event(cb_with_return_value)
            ctx.on_success(cb_success)
            ctx.on_failure(cb_failure)

        # Test failure callback execution
        with event_linker.on("WithFailureCallback", force_async=True) as ctx:
            ctx.on_event(cb_with_raise_exception)
            ctx.on_success(cb_success)
            ctx.on_failure(cb_failure)

        # Test Error Handling
        with event_linker.on("ErrorHandling") as ctx:
            ctx.on_event(CallableMock.Random())
            ctx.on_success(CallableMock.Random(raise_exception=EventFixtures.CustomExc()))
            ctx.on_failure(cb_failure)

        with event_linker.on("ErrorHandling") as ctx:
            ctx.on_event(CallableMock.Random(raise_exception=EventFixtures.CustomExc()))
            ctx.on_success(cb_success)
            ctx.on_failure(CallableMock.Random(raise_exception=EventFixtures.CustomExc()))

        # Any Event
        event_linker.subscribe(..., event_callback=cb_with_args_and_kwargs)

        # Different namespace
        DummyEventLinker.subscribe(..., event_callback=cb_with_args_and_kwargs)

        # =================================
        # Arrange: Create event emitter
        # =================================

        # Create event emitter
        event_emitter: _E = self._create_event_emitter(event_linker)

        # =================================
        # Act: Emit string events
        # =================================

        event_emitter.emit("Another")
        event_emitter.emit("WithoutParams")  # Has no subscribers
        event_emitter.emit("WithTwoParams", dict_param, param2=dtc_param)
        event_emitter.emit("WithKwargs", param1=int_param, param2=str_param, param3=list_param)
        event_emitter.emit("WithKwargs", param1=int_param, param2=str_param, param3=list_param)  # Has no subscribers
        event_emitter.emit("WithArgs", int_param, str_param, dict_param)
        event_emitter.emit("Invalid", int_param, dict_param)  # Is not registered

        # Try to emit invalid string event
        with pytest.raises(PyventusException):
            event_emitter.emit("")

        # =================================
        # Act: Emit dataclass events
        # =================================

        event_emitter.emit(dtc_immutable)
        event_emitter.emit(dtc_mutable, int_param, str_param, param3=dtc_param, param4=list_param)
        event_emitter.emit(EventFixtures.EmptyDtc())  # Has no subscribers
        event_emitter.emit(dtc_with_val)

        # Try to emit invalid dataclass events
        with pytest.raises(PyventusException):
            event_emitter.emit(None)
        with pytest.raises(PyventusException):
            event_emitter.emit(EventFixtures.EmptyDtc)
        with pytest.raises(PyventusException):  # `attr1` must be at least 3 characters, it is not emitted
            event_emitter.emit(EventFixtures.DtcWithVal(attr1="at", attr2=2.3))

        # =================================
        # Act: Emit exception events
        # =================================

        event_emitter.emit(custom_exc1)
        event_emitter.emit(custom_exc2, int_param, str_param, param2=dtc_param, param3=list_param)
        event_emitter.emit(Exception())

        try:
            EventFixtures.DtcWithVal(attr1="at", attr2=7)
        except PyventusException as e:
            event_emitter.emit(e)

        # Try to emit invalid exception events
        with pytest.raises(PyventusException):
            event_emitter.emit(Exception)

        # =================================
        # Act: Emit events with success and error handling
        # =================================

        event_emitter.emit("WithSuccessCallback")
        event_emitter.emit("WithSuccessCallback")  # Has no subscribers
        event_emitter.emit("WithFailureCallback")
        event_emitter.emit("ErrorHandling")

        # =================================
        # Act: Emit any event
        # =================================

        event_emitter.emit(..., dtc_immutable, mutable=dtc_mutable)

        # =================================
        # Act: Remove the Ellipsis event and emit unregistered ones
        # =================================

        event_linker.remove_event(...)

        event_emitter.emit("str")
        event_emitter.emit(...)

        # =================================
        # Act: Wait for all events to propagate
        # =================================

        yield event_emitter

        # =================================
        # Assert
        # =================================

        assert cb_without_params.call_count == 1
        assert cb_without_params.last_args == ()
        assert cb_without_params.last_kwargs == {}

        assert cb_with_two_params.call_count == 1
        assert cb_with_two_params.last_args == (dict_param,)
        assert cb_with_two_params.last_kwargs == {"param2": dtc_param}

        assert cb_with_args.call_count == 1
        assert cb_with_args.last_args == (int_param, str_param, dict_param)
        assert cb_with_args.last_kwargs == {}

        assert cb_with_kwargs.call_count == 1
        assert cb_with_kwargs.last_args == ()
        assert cb_with_kwargs.last_kwargs == {"param1": int_param, "param2": str_param, "param3": list_param}

        # Assert call count only, as last args and kwargs can be in any order
        assert cb_with_args_and_kwargs.call_count == 20

        assert cb_with_dtc_immutable.call_count == 1
        assert cb_with_dtc_immutable.last_args == (dtc_immutable,)
        assert cb_with_dtc_immutable.last_kwargs == {}

        assert cb_with_dtc_mutable_and_extras.call_count == 1
        assert cb_with_dtc_mutable_and_extras.last_args == (dtc_mutable, int_param, str_param)
        assert cb_with_dtc_mutable_and_extras.last_kwargs == {"param3": dtc_param, "param4": list_param}

        assert cb_with_dtc_validated.call_count == 1
        assert cb_with_dtc_validated.last_args == (dtc_with_val,)
        assert cb_with_dtc_validated.last_kwargs == {}

        # Assert call count only, as last args and kwargs can be in any order
        assert cb_with_dtc.call_count == 2

        assert cb_with_custom_exc1.call_count == 1
        assert cb_with_custom_exc1.last_args == (custom_exc1,)
        assert cb_with_custom_exc1.last_kwargs == {}

        assert cb_with_custom_exc2.call_count == 1
        assert cb_with_custom_exc2.last_args == (custom_exc2, int_param, str_param)
        assert cb_with_custom_exc2.last_kwargs == {"param2": dtc_param, "param3": list_param}

        assert cb_with_exc.call_count == 1
        assert cb_with_exc.last_args == (custom_exc1,)
        assert cb_with_exc.last_kwargs == {}

        assert cb_with_return_value.call_count == 1
        assert cb_with_return_value.last_args == ()
        assert cb_with_return_value.last_kwargs == {}

        assert cb_success.call_count == 1
        assert cb_success.last_args == (cb_with_return_value.return_value,)
        assert cb_success.last_kwargs == {}

        assert cb_with_raise_exception.call_count == 1
        assert cb_with_raise_exception.last_args == ()
        assert cb_with_raise_exception.last_kwargs == {}

        assert cb_failure.call_count == 1
        assert cb_failure.last_args == (cb_with_raise_exception.exception,)
        assert cb_failure.last_kwargs == {}

    # =================================

    @abstractmethod
    def test_emission_in_sync_context(self) -> None:
        """Performs tests to check if the event emission is working properly within a (SYNC) context."""
        pass

    # =================================

    @abstractmethod
    def test_emission_in_sync_context_with_custom_event_linker(self) -> None:
        """
        Performs tests to check if the event emission is working properly within a (SYNC) context
        and using a custom event linker.
        """
        pass

    # =================================

    @abstractmethod
    async def test_emission_in_async_context(self) -> None:
        """Performs tests to check if the event emission is working properly within an (ASYNC) context."""
        pass

    # =================================

    @abstractmethod
    async def test_emission_in_async_context_with_custom_event_linker(self) -> None:
        """
        Performs tests to check if the event emission is working properly within an (ASYNC) context
        and using a custom event linker.
        """
        pass
