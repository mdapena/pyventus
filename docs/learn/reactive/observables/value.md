# Observable Value

The `ObservableValue` class is a value-centric `Observable` subclass that encapsulates a value and provides a mechanism for streaming its changes over time.

With the `ObservableValue` class, you can turn any Python value into a push-based observable and subscribe to it to receive notifications of all its mutations as they occur, including valid and invalid ones, as well as value resets.

## Declaration

In order to define an `ObservableValue`, you simply have to create an instance of the class with an initial `seed` value and, optionally, a series of `validators` to enforce rules on future updates.

```Python
# Code Example 
# (1)!
```

1.  Validators do not apply to the `seed` value, neither upon instantiation nor during resets.

## Signal Triggering

Every observable emits three types of signals to communicate with its subscribers, and `ObservableValue` translates state mutations and validation outcomes directly into those signals:

- **Next:** This signal is triggered whenever a valid value is set through the `set_value()` method. A value is deemed valid if it passes all configured `validators` or if no validators are present.

    ```Python
    # Code Example 
    ```

- **Error:** This signal is triggered whenever an invalid value is set through the `set_value()` method. A value is deemed invalid if any of the configured `validators` raises an exception. Both the value and the exception are stored for later retrieval.

    ```Python
    # Code Example 
    ```

- **Complete:** This signal is triggered whenever the value is cleared and reset to its initial `seed` state through the `clear()` method.

    ```Python
    # Code Example 
    ```

## Key Highlights

In addition to the capabilities inherited from the `Observable` base class and the behavior already described above, the `ObservableValue` class also offers a series of distinct highlights that are worth mentioning:

- **Sync and Async Validation:** Any of the `validators` can be defined as either a `sync` or `async` callable. However, it is important to note that all of them are run concurrently during validation and executed as defined, meaning that blocking validators will still freeze the event loop until they finish.

    ```Python
    # Code Example 
    ```

- **Order-Preserving Execution:** All update and retrieval operations inside the `ObservableValue` are managed and synchronized through a queue, ensuring that their order is preserved and no inconsistent states or notifications are generated.

    ```Python
    # Code Example 
    ```

- **Subscriber Priming:** One or more subscribers can be primed at any time through the `prime_subscribers()` method of an `ObservableValue`. Based on its current state, this method will trigger the corresponding signals for only the given subscribers.

    ```Python
    # Code Example 
    ```

- **State Inspection:** - Through the `get_value()` and `get_error()` methods, the current value or error of an `ObservableValue` can be retrieved respectively. Both are exposed as callables so that each read is synchronized through the internal queue, ensuring no inconsistent state is ever returned.

    ```Python
    # Code Example 
    ```

## Usage Examples

To illustrate how `ObservableValue` works in practice, the following self-contained examples demonstrate the different ways it can be defined, subscribed to, and updated across various scenarios:

```Python
# Code Example 
```
