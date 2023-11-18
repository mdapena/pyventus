from _pytest.python_api import raises
from rq import Callback, Queue

from src.pyventus.core.exceptions import PyventusException
from src.pyventus.emitters.rq import RqEventEmitter
from src.pyventus.events import Event
from src.pyventus.linkers import EventLinker


def report_exception():
    TestRqEventEmitter.callback_count += 1


class TestRqEventEmitter:
    # Emulates callback count
    callback_count: int = 0

    # region: Callbacks

    async def callback_with_multi_params(self, *args, **kwargs):
        TestRqEventEmitter.callback_count += 1

    # endregion

    def test_creation(self, clean_event_linker: bool, rq_queue: Queue):
        # Arrange, Act and Assert
        event_emitter = RqEventEmitter(rq_queue=rq_queue)
        assert event_emitter is not None

    def test_creation_with_invalid_params(self, clean_event_linker: bool):
        # Arrange, Act and Assert
        with raises(PyventusException):
            RqEventEmitter(rq_queue=None)

    def test_emit_with_multi_params_callback(self, clean_event_linker: bool, rq_queue: Queue):
        # Arrange
        TestRqEventEmitter.callback_count = 0
        event_emitter = RqEventEmitter(rq_queue=rq_queue, rq_on_failure=Callback(report_exception))
        EventLinker.subscribe('RaiseExceptionInside', callback=self.callback_with_multi_params)
        EventLinker.subscribe(Event, Exception, callback=self.callback_with_multi_params, once=True)
        EventLinker.subscribe('Event', ValueError, callback=self.callback_with_multi_params)
        EventLinker.subscribe(Exception, callback=self.callback_with_multi_params)

        # Act
        event_emitter.emit(ValueError("Value error!"))

        # Assert
        assert TestRqEventEmitter.callback_count == 3

        # Act
        event_emitter.emit(TypeError("Type error!"))

        # Assert
        assert TestRqEventEmitter.callback_count == 4

        # Act
        event_emitter.emit('RaiseExceptionInside')

        # Assert
        assert TestRqEventEmitter.callback_count == 6

        # Act
        event_emitter.emit(Event())

        # Assert
        assert TestRqEventEmitter.callback_count == 7
