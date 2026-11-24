from collections.abc import Generator, Iterator
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import dataclass
from itertools import chain, product
from typing import Any

import pytest
from pyventus import PyventusException
from pyventus.reactive import Completed, Observable, ObservableTask, ObservableTaskCallbackType

from ....fixtures import CallableMock


class TestObservableTask:
    # =================================
    # Test Cases for creation
    # =================================

    @pytest.mark.parametrize(
        ["callback"],
        [
            pytest.param(CallableMock.Sync()),
            pytest.param(CallableMock.SyncGenerator()),
            pytest.param(CallableMock.Async()),
            pytest.param(CallableMock.AsyncGenerator()),
        ],
    )
    def test_creation_with_valid_input(self, callback: ObservableTaskCallbackType[Any]) -> None:
        # Arrange/Act
        observable_task = ObservableTask[Any](callback=callback)

        # Assert
        assert observable_task is not None
        assert isinstance(observable_task, ObservableTask)

    # =================================

    @pytest.mark.parametrize(
        ["callback", "args", "kwargs", "auto_complete", "exception"],
        [
            pytest.param(None, None, None, True, PyventusException),
            pytest.param(True, None, None, True, PyventusException),
            pytest.param(object, None, None, True, PyventusException),
            pytest.param(object(), None, None, True, PyventusException),
            pytest.param(CallableMock.Sync(), {}, None, True, PyventusException),
            pytest.param(CallableMock.Sync(), True, None, True, PyventusException),
            pytest.param(CallableMock.Sync(), object(), None, True, PyventusException),
            pytest.param(CallableMock.Sync(), None, [], True, PyventusException),
            pytest.param(CallableMock.Sync(), None, True, True, PyventusException),
            pytest.param(CallableMock.Sync(), None, object(), True, PyventusException),
            pytest.param(CallableMock.Sync(), None, None, None, PyventusException),
            pytest.param(CallableMock.Sync(), None, None, [], PyventusException),
            pytest.param(CallableMock.Sync(), None, None, 0, PyventusException),
        ],
    )
    def test_creation_with_invalid_input(
        self, callback: Any, args: Any, kwargs: Any, auto_complete: Any, exception: type[Exception]
    ) -> None:
        # Arrange/Act/Assert
        with pytest.raises(exception):
            ObservableTask(callback=callback, args=args, kwargs=kwargs, auto_complete=auto_complete)

    # =================================
    # Test Cases for execution
    # =================================

    @dataclass
    class ExecutionTestCase:
        id: str
        callback: CallableMock.Base
        args: tuple[Any, ...] | None
        kwargs: dict[str, Any] | None
        auto_complete: bool
        run_in_executor: bool
        use_execution_context: bool

        # =================================
        # Test Cases for next signal
        # =================================

        @classmethod
        def get_next_test_cases(cls) -> Iterator["TestObservableTask.ExecutionTestCase"]:
            for callback, args, kwargs, return_value, auto_complete, run_in_executor, use_execution_context in product(
                (CallableMock.Sync, CallableMock.SyncGenerator, CallableMock.Async, CallableMock.AsyncGenerator),
                (None, ("pi", 3.14, [object()])),
                (None, {"ellipsis": ...}),
                (None, object()),
                (False, True),
                (False, True),
                (False, True),
            ):
                yield cls(
                    id=(
                        f"next-{callback.__name__.lower()}-"
                        f"{'no_args' if args is None else 'with_args'}-"
                        f"{'no_kwargs' if kwargs is None else 'with_kwargs'}-"
                        f"{'no_return_value' if return_value is None else 'with_return_value'}-"
                        f"{'auto_complete' if auto_complete else 'no_auto_complete'}-"
                        f"{'executor' if run_in_executor else 'no_executor'}-"
                        f"{'exec_ctx' if use_execution_context else 'no_exec_ctx'}"
                    ),
                    callback=callback(  # type: ignore[abstract]
                        return_value=return_value,
                        raise_exception=None,
                    ),
                    args=args,
                    kwargs=kwargs,
                    auto_complete=auto_complete,
                    run_in_executor=run_in_executor,
                    use_execution_context=use_execution_context,
                )

        # =================================
        # Test Cases for error signal
        # =================================

        @classmethod
        def get_error_test_cases(cls) -> Iterator["TestObservableTask.ExecutionTestCase"]:
            for callback, run_in_executor, use_execution_context in product(
                (CallableMock.Sync, CallableMock.SyncGenerator, CallableMock.Async, CallableMock.AsyncGenerator),
                (False, True),
                (False, True),
            ):
                yield cls(
                    id=(
                        f"error-{callback.__name__.lower()}-"
                        "with_args-with_kwargs-with_return_value-auto_complete-"
                        f"{'executor' if run_in_executor else 'no_executor'}-"
                        f"{'exec_ctx' if use_execution_context else 'no_exec_ctx'}"
                    ),
                    callback=callback(  # type: ignore[abstract]
                        return_value=object(),
                        raise_exception=Exception(),
                    ),
                    args=("pi", 3.14, []),
                    kwargs={"ellipsis": ...},
                    auto_complete=True,
                    run_in_executor=run_in_executor,
                    use_execution_context=use_execution_context,
                )

        # =================================
        # Test Cases for complete signal
        # =================================

        @classmethod
        def get_complete_test_cases(cls) -> Iterator["TestObservableTask.ExecutionTestCase"]:
            for callback, run_in_executor, use_execution_context in product(
                (CallableMock.Sync, CallableMock.SyncGenerator, CallableMock.Async, CallableMock.AsyncGenerator),
                (False, True),
                (False, True),
            ):
                yield cls(
                    id=(
                        f"complete-{callback.__name__.lower()}-"
                        "with_args-with_kwargs-with_return_value-auto_complete-"
                        f"{'executor' if run_in_executor else 'no_executor'}-"
                        f"{'exec_ctx' if use_execution_context else 'no_exec_ctx'}"
                    ),
                    callback=callback(  # type: ignore[abstract]
                        return_value=object(),
                        raise_exception=Completed,
                    ),
                    args=("pi", 3.14, []),
                    kwargs={"ellipsis": ...},
                    auto_complete=True,
                    run_in_executor=run_in_executor,
                    use_execution_context=use_execution_context,
                )

    # =================================

    @contextmanager
    def _test_execution(self, tc: ExecutionTestCase) -> Generator[ObservableTask[Any], None, None]:
        """
        Context manager for testing the execution of an observable task.

        Usage:
        ```Python
        with self.execution_test(tc) as obs:
            # Wait for all events to propagate
        ```

        :param tc: An instance of ExecutionTestCase that contains the configuration for the test.
        :return: A generator object that yields the current observable task being tested.
        """
        # Arrange: Set up mock callbacks for testing.
        next_callback = CallableMock.Async()
        error_callback = CallableMock.Async()
        complete_callback = CallableMock.Sync()

        # Arrange: Create an instance of ObservableTask with the specified callback and arguments.
        observable_task = ObservableTask[Any](
            callback=tc.callback, args=tc.args, kwargs=tc.kwargs, auto_complete=tc.auto_complete
        )

        # Act: Subscribe to the observable task and
        # execute it based on the test configuration.
        if tc.run_in_executor:
            executor = ThreadPoolExecutor()

            if tc.use_execution_context:
                with observable_task.to_thread(executor) as obs:
                    obs.subscribe(
                        next_callback=next_callback,
                        error_callback=error_callback,
                        complete_callback=complete_callback,
                    )
            else:
                observable_task.subscribe(
                    next_callback=next_callback,
                    error_callback=error_callback,
                    complete_callback=complete_callback,
                )
                observable_task(executor)

            executor.shutdown()
        else:
            if tc.use_execution_context:
                with observable_task as obs:
                    obs.subscribe(
                        next_callback=next_callback,
                        error_callback=error_callback,
                        complete_callback=complete_callback,
                    )
            else:
                observable_task.subscribe(
                    next_callback=next_callback,
                    error_callback=error_callback,
                    complete_callback=complete_callback,
                )
                observable_task()

        # Yield the current observable_task and
        # wait for all callables to complete.
        yield observable_task

        # Assert: Verify that the main callback was executed correctly.
        assert tc.callback.call_count == 1
        assert tc.callback.last_args == (tc.args if tc.args is not None else ())
        assert tc.callback.last_kwargs == (tc.kwargs if tc.kwargs is not None else {})

        # Assert: Verify subscriber notifications.
        if tc.callback.exception is not None:
            assert next_callback.call_count == 0
            assert next_callback.last_args == ()
            assert next_callback.last_kwargs == {}

            if isinstance(tc.callback.exception, Observable.Completed):
                assert error_callback.call_count == 0
                assert error_callback.last_args == ()
                assert error_callback.last_kwargs == {}

                assert complete_callback.call_count == 1
                assert complete_callback.last_args == ()
                assert complete_callback.last_kwargs == {}
            else:
                assert complete_callback.call_count == 0
                assert complete_callback.last_args == ()
                assert complete_callback.last_kwargs == {}

                assert error_callback.call_count == 1
                assert error_callback.last_args == (tc.callback.exception,)
                assert error_callback.last_kwargs == {}
        else:
            assert next_callback.call_count == 1
            assert next_callback.last_args == (tc.callback.return_value,)
            assert next_callback.last_kwargs == {}

            assert error_callback.call_count == 0
            assert error_callback.last_args == ()
            assert error_callback.last_kwargs == {}

            assert complete_callback.call_count == (1 if tc.auto_complete else 0)
            assert complete_callback.last_args == ()
            assert complete_callback.last_kwargs == {}

    # =================================

    @pytest.mark.parametrize(
        ["tc"],
        [
            pytest.param(tc, id=tc.id)
            for tc in chain(
                ExecutionTestCase.get_next_test_cases(),
                ExecutionTestCase.get_error_test_cases(),
                ExecutionTestCase.get_complete_test_cases(),
            )
        ],
    )
    def test_execution_in_sync_context(self, tc: ExecutionTestCase) -> None:
        with self._test_execution(tc):
            pass

    # =================================

    @pytest.mark.parametrize(
        ["tc"],
        [
            pytest.param(tc, id=tc.id)
            for tc in chain(
                ExecutionTestCase.get_next_test_cases(),
                ExecutionTestCase.get_error_test_cases(),
                ExecutionTestCase.get_complete_test_cases(),
            )
        ],
    )
    async def test_execution_in_async_context(self, tc: ExecutionTestCase) -> None:
        with self._test_execution(tc) as obs:
            await obs.wait_for_tasks()

    # =================================

    def test_execution_with_invalid_input(self) -> None:
        # Arrange
        observable_task = ObservableTask[Any](callback=lambda: object())

        # Act/Assert
        with pytest.raises(PyventusException):
            observable_task(executor=ProcessPoolExecutor())  # type: ignore[arg-type]

    # =================================
    # Test Cases for to_thread()
    # =================================

    def test_to_thread_with_default_executor(self) -> None:
        # Arrange
        callback = CallableMock.Sync()
        observable_task = ObservableTask[Any](callback=callback)

        # Act
        with observable_task.to_thread():
            pass

        # Assert
        assert callback.call_count == 1
        assert callback.last_args == ()
        assert callback.last_kwargs == {}

    # =================================

    @pytest.mark.parametrize(
        ["shutdown"],
        [
            pytest.param(True),
            pytest.param(False),
        ],
    )
    def test_to_thread_with_shutdown_argument(self, shutdown: bool) -> None:
        # Arrange
        executor = ThreadPoolExecutor()
        observable_task = ObservableTask[Any](callback=CallableMock.Sync())

        # Act
        with observable_task.to_thread(executor=executor, shutdown=shutdown):
            pass

        # Assert
        assert executor._shutdown is shutdown
        executor.shutdown()
