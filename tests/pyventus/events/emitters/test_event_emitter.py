from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from types import EllipsisType
from typing import Any

import pytest
from pyventus import PyventusException
from pyventus.core.processing import ProcessingService
from pyventus.core.processing.asyncio import AsyncIOProcessingService
from pyventus.events import EmittableEventType, EventEmitter, EventLinker, SubscribableEventType

from ....fixtures import CallableMock, EventFixtures


class TestEventEmitter:
    class CustomEventLinker(EventLinker): ...

    # =================================
    # Test Cases for creation
    # =================================

    @pytest.mark.parametrize(
        ["event_processor", "event_linker", "debug"],
        [
            (AsyncIOProcessingService(), EventLinker, None),
            (AsyncIOProcessingService(), CustomEventLinker, None),
            (AsyncIOProcessingService(), CustomEventLinker, False),
        ],
    )
    def test_creation_with_valid_input(
        self, event_processor: ProcessingService, event_linker: type[EventLinker], debug: bool
    ) -> None:
        # Arrange/Act
        event_emitter = EventEmitter(event_processor=event_processor, event_linker=event_linker, debug=debug)

        # Assert
        assert event_emitter is not None
        assert isinstance(event_emitter, EventEmitter)

    # =================================

    @pytest.mark.parametrize(
        ["event_processor", "event_linker", "debug", "exception"],
        [
            (None, EventLinker, False, PyventusException),
            (True, EventLinker, False, PyventusException),
            (object(), EventLinker, False, PyventusException),
            (AsyncIOProcessingService, EventLinker, False, PyventusException),
            (AsyncIOProcessingService(), None, False, PyventusException),
            (AsyncIOProcessingService(), object, False, PyventusException),
            (AsyncIOProcessingService(), EventLinker, "False", PyventusException),
        ],
    )
    def test_creation_with_invalid_input(
        self,
        event_processor: ProcessingService,
        event_linker: type[EventLinker],
        debug: bool,
        exception: type[Exception],
    ) -> None:
        # Arrange/Act/Assert
        with pytest.raises(PyventusException):
            EventEmitter(event_processor=event_processor, event_linker=event_linker, debug=debug)

    # =================================
    # Test Cases for event emission
    # =================================

    # Define a dataclass for better readability of test cases
    @dataclass
    class EmissionTestCase:
        subscription_event: SubscribableEventType
        subscription_callback: CallableMock.Base
        # =============================
        emission_event: EmittableEventType
        emission_args: tuple[Any, ...]
        emission_kwargs: dict[str, Any]

    # =================================

    @pytest.mark.parametrize(
        ["tc"],
        [
            # Test cases with Ellipsis (...)
            # =================================
            (
                EmissionTestCase(
                    subscription_event=...,
                    subscription_callback=CallableMock.Sync(),
                    # =========================
                    emission_event=...,
                    emission_args=(),
                    emission_kwargs={},
                ),
            ),
            (
                EmissionTestCase(
                    subscription_event=...,
                    subscription_callback=CallableMock.Async(),
                    # =========================
                    emission_event=...,
                    emission_args=("str", 0, [object()]),
                    emission_kwargs={},
                ),
            ),
            (
                EmissionTestCase(
                    subscription_event=...,
                    subscription_callback=CallableMock.Sync(),
                    # =========================
                    emission_event=...,
                    emission_args=(),
                    emission_kwargs={"ellipsis": ..., "str": 0},
                ),
            ),
            (
                EmissionTestCase(
                    subscription_event=...,
                    subscription_callback=CallableMock.Async(),
                    # =========================
                    emission_event=...,
                    emission_args=("str", 0, [object()]),
                    emission_kwargs={"ellipsis": ..., "str": 0},
                ),
            ),
            # Test cases with Strings
            # =================================
            (
                EmissionTestCase(
                    subscription_event="StrEvent",
                    subscription_callback=CallableMock.Async(),
                    # =========================
                    emission_event="StrEvent",
                    emission_args=(),
                    emission_kwargs={},
                ),
            ),
            (
                EmissionTestCase(
                    subscription_event="StrEvent",
                    subscription_callback=CallableMock.Sync(),
                    # =========================
                    emission_event="StrEvent",
                    emission_args=("str", 0, [object()]),
                    emission_kwargs={},
                ),
            ),
            (
                EmissionTestCase(
                    subscription_event="StrEvent",
                    subscription_callback=CallableMock.Async(),
                    # =========================
                    emission_event="StrEvent",
                    emission_args=(),
                    emission_kwargs={"ellipsis": ..., "str": 0},
                ),
            ),
            (
                EmissionTestCase(
                    subscription_event="StrEvent",
                    subscription_callback=CallableMock.Sync(),
                    # =========================
                    emission_event="StrEvent",
                    emission_args=("str", 0, [object()]),
                    emission_kwargs={"ellipsis": ..., "str": 0},
                ),
            ),
            # Test cases with dataclass objets
            # =================================
            (
                EmissionTestCase(
                    subscription_event=EventFixtures.DtcImmutable,
                    subscription_callback=CallableMock.Sync(),
                    # =========================
                    emission_event=EventFixtures.DtcImmutable(attr1="str", attr2=("0", "1")),
                    emission_args=(),
                    emission_kwargs={},
                ),
            ),
            (
                EmissionTestCase(
                    subscription_event=EventFixtures.DtcImmutable,
                    subscription_callback=CallableMock.Async(),
                    # =========================
                    emission_event=EventFixtures.DtcImmutable(attr1="str", attr2=("0", "1")),
                    emission_args=("str", 0, [object()]),
                    emission_kwargs={},
                ),
            ),
            (
                EmissionTestCase(
                    subscription_event=EventFixtures.DtcImmutable,
                    subscription_callback=CallableMock.Sync(),
                    # =========================
                    emission_event=EventFixtures.DtcImmutable(attr1="str", attr2=("0", "1")),
                    emission_args=(),
                    emission_kwargs={"ellipsis": ..., "str": 0},
                ),
            ),
            (
                EmissionTestCase(
                    subscription_event=EventFixtures.DtcImmutable,
                    subscription_callback=CallableMock.Async(),
                    # =========================
                    emission_event=EventFixtures.DtcImmutable(attr1="str", attr2=("0", "1")),
                    emission_args=("str", 0, [object()]),
                    emission_kwargs={"ellipsis": ..., "str": 0},
                ),
            ),
            # Test cases with exception objets
            # =================================
            (
                EmissionTestCase(
                    subscription_event=EventFixtures.CustomExc,
                    subscription_callback=CallableMock.Async(),
                    # =========================
                    emission_event=EventFixtures.CustomExc(),
                    emission_args=(),
                    emission_kwargs={},
                ),
            ),
            (
                EmissionTestCase(
                    subscription_event=EventFixtures.CustomExc,
                    subscription_callback=CallableMock.Sync(),
                    # =========================
                    emission_event=EventFixtures.CustomExc(),
                    emission_args=("str", 0, [object()]),
                    emission_kwargs={},
                ),
            ),
            (
                EmissionTestCase(
                    subscription_event=EventFixtures.CustomExc,
                    subscription_callback=CallableMock.Async(),
                    # =========================
                    emission_event=EventFixtures.CustomExc(),
                    emission_args=(),
                    emission_kwargs={"ellipsis": ..., "str": 0},
                ),
            ),
            (
                EmissionTestCase(
                    subscription_event=EventFixtures.CustomExc,
                    subscription_callback=CallableMock.Sync(),
                    # =========================
                    emission_event=EventFixtures.CustomExc(),
                    emission_args=("str", 0, [object()]),
                    emission_kwargs={"ellipsis": ..., "str": 0},
                ),
            ),
        ],
    )
    def test_emit_with_valid_input(self, tc: EmissionTestCase) -> None:
        # Arrange
        class IsolatedEventLinker(EventLinker): ...

        IsolatedEventLinker.subscribe(tc.subscription_event, event_callback=tc.subscription_callback)
        event_emitter = EventEmitter(event_processor=AsyncIOProcessingService(), event_linker=IsolatedEventLinker)

        # Act
        event_emitter.emit(tc.emission_event, *tc.emission_args, **tc.emission_kwargs)

        # Assert
        assert tc.subscription_callback.call_count == 1
        assert tc.subscription_callback.last_kwargs == tc.emission_kwargs
        assert tc.subscription_callback.last_args == (
            tc.emission_args
            if isinstance(tc.emission_event, str | EllipsisType)
            else (tc.emission_event, *tc.emission_args)
        )

    # =================================

    @pytest.mark.parametrize(
        ["tc", "exception"],
        [
            (
                EmissionTestCase(
                    subscription_event=EventFixtures.DtcImmutable,
                    subscription_callback=CallableMock.Sync(),
                    # =========================
                    emission_event=None,
                    emission_args=(),
                    emission_kwargs={},
                ),
                PyventusException,
            ),
            (
                EmissionTestCase(
                    subscription_event=EventFixtures.DtcImmutable,
                    subscription_callback=CallableMock.Sync(),
                    # =========================
                    emission_event=EventFixtures.DtcImmutable,
                    emission_args=(),
                    emission_kwargs={},
                ),
                PyventusException,
            ),
            (
                EmissionTestCase(
                    subscription_event="StrEvent",
                    subscription_callback=CallableMock.Sync(),
                    # =========================
                    emission_event="",
                    emission_args=(),
                    emission_kwargs={},
                ),
                PyventusException,
            ),
        ],
    )
    def test_emit_with_invalid_input(self, tc: EmissionTestCase, exception: type[Exception]) -> None:
        # Arrange
        class IsolatedEventLinker(EventLinker): ...

        IsolatedEventLinker.subscribe(tc.subscription_event, event_callback=tc.subscription_callback)
        event_emitter = EventEmitter(event_processor=AsyncIOProcessingService(), event_linker=IsolatedEventLinker)

        # Act/Assert
        with pytest.raises(exception):
            event_emitter.emit(tc.emission_event, *tc.emission_args, **tc.emission_kwargs)

    @contextmanager
    def event_emission_test(
        self, event_processor: ProcessingService, event_linker: type[EventLinker]
    ) -> Generator[None, None, None]:
        """
        Context manager for performing tests to check if the event emission is working properly using
        both synchronous and asynchronous callbacks.

        The `event_emission_test` function is a context manager that allows you to perform tests
        on event emission behavior. When used with a `with` statement, you should complete the necessary
        actions to propagate the events that were linked and emitted within the `event_emission_test`
        function before the yield statement. These actions might include triggering events, calling
        relevant functions, or waiting for event propagation to complete.

        After the execution of the code section inside the `with` statement, the control is returned to
        the `event_emission_test` function. At this point, the function can proceed to perform
        the assertions to validate the expected behavior of the callbacks.

        Usage:
        ```Python
        with self.event_emission_test(event_processor, event_linker):
            # Wait for all events to propagate
        ```

        :param event_processor: The processing service object used to handle the event propagation.
        :param event_linker: The event linker class used to link events and callbacks.
        :return: A generator object.
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

        cb_without_params: CallableMock.Base = CallableMock.Sync()
        cb_with_two_params: CallableMock.Base = CallableMock.Async()

        cb_with_args: CallableMock.Base = CallableMock.Sync()
        cb_with_kwargs: CallableMock.Base = CallableMock.Async()
        cb_with_args_and_kwargs: CallableMock.Base = CallableMock.Sync()

        cb_with_dtc_immutable: CallableMock.Base = CallableMock.Async()
        cb_with_dtc_mutable_and_extras: CallableMock.Base = CallableMock.Sync()
        cb_with_dtc_validated: CallableMock.Base = CallableMock.Async()
        cb_with_dtc: CallableMock.Base = CallableMock.Sync()

        cb_with_custom_exc1: CallableMock.Base = CallableMock.Async()
        cb_with_custom_exc2: CallableMock.Base = CallableMock.Sync()
        cb_with_exc: CallableMock.Base = CallableMock.Async()

        cb_with_return_value: CallableMock.Base = CallableMock.Sync(return_value=return_value)
        cb_with_raise_exception: CallableMock.Base = CallableMock.Async(raise_exception=raise_exception)

        cb_success: CallableMock.Base = CallableMock.Async()
        cb_failure: CallableMock.Base = CallableMock.Sync()

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
            ctx.on_event(CallableMock.Async())
            ctx.on_success(CallableMock.Sync(raise_exception=EventFixtures.CustomExc()))
            ctx.on_failure(cb_failure)

        with event_linker.on("ErrorHandling") as ctx:
            ctx.on_event(CallableMock.Async(raise_exception=EventFixtures.CustomExc()))
            ctx.on_success(cb_success)
            ctx.on_failure(CallableMock.Sync(raise_exception=EventFixtures.CustomExc()))

        # Any Event
        event_linker.subscribe(..., event_callback=cb_with_args_and_kwargs)

        # Different namespace
        DummyEventLinker.subscribe(..., event_callback=cb_with_args_and_kwargs)

        # =================================
        # Arrange: Create event emitter
        # =================================

        # Create event emitter
        event_emitter: EventEmitter = EventEmitter(event_processor=event_processor, event_linker=event_linker)

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

        # =================================
        # Act: Emit dataclass events
        # =================================

        event_emitter.emit(dtc_immutable)
        event_emitter.emit(dtc_mutable, int_param, str_param, param3=dtc_param, param4=list_param)
        event_emitter.emit(EventFixtures.EmptyDtc())  # Has no subscribers
        event_emitter.emit(dtc_with_val)

        # Try to emit invalid dataclass events
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

        yield

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

    def test_event_emission_in_sync_context(self) -> None:
        # Arrange
        class IsolatedEventLinker(EventLinker): ...

        event_processor = AsyncIOProcessingService()

        # Act/Assert
        with self.event_emission_test(event_processor, IsolatedEventLinker):
            pass

    async def test_event_emission_in_async_context(self) -> None:
        # Arrange
        class IsolatedEventLinker(EventLinker): ...

        event_processor = AsyncIOProcessingService()

        # Act/Assert
        with self.event_emission_test(event_processor, IsolatedEventLinker):
            await event_processor.wait_for_tasks()
