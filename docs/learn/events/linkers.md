# Event Linkers

<p style="text-align: justify;" markdown>
    &emsp;&emsp;As we discussed in the previous section on [Event Types](types.md), events are essential components of an event-driven architecture. However, by themselves, they are simply messages without context. So, we need a way to connect these events to the logic that determines how the system should respond. To accomplish this, Pyventus introduces the concept of the Event Linker.
</p>

<p style="text-align: justify;">
    &emsp;&emsp;In summary, the Event Linker is a base class that provides a centralized mechanism for managing the connections between events and their corresponding logic. It can be subclassed to create specific namespaces or contexts, or to modify its behavior.
</p>

## Event Subscribers and Handlers

<p style="text-align: justify;">
    &emsp;&emsp;Before we dive deeper into the functionalities of the Event Linker, it's important to grasp the following concepts for a better understanding:
</p>

- <p style="text-align: justify;"><b>Event Handler:</b>
  	The Event Handler is an abstract base class that defines the workflow and essential protocols for event handling.
  </p>
- <p style="text-align: justify;"><b>Event Subscriber:</b>
  	Represents an Event Handler that is or was subscribed to an Event Linker. It combines the Event Handler interface with the Subscription base class, providing a convenient way to handle events and manage the subscription lifecycle.
  </p>

<p style="text-align: justify;">
    &emsp;&emsp;When performing subscriptions with the Event Linker, the returned object will always be an Event Subscriber.
</p>

## Subscribing

<p style="text-align: justify;">
    &emsp;&emsp;The Event Linker offers different alternatives for the subscription process, allowing you to choose the approach that best aligns with your unique requirements and style. However, regardless of the method you choose, each subscription will create an independent instance of an Event Subscriber. So, for example, if you subscribe the same callback multiple times to an event, it will be invoked multiple times.
</p>

### Regular Subscriptions

<p style='text-align: justify;' markdown>
	&emsp;&emsp;Regular subscriptions enable the event workflow to be triggered by the subscribed event(s) any number of times until they are explicitly unsubscribed.
</p>

=== "Using Decorators"

    ```Python linenums="1" hl_lines="4-5"
    from pyventus.events import EventLinker


    @EventLinker.on("MyEvent")
    def handle_my_event():  # (1)!
    	print("Handling 'MyEvent'!")
    ```

    1.  You can also work with `async` functions:

    	```Python linenums="1" hl_lines="2"
    	@EventLinker.on("MyEvent")
    	async def handle_my_event():
    		print("Handling 'MyEvent'!")
    	```

=== "Using `subscribe()`"

    ```Python linenums="1" hl_lines="3 6"
    from pyventus.events import EventLinker

    def handle_my_event():  # (1)!
    	print("Handling 'MyEvent'!")

    EventLinker.subscribe("MyEvent", event_callback=handle_my_event)
    ```

    1.  You can also work with `async` functions:

    	```Python linenums="1" hl_lines="1"
    	async def handle_my_event():
    		print("Handling 'MyEvent'!")

    	EventLinker.subscribe("MyEvent", event_callback=handle_my_event)
    	```

### One-time Subscriptions

<p style="text-align: justify;">
	&emsp;&emsp;One-time subscriptions enable the event workflow to be triggered by the subscribed event(s) only once, after which it automatically unsubscribes.
</p>

=== "Using Decorators"

    ```Python linenums="1" hl_lines="4-5"
    from pyventus.events import EventLinker


    @EventLinker.once("MyEvent")
    def handle_my_event_once():  # (1)!
    	print("Handling 'MyEvent' once!")
    ```

    1.  You can also work with `async` functions:

    	```Python linenums="1" hl_lines="2"
    	@EventLinker.once("MyEvent")
    	async def handle_my_event_once():
    		print("Handling 'MyEvent' once!")
    	```

=== "Using `subscribe()`"

    ```Python linenums="1" hl_lines="3 6"
    from pyventus.events import EventLinker

    def handle_my_event_once():  # (1)!
    	print("Handling 'MyEvent' once!")

    EventLinker.subscribe("MyEvent", event_callback=handle_my_event_once, once=True)
    ```

    1.  You can also work with `async` functions:

    	```Python linenums="1" hl_lines="1"
    	async def handle_my_event_once():
    		print("Handling 'MyEvent' once!")

    	EventLinker.subscribe("MyEvent", event_callback=handle_my_event_once, once=True)
    	```

### Multi-Event Subscriptions

<p style="text-align: justify;">
	&emsp;&emsp;The previous subscription methods also allow you to subscribe the event workflow to multiple events at once. Simply add more events after the first one, and that’s it! You can even combine different event types together.
</p>

=== "Using Decorators"

    ```Python linenums="1" hl_lines="4 9"
    from pyventus.events import EventLinker


    @EventLinker.on("FirstEvent", "SecondEvent")
    def handle_events():  # (1)!
    	print("Handling multiple events!")


    @EventLinker.once("FirstEvent", "SecondEvent")
    def handle_events_once():  # (2)!
    	print("Handling multiple events once!")
    ```

    1.  You can also work with `async` functions:

    	```Python linenums="1" hl_lines="2"
    	@EventLinker.on("FirstEvent", "SecondEvent")
    	async def handle_events():
    		print("Handling multiple events!")
    	```

    2.  You can also work with `async` functions:

    	```Python linenums="1" hl_lines="2"
    	@EventLinker.once("FirstEvent", "SecondEvent")
    	async def handle_events_once():
    		print("Handling multiple events once!")
    	```

=== "Using `subscribe()`"

    ```Python linenums="1" hl_lines="10-11"
    from pyventus.events import EventLinker


    def handle_events():  # (1)!
    	print("Handling multiple events!")

    def handle_events_once():  # (2)!
    	print("Handling multiple events once!")

    EventLinker.subscribe("FirstEvent", "SecondEvent", event_callback=handle_events)
    EventLinker.subscribe("FirstEvent", "SecondEvent", event_callback=handle_events_once, once=True)
    ```

    1.  You can also work with `async` functions:

    	```Python linenums="1" hl_lines="1"
    	async def handle_events():
    		print("Handling multiple events!")

    	EventLinker.subscribe("FirstEvent", "SecondEvent", event_callback=handle_events)
    	```

    2.  You can also work with `async` functions:

    	```Python linenums="1" hl_lines="1"
    	async def handle_events_once():
    		print("Handling multiple events once!")

    	EventLinker.subscribe("FirstEvent", "SecondEvent", event_callback=handle_events_once, once=True)
    	```

??? tip "One-Time Subscriptions with Multiple Events"

    <p style="text-align: justify;">
        &emsp;&emsp;When performing one-time subscriptions with multiple events, the first event that gets triggered will automatically unsubscribe the subscriber from all other events. As a result, regardless of how many events a one-time subscriber is listening to, it will only be triggered once.
    </p>

### Event Workflow Definition

<p style="text-align: justify;" markdown>
    &emsp;&emsp;With Pyventus, you can define the overall workflow for an event, from its initial response to its completion, whether it succeeds or encounters errors. This definition is established during the subscription process and includes three main callbacks: `event_callback`, `success_callback`, and `failure_callback`.
</p>

=== "Using Decorators"

    ```Python linenums="1"  hl_lines="4 6-7 10-11 14-15"
    from pyventus.events import EventLinker

    # Create a subscription context for the "DivisionEvent" event
    with EventLinker.on("DivisionEvent") as subctx:  # (1)!

        @subctx.on_event
        def divide(a: float, b: float) -> float:  # (2)!
            return a / b

        @subctx.on_success
        def handle_success(result: float) -> None:  # (3)!
            print(f"Division result: {result:.3g}")

        @subctx.on_failure
        def handle_failure(e: Exception) -> None:  # (4)!
            print(f"Oops, something went wrong: {e}")
    ```

    1.  You can also use the `once()` decorator:

        ```Python linenums="1"  hl_lines="3"
        from pyventus.events import EventLinker

        with EventLinker.once("DivisionEvent") as subctx:

            @subctx.on_event
            def divide(a: float, b: float) -> float:
                return a / b

            @subctx.on_success
            def handle_success(result: float) -> None:
                print(f"Division result: {result:.3g}")

            @subctx.on_failure
            def handle_failure(e: Exception) -> None:
                print(f"Oops, something went wrong: {e}")
        ```

    2.  This callback will be executed when the event occurs.
    3.  This callback will be executed when the event response completes successfully.
    4.  This callback will be executed when the event response fails.

=== "Using `subscribe()`"

    ```Python linenums="1"  hl_lines="3-8"
    from pyventus.events import EventLinker

    EventLinker.subscribe(  # (1)!
        "DivisionEvent",
        event_callback=lambda a, b: a / b,  # (2)!
        success_callback=lambda result: print(f"Division result: {result:.3g}"),  # (3)!
        failure_callback=lambda e: print(f"Oops, something went wrong: {e}"),  # (4)!
    )
    ```

    1.  You can also make this a one-time subscription:

        ```Python linenums="1"  hl_lines="8"
        from pyventus.events import EventLinker

        EventLinker.subscribe(
            "DivisionEvent",
            event_callback=lambda a, b: a / b,
            success_callback=lambda result: print(f"Division result: {result:.3g}"),
            failure_callback=lambda e: print(f"Oops, something went wrong: {e}"),
            once=True,
        )
        ```

    2.  This callback will be executed when the event occurs.
    3.  This callback will be executed when the event response completes successfully.
    4.  This callback will be executed when the event response fails.

### Optimizing Event Subscribers

<p style="text-align: justify;" markdown>
    &emsp;&emsp;By default, event subscribers in Pyventus are executed concurrently during an event emission[^1], running their `sync` and `async` callbacks as defined. However, if you have a `sync` callback that involves I/O or non-CPU bound operations, you can enable the `force_async` parameter to offload it to a thread pool, ensuring optimal performance and responsiveness. The offloading process is handled by the <a href="https://docs.python.org/3/library/asyncio-task.html#running-in-threads" target="_blank">`asyncio.to_thread()`</a> function.
</p>

=== "Using Decorators"

    ```Python linenums="1"  hl_lines="5"
    import time
    from pyventus.events import EventLinker


    @EventLinker.on("BlockingIO", force_async=True)  # (1)!
    def blocking_io():
        print(f"start blocking_io at {time.strftime('%X')}")
        # Note that time.sleep() can be replaced with any blocking
        # IO-bound operation, such as file operations.
        time.sleep(1)
        print(f"blocking_io complete at {time.strftime('%X')}")
    ```

    1.  This property is also available for the `once()` decorator:

        ```Python linenums="1"  hl_lines="5"
        import time
        from pyventus.events import EventLinker


        @EventLinker.once("BlockingIO", force_async=True)
        def blocking_io():
            print(f"start blocking_io at {time.strftime('%X')}")
            # Note that time.sleep() can be replaced with any blocking
            # IO-bound operation, such as file operations.
            time.sleep(1)
            print(f"blocking_io complete at {time.strftime('%X')}")
        ```

=== "Using `subscribe()`"

    ```Python linenums="1"  hl_lines="16"
    import time
    from pyventus.events import EventLinker


    def blocking_io():
        print(f"start blocking_io at {time.strftime('%X')}")
        # Note that time.sleep() can be replaced with any blocking
        # IO-bound operation, such as file operations.
        time.sleep(1)
        print(f"blocking_io complete at {time.strftime('%X')}")


    EventLinker.subscribe(  # (1)!
        "BlockingIO",
        event_callback=blocking_io,
        force_async=True,
    )
    ```

    1.  You can also make this a one-time subscription:

        ```Python linenums="1"  hl_lines="17"
        import time
        from pyventus.events import EventLinker


        def blocking_io():
            print(f"start blocking_io at {time.strftime('%X')}")
            # Note that time.sleep() can be replaced with any blocking
            # IO-bound operation, such as file operations.
            time.sleep(1)
            print(f"blocking_io complete at {time.strftime('%X')}")


        EventLinker.subscribe(
            "BlockingIO",
            event_callback=blocking_io,
            force_async=True,
            once=True,
        )
        ```

### Retrieving Event Subscribers from Subscriptions

<p style="text-align: justify;" markdown>
    &emsp;&emsp;As we discussed earlier, each subscription generates its own instance of an Event Subscriber, and you can always access it whenever necessary.
</p>

=== "Using Decorators"

    ```Python linenums="1"  hl_lines="4 9 10"
    from pyventus.events import EventLinker


    @EventLinker.on("MyEvent", stateful_subctx=True)  # (1)!
    def handle_my_event():
        print("Handling 'MyEvent'!")


    handle_my_event, subctx = handle_my_event
    event_linker, event_subscriber = subctx.unpack()
    ```

    1.  Setting `stateful_subctx` to `True` will not only make the subscription context object accessible, but it will also preserve its state, allowing us to access the subscriber and the source to which it was subscribed through the `unpack()` method.

=== "Using `subscribe()`"

    ```Python linenums="1"  hl_lines="4"
    from pyventus.events import EventLinker, EventSubscriber


    event_subscriber: EventSubscriber = EventLinker.subscribe(
        "MyEvent", event_callback=lambda: print("Handling 'MyEvent'!")
    )
    ```

## Unsubscribing

<p style="text-align: justify;">
    &emsp;&emsp;The unsubscription process can be accomplished through various methods, each providing different levels of detail and control. It's worth noting that all of these methods will return a boolean value to indicate whether the removal was successful.
</p>

### Removing Subscribers

=== "Using `unsubscribe()`"

    ```Python linenums="1" hl_lines="9"
    from pyventus.events import EventLinker, EventSubscriber


    event_subscriber: EventSubscriber = EventLinker.subscribe(
        "FirstEvent", "SecondEvent",
        event_callback=lambda: print("Handling two events!")
    )

    event_subscriber.unsubscribe()  # (1)!
    ```

    1.  This will remove the event subscriber from both the `FirstEvent` and `SecondEvent`.

=== "Using `remove_subscriber()`"

    ```Python linenums="1" hl_lines="9"
    from pyventus.events import EventLinker, EventSubscriber


    event_subscriber: EventSubscriber = EventLinker.subscribe(
        "FirstEvent", "SecondEvent",
        event_callback=lambda: print("Handling two events!")
    )

    EventLinker.remove_subscriber(event_subscriber)  # (1)!
    ```

    1.  This will remove the event subscriber from both the `FirstEvent` and `SecondEvent`.

### Removing Linkages

```Python linenums="1" hl_lines="5 9"
from pyventus.events import EventLinker, EventSubscriber


event_subscriber: EventSubscriber = EventLinker.subscribe(
    "FirstEvent", "SecondEvent",
    event_callback=lambda: print("Handling two events!")
)

EventLinker.remove("FirstEvent", event_subscriber)  # (1)!
```

1.  This will remove the `FirstEvent` from the `event_subscriber`, but it will not be fully unsubscribed since it is still subscribed to the `SecondEvent`.

### Removing Events

```Python linenums="1" hl_lines="13"
from pyventus.events import EventLinker


EventLinker.subscribe(
    "FirstEvent",
    event_callback=lambda: print("Handling one event!")
)
EventLinker.subscribe(
    "FirstEvent", "SecondEvent",
    event_callback=lambda: print("Handling two events!")
)

EventLinker.remove_event("FirstEvent")  # (1)!
```

1.  This will remove the `FirstEvent` from both subscribers. However, only the first subscriber will be fully unsubscribed, as it was exclusively subscribed to the `FirstEvent`. The second subscriber will continue to be subscribed to the `SecondEvent`.

### Removing All

```Python linenums="1" hl_lines="13"
from pyventus.events import EventLinker


EventLinker.subscribe(
    "FirstEvent",
    event_callback=lambda: print("Handling one event!")
)
EventLinker.subscribe(
    "FirstEvent", "SecondEvent",
    event_callback=lambda: print("Handling two events!")
)

EventLinker.remove_all()  # (1)!
```

1.  This will remove all events and their associated subscribers from the Event Linker registry.

## Registry Accessibility

<p style="text-align: justify;" markdown>
    &emsp;&emsp;The Event Linker offers several methods to access the registry and retrieve necessary information from both the event and subscriber perspectives. For instance, you can obtain all subscribers for a specific event or retrieve all events associated with a particular subscriber. For more information, please refer to the API documentation for methods ranging from [`is_empty()`](../../api/events/linkers/event_linker.md#pyventus.events.EventLinker.is_empty) to [`are_linked()`](../../api/events/linkers/event_linker.md#pyventus.events.EventLinker.are_linked).
</p>

## Custom Event Linkers

<p style="text-align: justify;">
	&emsp;&emsp;The Event Linker class in Pyventus is built from the ground up to support both subclassing and configuration, allowing you to not only create separate linking registries or namespaces but also customize its behavior as needed.
</p>

```Python linenums="1" hl_lines="4 9 14"
from pyventus.events import EventLinker


class UserEventLinker(EventLinker, max_subscribers=1):  # (1)!
    """EventLinker for User's events only"""
    pass  # Additional logic can be added here if needed...


@UserEventLinker.on("PasswordResetEvent")
async def handle_password_reset_event(email: str):
    print("PasswordResetEvent received!")


@UserEventLinker.on("EmailVerifiedEvent")
async def handle_email_verified_event(email: str):
    print("EmailVerifiedEvent received!")
```

1.  The `max_subscribers` property determines the maximum number of subscribers allowed for each event. By default, it is set to `None` (infinity).

## Debug Mode

<p style="text-align: justify;">
	&emsp;&emsp;The Event Linker also offers a debug mode feature which helps you understand how event subscriptions and unsubscriptions are happening during runtime.
</p>

### Global Debug Mode

<p style="text-align: justify;">
	&emsp;&emsp;By default, Pyventus leverages the Python's global debug tracing feature. Simply run your code in an IDE's debugger mode to activate the global debug mode tracing.
</p>

<p align="center">
   <img style="border-radius: 0.5rem;" src="../../../images/examples/event-linker-debug-mode-example.png" alt="EventLinker Global Debug Mode" width="900px">
</p>

### Namespace Debug Mode

<p style="text-align: justify;" markdown>
    &emsp;&emsp;Alternatively, if you want to enable or disable the debug mode specifically for a certain `EventLinker` namespace, you can use the `debug` flag that is available in the subclass configurations. Setting the `debug` flag to `True` enables debug mode for that namespace, while setting it to `False` disables debug mode.
</p>

=== "Debug Mode `On`"

    ```Python linenums="1" hl_lines="1"
    class CustomEventLinker(EventLinker, debug=True):
        pass  # Additional logic can be added here if needed...
    ```

=== "Debug Mode `Off`"

    ```Python linenums="1" hl_lines="1"
    class CustomEventLinker(EventLinker, debug=False):
        pass  # Additional logic can be added here if needed...
    ```

[^1]: Since each event subscriber is executed concurrently during an event emission, an active AsyncIO loop is always present within each callback. As a result, creating a new AsyncIO loop inside a callback is neither possible nor useful for performing asynchronous work. Instead, you can define the entire callback as `async` without any issues.
