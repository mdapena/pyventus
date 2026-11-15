# Observable Task

The `ObservableTask` class is an `Observable` subclass designed to wrap any Python callable and its arguments into a self-contained, reactive unit of work. Unlike a standard function call that runs immediately and returns a result to the caller, an `ObservableTask` is evaluated lazily by packaging the callable and its parameters together so you can pass the task around, attach multiple observers to it, and trigger its execution whenever needed.

With `ObservableTask`, you can turn both `sync` and `async` functions or generators, as well as custom callable objects, into push-based observables. Once the task is triggered, it executes the wrapped callback with the given arguments and streams any returned or yielded values, raised exceptions, and completion signals to its subscribers accordingly.

## Declaration

An `ObservableTask` can be created in two ways depending on whether you are wrapping a single one-off call or reusing the same function with different arguments.

- **Direct Instantiation:** You can instantiate the `ObservableTask` class directly by passing both the callable and its positional or keyword arguments to the constructor. This packages that specific callable and those exact arguments into a single `ObservableTask` instance ready to be subscribed to and executed on demand.

    ```Python
    # Code Example
    ```

- **Decorator Wrapping:** When the function stays the same across calls and only its arguments change, you can wrap it with the `@as_observable_task` decorator instead of instantiating `ObservableTask` manually every time. Once decorated, calling the function with your parameters automatically creates and returns a new `ObservableTask` for that function and those arguments, rather than executing the function and returning its value right away.

    ```Python
    # Code Example
    ```

## Signal Triggering

Every observable emits three types of signals to communicate with its subscribers, and `ObservableTask` translates standard Python execution flows directly into those signals.

- **Next:** This signal is triggered by the `return` or `yield` statements inside the wrapped callable, carrying the returned value or yielded values directly to the subscribers depending on the callable type.

    - **Regular Functions and Methods:** In both `sync` and `async` functions or methods, this signal is triggered when the callable returns, streaming the returned value to its subscribers.

        ```Python
        # Code Example
        ```

    - **Generators** In both `sync` and `async` generators, this signal is triggered on every `yield` expression, streaming each yielded value to the subscribers as the generator iterates.

        ```Python
        # Code Example
        ```

- **Error:** This signal is triggered by raising any unhandled exception distinct from `Observable.Completed` inside the wrapped callable, immediately stopping execution and sending that exception to the subscribers.

    ```Python
    # Code Example
    ```

- **Complete:** This signal is triggered whenever the `Observable.Completed` exception is raised during the execution of the `ObservableTask`. By default, this exception is always raised once the wrapped callable finishes executing. However, you can disable this behavior by setting the `auto_complete` property to `False`, requiring `Observable.Completed` to be raised explicitly inside the wrapped callable to trigger the signal.

    ```Python
    # Code Example
    ```

## Key Highlights

In addition to the capabilities inherited from the `Observable` base class and the behavior already described above, the `ObservableTask` class also offers a series of distinct highlights that are worth mentioning:

- **Simplified Execution for Observable Tasks:** Having to explicitly call each observable task to initiate their execution can be tedious and easily overlooked, especially when working with multiple observables at the same time. However, by using observable tasks within a `with` statement block, you can avoid this manual work and enable what is known as their execution context, which will allow you to work with them as usual while ensuring that they are called upon exiting the context block.

    ```Python
    # Code Example
    ```

- **Thread Offloading for Observable Tasks:** By default, the processing of each observable task is handled by the AsyncIO framework, either synchronously or asynchronously depending on the context. However, for multithreaded environments, Pyventus also provides support for running these observable tasks in separate threads.

    ```Python
    # Code Example
    ```

## Usage Examples

To illustrate how `ObservableTask` works in practice, the following self-contained examples demonstrate the different ways it can be defined, subscribed to, and executed across various scenarios:

```Python
# Code Example
```
