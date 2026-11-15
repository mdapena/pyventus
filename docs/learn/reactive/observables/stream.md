# Observable Stream

The `ObservableStream` class is a data flow-centric `Observable` subclass that encapsulates a continuous flow of data and provides a mechanism for streaming its entries over time.

With the `ObservableStream` class, you can easily create observable data channels that allow you to not only push entries through, but also subscribe to them and receive notifications as new values, errors, or completion signals occur.

## Declaration

As one of the most straightforward observables, the `ObservableStream` class does not require any parameters upon initialization, so you can declare a new stream by simply creating an instance of the class:

```Python
# Code Example 
```

## Signal Triggering

Every observable emits three types of signals to communicate with its subscribers, and `ObservableStream` translates each of them into a dedicated method that can be invoked directly:

- **Next:** This signal is triggered whenever the `next()` method is invoked on the instance, forwarding the given entry to its subscribers.

    ```Python
    # Code Example 
    ```

- **Error:** This signal is triggered whenever the `error()` method is invoked on the instance, forwarding the given exception to its subscribers.

    ```Python
    # Code Example 
    ```

- **Complete:** This signal is triggered whenever the `complete()` method is invoked on the instance, notifying its subscribers and subsequently removing them.

    ```Python
    # Code Example 
    ```

## Key Highlights

In addition to the capabilities inherited from the `Observable` base class and the behavior already described above, the `ObservableStream` class also offers a series of distinct highlights that are worth mentioning:

- **Order-Preserving Execution:** All signal emissions inside the `ObservableStream` are managed and synchronized through an internal queue, ensuring that their order is preserved and no inconsistent notifications are generated.

    ```Python
    # Code Example 
    ```

- **Straightforward and Lightweight:** As one of the simplest implementations of the `Observable` base class, the `ObservableStream` acts as a direct pass-through channel, making it effortless to set up and use.

    ```Python
    # Code Example 
    ```

## Usage Examples

To illustrate how `ObservableStream` works in practice, the following self-contained examples demonstrate the different ways it can be defined, subscribed to, and used across various scenarios:

```Python
# Code Example
```
