# Observers

<p style="text-align: justify;" markdown>
	&emsp;&emsp;While the `Observable` serves as the source and producer of data in the reactive paradigm, the `Observer`, on the other hand, represents the consumer. In the classic Observer pattern, an `Observer` is basically an object that listens to a subject and reacts whenever a state change occurs. This separation of concerns is intended to decouple the generation of data from the downstream logic that processes it.
</p>

<p style="text-align: justify;" markdown>
	&emsp;&emsp;In Pyventus, this concept remains largely the same as in the classic pattern, except that notification handling is integrated with the subscription lifecycle to better fit the library’s broader architecture and improve overall usability. The following section introduces two of the main components of this implementation.
</p>

- <p style="text-align: justify;" markdown><b>Observer:</b>
  Similar to the `EventHandler` in the event-driven module, the `Observer` class is an abstract base class that defines the workflow and essential protocols for handling the three main notification signals emitted by an `Observable`.
  </p>

- <p style="text-align: justify;" markdown><b>Subscriber:</b>
  Represents an `Observer` that is currently or was previously subscribed to an `Observable`. It combines the `Observer` interface with the `Subscription` base class to provide a convenient way to handle notifications and manage the subscription lifecycle.
  </p>

<p style="text-align: justify;" markdown>
	&emsp;&emsp;In practice, you don’t instantiate either the `Observer` base class or the `Subscriber` class directly. Instead, the observer is defined through the Observable’s subscription process, during which a `Subscriber` instance is created with the given definition, registered, and returned.
</p>

## Subscribing

<p style="text-align: justify;" markdown>
	&emsp;&emsp;Since all concrete observables inherit from the `Observable` base class, they share the same `subscribe()` interface for defining and attaching observers. Let’s explore the three ways to define an observer during the subscription process:
</p>

### As a Regular Call

<p style="text-align: justify;" markdown>
	&emsp;&emsp;The most direct way to define an observer is by calling the `subscribe()` method on an observable and passing your callbacks as arguments. This approach is ideal when working with `lambda` functions, built-in callables like `print`, or predefined handlers.
</p>

```Python linenums="1"  hl_lines="6-10"
from pyventus.reactive import ObservableStream


obss = ObservableStream[int]()

subscriber = obss.subscribe(
    next_callback=lambda val: print(f"Next: {val}"),
    error_callback=lambda err: print(f"Error: {err}"),
    complete_callback=lambda: print("Completed!"),
)

obss.next(12345)
obss.error(Exception("Invalid!"))
obss.complete()
```

### As a Decorator

<p style="text-align: justify;" markdown>
	&emsp;&emsp;When you only need to handle incoming `next` signals and want to define the callback at the point of subscription, you can use `subscribe()` as a decorator to define the function and subscribe it as an `Observer` in one step. The decorated function is used exclusively as its `next_callback`, without an `error_callback` or `complete_callback`, while still allowing you to configure execution options such as `force_async` and others.
</p>

```Python linenums="1"  hl_lines="8-10"
from pyventus.reactive import ObservableValue


obsv = ObservableValue[dict[str, str | bool]](
    seed={"theme": "light", "notifications": True},
)

@obsv.subscribe()  # (1)!
def sync_settings_to_storage(settings: dict[str, str | bool]) -> None:
    print(f"Syncing user settings: {settings}")


obsv.set_value({"theme": "dark", "notifications": True})
obsv.set_value({"theme": "dark", "notifications": False})
```

1.  <p style="text-align: justify;" markdown>
        &emsp;&emsp;To retrieve the subscriber created by the decorator, set `stateful_subctx` to `True`. This makes the subscription context stateful, so it keeps track of the subscriber and its source.
    </p>

    ```Python hl_lines="1"
    @obsv.subscribe(stateful_subctx=True)
    def sync_settings_to_storage(settings: dict[str, str | bool]) -> None:
        print(f"Syncing user settings: {settings}")
    ```

    <p style="text-align: justify;" markdown>
        &emsp;&emsp;With a stateful subscription context, the decorated callback becomes a tuple containing the original callback and the context. You can unpack them like this:
    </p>

    ```Python hl_lines="1"
    sync_settings_to_storage, subctx = sync_settings_to_storage
    ```

    <p style="text-align: justify;" markdown>
        &emsp;&emsp;Call `unpack()` on the context to retrieve the observable to which the subscriber was subscribed, along with the subscriber itself. The call also clears the information stored in the context:
    </p>

    ```Python hl_lines="1"
    obsv, subscriber = subctx.unpack()
    ```

### As a Context Manager

<p style="text-align: justify;" markdown>
	&emsp;&emsp;Since Python’s `lambda` functions are limited to a single expression, working with multi-line callbacks across different signals (`next`, `error`, and `complete`) forces you to define the callbacks beforehand, separately from the subscription, making the overall process not only cumbersome to work with but also prone to errors. However, for these scenarios, Pyventus also lets you use the `subscribe()` method as a context manager, so you can define the observer’s callbacks inline and in a step-by-step manner right before the subscription takes place.
</p>

```Python linenums="1"  hl_lines="15 17 18 21 22 26 27"
from pyventus.reactive import as_observable_task, Completed


@as_observable_task
def icounter():
    response: str = input("Count to (or 'exit'): ").strip()
    if response.lower() != "exit":
        yield from range(1, int(response) + 1)
    raise Completed


counter = icounter()


with counter.subscribe() as subctx:  # (1)!

    @subctx.on_next
    def next(value: int) -> None:
        print(f"Received: {value}")

    @subctx.on_error
    def error(error: Exception) -> None:
        print(f"Exception: {error}")
        counter()  # Reinvoke the existing observable.

    @subctx.on_complete
    def complete() -> None:
        print("All done!")


counter()
```

1.  <p style="text-align: justify;" markdown>
        &emsp;&emsp;To retrieve the subscriber created by the subscription context manager, set `stateful_subctx` to `True` when calling the `subscribe()` method. This makes the subscription context stateful, allowing it to keep track of the subscriber and the observable it subscribed to.
    </p>

    ```Python hl_lines="1"
    with counter.subscribe(stateful_subctx=True) as subctx:

        @subctx.on_next
        def next(value: int) -> None:
            print(f"Received: {value}")

        @subctx.on_error
        def error(error: Exception) -> None:
            print(f"Exception: {error}")
            counter()  # Reinvoke the existing observable.

        @subctx.on_complete
        def complete() -> None:
            print("All done!")
    ```

    <p style="text-align: justify;" markdown>
        &emsp;&emsp;Call `unpack()` on the context to retrieve the observable to which the subscriber was subscribed, along with the subscriber itself. The call also clears the information stored in the context:
    </p>

    ```Python hl_lines="1"
    obst, subscriber = subctx.unpack()
    ```

## Subscription Lifecycle

<p style="text-align: justify;" markdown>
	&emsp;&emsp;A `Subscriber` remains active and continues to receive notifications until it is detached by one of the following mechanisms:
</p>

- <p style="text-align: justify;" markdown><b>Manual Unsubscription:</b>
  Calling `unsubscribe()` on a `Subscriber` instance detaches it from the observable it is subscribed to. Calling `observable.remove_subscriber(sub)` achieves the same result from the observable’s side.
  </p>

    === ":material-file-document-remove: Using `unsubscribe()`"
        ```Python linenums="1"  hl_lines="7"
        from pyventus.reactive import ObservableStream

        obss = ObservableStream[int]()
        sub = obss.subscribe(next_callback=print)
        obss.next(0)

        sub.unsubscribe()

        obss.next(1)
        ```
    === ":material-book-remove-multiple: Using `remove_subscriber()`"
        ```Python linenums="1" hl_lines="7"
        from pyventus.reactive import ObservableStream

        obss = ObservableStream[int]()
        sub = obss.subscribe(next_callback=print)
        obss.next(0)

        obss.remove_subscriber(sub)

        obss.next(1)
        ```

- <p style="text-align: justify;" markdown><b>Bulk Unsubscription:</b>
  Calling `remove_all()` on an `Observable` detaches and unsubscribes all currently registered subscribers at once.
  </p>

    ```Python linenums="1" hl_lines="7"
    from pyventus.reactive import ObservableStream

    obss = ObservableStream[int]()
    sub = obss.subscribe(next_callback=print)
    obss.next(0)

    obss.remove_all()

    obss.next(1)
    ```

- <p style="text-align: justify;" markdown><b>Automatic Unsubscription:</b>
  When an observable emits a `complete` signal, it notifies all active subscribers by calling their `complete_callback` and automatically unsubscribes them, resetting the observable’s registry for future subscriptions.
  </p>

    ```Python linenums="1" hl_lines="7"
    from pyventus.reactive import ObservableStream

    obss = ObservableStream[int]()
    sub = obss.subscribe(next_callback=print)
    obss.next(0)

    obss.complete()

    obss.next(1)
    ```

## Sync and Async Support

<p style="text-align: justify;" markdown>
	&emsp;&emsp;Pyventus is designed from the ground up to support both synchronous and asynchronous programming models. Its unified sync/async API lets you define any of the Observer’s callbacks as either a synchronous or asynchronous callable.
</p>

```Python linenums="1" hl_lines="18-22 24-27"
from asyncio import sleep

from pyventus.reactive import as_observable_task, Completed


@as_observable_task
def icounter():
    response: str = input("Count to (or 'exit'): ").strip()
    if response.lower() != "exit":
        yield from range(1, int(response) + 1)
    raise Completed


counter = icounter()

with counter.subscribe() as subctx:

    @subctx.on_next
    async def next(value: int) -> None:
        print(f"Received: {value}")
        await sleep(0.25)  # Simulate async processing.
        print(f"Processed: {value}")

    @subctx.on_error
    def error(error: Exception) -> None:
        print(f"Exception: {error}")
        counter()  # Reinvoke the existing observable.

    @subctx.on_complete
    def complete() -> None:
        print("All done!")


counter()
```

## Threat Offloading

<p style="text-align: justify;" markdown>
	&emsp;&emsp;By default, observers in Pyventus are executed concurrently during each signal notification, running their `sync` and `async` callbacks as defined. However, if you have a `sync` callback that involves I/O or non-CPU bound operations, you can enable the `force_async` parameter to offload it to a thread pool, ensuring optimal performance and responsiveness. The offloading process is handled by the [`asyncio.to_thread()`](https://docs.python.org/3/library/asyncio-task.html#running-in-threads) function.
</p>

```Python linenums="1" hl_lines="13-17"
from asyncio import run
from time import sleep, strftime

from pyventus.core.processing.asyncio import AsyncIOProcessingService
from pyventus.reactive import ObservableStream


@AsyncIOProcessingService.guard
async def main() -> None:

    obss = ObservableStream[str]()

    @obss.subscribe(force_async=True)
    def persist_to_disk(payload: str) -> None:
        print(f"\tStart blocking I/O for '{payload}' at {strftime('%X')}")
        sleep(1)  # Simulate a blocking I/O operation (e.g., writing to disk).
        print(f"\tCompleted blocking I/O for '{payload}' at {strftime('%X')}")

    @obss.subscribe()
    async def real_time_alert(payload: str) -> None:
        # Runs immediately on the event loop without being blocked by `persist_to_disk`.
        print(f"Real-time alert triggered for '{payload}' at {strftime('%X')}")

    # Emit multiple entries.
    obss.next("Order#1001")
    obss.next("Order#1002")
    obss.next("Order#1003")


run(main())
```
