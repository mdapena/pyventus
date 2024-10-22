from collections.abc import Generator
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import dataclass
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
            (CallableMock.Sync(),),
            (CallableMock.SyncGenerator(),),
            (CallableMock.Async(),),
            (CallableMock.AsyncGenerator(),),
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
        ["callback", "args", "kwargs", "exception"],
        [
            (None, None, None, PyventusException),
            (True, None, None, PyventusException),
            (object, None, None, PyventusException),
            (object(), None, None, PyventusException),
            (CallableMock.Sync(), True, None, PyventusException),
            (CallableMock.Sync(), object(), None, PyventusException),
            (CallableMock.Sync(), None, True, PyventusException),
            (CallableMock.Sync(), None, object(), PyventusException),
        ],
    )
    def test_creation_with_invalid_input(
        self, callback: Any, args: Any, kwargs: Any, exception: type[Exception]
    ) -> None:
        # Arrange/Act/Assert
        with pytest.raises(exception):
            ObservableTask(callback=callback, args=args, kwargs=kwargs)

    # =================================
    # Test Cases for execution
    # =================================

    # Define a dataclass for better readability of test cases
    @dataclass
    class ExecutionTestCase:
        callback: type[CallableMock.Base]
        args: tuple[Any, ...] | None
        kwargs: dict[str, Any] | None
        return_value: Any
        raise_exception: Exception | None
        # =============================
        run_in_executor: bool
        use_execution_context: bool

    # =================================

    EXECUTION_TEST_CASES = [
        # Test cases with Sync callback
        # =================================
        (
            ExecutionTestCase(
                callback=CallableMock.Sync,
                args=None,
                kwargs=None,
                return_value=object(),
                raise_exception=None,
                # =========================
                run_in_executor=False,
                use_execution_context=False,
            ),
        ),
        (
            ExecutionTestCase(
                callback=CallableMock.Sync,
                args=None,
                kwargs=None,
                return_value=object(),
                raise_exception=Completed,
                # =========================
                run_in_executor=False,
                use_execution_context=False,
            ),
        ),
        (
            ExecutionTestCase(
                callback=CallableMock.Sync,
                args=None,
                kwargs=None,
                return_value=object(),
                raise_exception=Exception(),
                # =========================
                run_in_executor=False,
                use_execution_context=False,
            ),
        ),
        (
            ExecutionTestCase(
                callback=CallableMock.Sync,
                args=("str", 0, [object()]),
                kwargs={"ellipsis": ...},
                return_value=object(),
                raise_exception=None,
                # =========================
                run_in_executor=False,
                use_execution_context=False,
            ),
        ),
        (
            ExecutionTestCase(
                callback=CallableMock.Sync,
                args=("str", 0, [object()]),
                kwargs={"ellipsis": ...},
                return_value=object(),
                raise_exception=Completed,
                # =========================
                run_in_executor=False,
                use_execution_context=False,
            ),
        ),
        (
            ExecutionTestCase(
                callback=CallableMock.Sync,
                args=("str", 0, [object()]),
                kwargs={"ellipsis": ...},
                return_value=object(),
                raise_exception=Exception(),
                # =========================
                run_in_executor=False,
                use_execution_context=False,
            ),
        ),
        # Test cases with Sync Generator
        # =================================
        (
            ExecutionTestCase(
                callback=CallableMock.SyncGenerator,
                args=None,
                kwargs=None,
                return_value=object(),
                raise_exception=None,
                # =========================
                run_in_executor=False,
                use_execution_context=False,
            ),
        ),
        (
            ExecutionTestCase(
                callback=CallableMock.SyncGenerator,
                args=None,
                kwargs=None,
                return_value=object(),
                raise_exception=Completed,
                # =========================
                run_in_executor=False,
                use_execution_context=False,
            ),
        ),
        (
            ExecutionTestCase(
                callback=CallableMock.SyncGenerator,
                args=None,
                kwargs=None,
                return_value=object(),
                raise_exception=Exception(),
                # =========================
                run_in_executor=False,
                use_execution_context=False,
            ),
        ),
        (
            ExecutionTestCase(
                callback=CallableMock.SyncGenerator,
                args=("str", 0, [object()]),
                kwargs={"ellipsis": ...},
                return_value=object(),
                raise_exception=None,
                # =========================
                run_in_executor=False,
                use_execution_context=False,
            ),
        ),
        (
            ExecutionTestCase(
                callback=CallableMock.SyncGenerator,
                args=("str", 0, [object()]),
                kwargs={"ellipsis": ...},
                return_value=object(),
                raise_exception=Completed,
                # =========================
                run_in_executor=False,
                use_execution_context=False,
            ),
        ),
        (
            ExecutionTestCase(
                callback=CallableMock.SyncGenerator,
                args=("str", 0, [object()]),
                kwargs={"ellipsis": ...},
                return_value=object(),
                raise_exception=Exception(),
                # =========================
                run_in_executor=False,
                use_execution_context=False,
            ),
        ),
        # Test cases with Async callback
        # =================================
        (
            ExecutionTestCase(
                callback=CallableMock.Async,
                args=None,
                kwargs=None,
                return_value=object(),
                raise_exception=None,
                # =========================
                run_in_executor=False,
                use_execution_context=False,
            ),
        ),
        (
            ExecutionTestCase(
                callback=CallableMock.Async,
                args=None,
                kwargs=None,
                return_value=object(),
                raise_exception=Completed,
                # =========================
                run_in_executor=False,
                use_execution_context=False,
            ),
        ),
        (
            ExecutionTestCase(
                callback=CallableMock.Async,
                args=None,
                kwargs=None,
                return_value=object(),
                raise_exception=Exception(),
                # =========================
                run_in_executor=False,
                use_execution_context=False,
            ),
        ),
        (
            ExecutionTestCase(
                callback=CallableMock.Async,
                args=("str", 0, [object()]),
                kwargs={"ellipsis": ...},
                return_value=object(),
                raise_exception=None,
                # =========================
                run_in_executor=False,
                use_execution_context=False,
            ),
        ),
        (
            ExecutionTestCase(
                callback=CallableMock.Async,
                args=("str", 0, [object()]),
                kwargs={"ellipsis": ...},
                return_value=object(),
                raise_exception=Completed,
                # =========================
                run_in_executor=False,
                use_execution_context=False,
            ),
        ),
        (
            ExecutionTestCase(
                callback=CallableMock.Async,
                args=("str", 0, [object()]),
                kwargs={"ellipsis": ...},
                return_value=object(),
                raise_exception=Exception(),
                # =========================
                run_in_executor=False,
                use_execution_context=False,
            ),
        ),
        # Test cases with Async Generator
        # =================================
        (
            ExecutionTestCase(
                callback=CallableMock.AsyncGenerator,
                args=None,
                kwargs=None,
                return_value=object(),
                raise_exception=None,
                # =========================
                run_in_executor=False,
                use_execution_context=False,
            ),
        ),
        (
            ExecutionTestCase(
                callback=CallableMock.AsyncGenerator,
                args=None,
                kwargs=None,
                return_value=object(),
                raise_exception=Completed,
                # =========================
                run_in_executor=False,
                use_execution_context=False,
            ),
        ),
        (
            ExecutionTestCase(
                callback=CallableMock.AsyncGenerator,
                args=None,
                kwargs=None,
                return_value=object(),
                raise_exception=Exception(),
                # =========================
                run_in_executor=False,
                use_execution_context=False,
            ),
        ),
        (
            ExecutionTestCase(
                callback=CallableMock.AsyncGenerator,
                args=("str", 0, [object()]),
                kwargs={"ellipsis": ...},
                return_value=object(),
                raise_exception=None,
                # =========================
                run_in_executor=False,
                use_execution_context=False,
            ),
        ),
        (
            ExecutionTestCase(
                callback=CallableMock.AsyncGenerator,
                args=("str", 0, [object()]),
                kwargs={"ellipsis": ...},
                return_value=object(),
                raise_exception=Completed,
                # =========================
                run_in_executor=False,
                use_execution_context=False,
            ),
        ),
        (
            ExecutionTestCase(
                callback=CallableMock.AsyncGenerator,
                args=("str", 0, [object()]),
                kwargs={"ellipsis": ...},
                return_value=object(),
                raise_exception=Exception(),
                # =========================
                run_in_executor=False,
                use_execution_context=False,
            ),
        ),
        # Test cases with Executor
        # =================================
        (
            ExecutionTestCase(
                callback=CallableMock.Sync,
                args=None,
                kwargs=None,
                return_value=object(),
                raise_exception=None,
                # =========================
                run_in_executor=True,
                use_execution_context=False,
            ),
        ),
        (
            ExecutionTestCase(
                callback=CallableMock.SyncGenerator,
                args=("str", 0, [object()]),
                kwargs={"ellipsis": ...},
                return_value=object(),
                raise_exception=None,
                # =========================
                run_in_executor=True,
                use_execution_context=False,
            ),
        ),
        (
            ExecutionTestCase(
                callback=CallableMock.Async,
                args=("str", 0, [object()]),
                kwargs={"ellipsis": ...},
                return_value=object(),
                raise_exception=Completed,
                # =========================
                run_in_executor=True,
                use_execution_context=False,
            ),
        ),
        (
            ExecutionTestCase(
                callback=CallableMock.AsyncGenerator,
                args=None,
                kwargs=None,
                return_value=object(),
                raise_exception=Exception(),
                # =========================
                run_in_executor=True,
                use_execution_context=False,
            ),
        ),
        # Test cases with ExecutionContext
        # =================================
        (
            ExecutionTestCase(
                callback=CallableMock.Sync,
                args=None,
                kwargs=None,
                return_value=object(),
                raise_exception=None,
                # =========================
                run_in_executor=False,
                use_execution_context=True,
            ),
        ),
        (
            ExecutionTestCase(
                callback=CallableMock.SyncGenerator,
                args=("str", 0, [object()]),
                kwargs={"ellipsis": ...},
                return_value=object(),
                raise_exception=None,
                # =========================
                run_in_executor=False,
                use_execution_context=True,
            ),
        ),
        (
            ExecutionTestCase(
                callback=CallableMock.Async,
                args=("str", 0, [object()]),
                kwargs={"ellipsis": ...},
                return_value=object(),
                raise_exception=Completed,
                # =========================
                run_in_executor=False,
                use_execution_context=True,
            ),
        ),
        (
            ExecutionTestCase(
                callback=CallableMock.AsyncGenerator,
                args=None,
                kwargs=None,
                return_value=object(),
                raise_exception=Exception(),
                # =========================
                run_in_executor=False,
                use_execution_context=True,
            ),
        ),
        # Test cases with Executor & ExecutionContext
        # =================================
        (
            ExecutionTestCase(
                callback=CallableMock.Sync,
                args=None,
                kwargs=None,
                return_value=object(),
                raise_exception=None,
                # =========================
                run_in_executor=True,
                use_execution_context=True,
            ),
        ),
        (
            ExecutionTestCase(
                callback=CallableMock.SyncGenerator,
                args=("str", 0, [object()]),
                kwargs={"ellipsis": ...},
                return_value=object(),
                raise_exception=None,
                # =========================
                run_in_executor=True,
                use_execution_context=True,
            ),
        ),
        (
            ExecutionTestCase(
                callback=CallableMock.Async,
                args=("str", 0, [object()]),
                kwargs={"ellipsis": ...},
                return_value=object(),
                raise_exception=Completed,
                # =========================
                run_in_executor=True,
                use_execution_context=True,
            ),
        ),
        (
            ExecutionTestCase(
                callback=CallableMock.AsyncGenerator,
                args=None,
                kwargs=None,
                return_value=object(),
                raise_exception=Exception(),
                # =========================
                run_in_executor=True,
                use_execution_context=True,
            ),
        ),
    ]

    # =================================

    @contextmanager
    def execution_test(self, tc: ExecutionTestCase) -> Generator[ObservableTask[Any], None, None]:
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
        main_callback = tc.callback(return_value=tc.return_value, raise_exception=tc.raise_exception)

        # Arrange: Create an instance of ObservableTask with the specified callback and arguments.
        observable_task = ObservableTask[Any](callback=main_callback, args=tc.args, kwargs=tc.kwargs)

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
        assert main_callback.call_count == 1
        assert main_callback.last_args == (tc.args if tc.args else ())
        assert main_callback.last_kwargs == (tc.kwargs if tc.kwargs else {})

        # Assert: Verify subscriber notifications.
        if tc.raise_exception is not None:
            assert next_callback.call_count == 0

            if isinstance(tc.raise_exception, Observable.Completed):
                assert error_callback.call_count == 0

                assert complete_callback.call_count == 1
                assert complete_callback.last_args == ()
                assert complete_callback.last_kwargs == {}
            else:
                assert complete_callback.call_count == 0

                assert error_callback.call_count == 1
                assert error_callback.last_args == (tc.raise_exception,)
                assert error_callback.last_kwargs == {}
        else:
            assert next_callback.call_count == 1
            assert next_callback.last_args == (tc.return_value,)
            assert next_callback.last_kwargs == {}

            assert error_callback.call_count == 0

            assert complete_callback.call_count == (
                1 if isinstance(main_callback, CallableMock.Sync | CallableMock.Async) else 0
            )
            assert complete_callback.last_args == ()
            assert complete_callback.last_kwargs == {}

    # =================================

    def test_execution_with_invalid_input(self) -> None:
        # Arrange
        observable_task = ObservableTask[Any](callback=lambda: object())

        # Act/Assert
        with pytest.raises(PyventusException):
            observable_task(executor=ProcessPoolExecutor())  # type: ignore[arg-type]

    # =================================

    @pytest.mark.parametrize(["tc"], EXECUTION_TEST_CASES)
    def test_execution_in_sync_context(self, tc: ExecutionTestCase) -> None:
        with self.execution_test(tc):
            pass

    # =================================

    @pytest.mark.parametrize(["tc"], EXECUTION_TEST_CASES)
    async def test_execution_in_async_context(self, tc: ExecutionTestCase) -> None:
        with self.execution_test(tc) as obs:
            await obs.wait_for_tasks()

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
            (True,),
            (False,),
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
