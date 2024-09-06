import pytest
from pyventus.reactive import Observable, as_observable
from typing_extensions import Any

from ...fixtures import CallableMock
from ...utils import get_private_attr


class TestAsObservable:
    @pytest.mark.parametrize(
        ["callback", "args", "kwargs"],
        [
            (CallableMock.RandomAll(), (), {}),
            (CallableMock.RandomAll(), ("str", 3.14), {}),
            (CallableMock.RandomAll(), (), {"str": ...}),
            (CallableMock.RandomAll(), ("str", 3.14), {"str": ...}),
        ],
    )
    def test_decorator(self, callback: CallableMock.Base, args: tuple[Any, ...], kwargs: dict[str, Any]) -> None:
        # Arrange: Create a decorated version of the callback using the as_observable decorator.
        decorated_callback = as_observable(callback=callback)

        # Act: Call the decorated callback with the provided arguments and keyword arguments.
        observable: Observable[Any] = decorated_callback(*args, **kwargs)

        # Assert: Verify that the result is an instance of Observable.
        assert isinstance(observable, Observable)

        # Assert: Verify that the original callback is correctly passed to the observable.
        obs_callback = get_private_attr(observable, "__callback")
        assert get_private_attr(obs_callback, "__callable") is callback

        # Assert: Verify that the positional and keyword arguments are correctly passed to the observable.
        assert get_private_attr(observable, "__args") == args
        assert get_private_attr(observable, "__kwargs") == kwargs
