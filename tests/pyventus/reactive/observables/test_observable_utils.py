import pytest
from pyventus.reactive import ObservableTask, as_observable_task
from typing_extensions import Any

from ....fixtures import CallableMock
from ....utils import get_private_attr


class TestObservableUtils:
    # =================================
    # Test Cases for as_observable_task()
    # =================================

    @pytest.mark.parametrize(
        ["callback", "args", "kwargs"],
        [
            (CallableMock.Sync(), (), {}),
            (CallableMock.SyncGenerator(), ("pi", 3.14), {}),
            (CallableMock.Async(), (), {"...": ...}),
            (CallableMock.AsyncGenerator(), ("pi", 3.14), {"...": ...}),
        ],
    )
    def test_as_observable_task_decorator(
        self, callback: CallableMock.Base, args: tuple[Any, ...], kwargs: dict[str, Any]
    ) -> None:
        # Arrange
        decorated_callback = as_observable_task(callback)

        # Act
        observable_task: ObservableTask[Any] = decorated_callback(*args, **kwargs)
        observable_task_callback = get_private_attr(observable_task, "__callback")

        # Assert
        assert callable(decorated_callback)
        assert isinstance(observable_task, ObservableTask)
        assert get_private_attr(observable_task_callback, "__callable") is callback
        assert get_private_attr(observable_task, "__args") == args
        assert get_private_attr(observable_task, "__kwargs") == kwargs

    # =================================

    @pytest.mark.parametrize(
        ["debug"],
        [(False,), (True,)],
    )
    def test_as_observable_task_decorator_with_parameters(self, debug: bool) -> None:
        # Arrange
        callback = CallableMock.Sync()
        decorated_callback = as_observable_task(debug=debug)(callback)

        # Act
        observable_task = decorated_callback()

        # Assert
        assert isinstance(observable_task, ObservableTask)
        assert getattr(observable_task, "_Observable__logger").debug_enabled is debug  # noqa: B009
