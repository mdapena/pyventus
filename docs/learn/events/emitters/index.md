---
hide:
    - feedback
---

# Master the Event Emitter

!!! warning "🏗️ Work in Progress"

    This section is currently being rebuilt.

<p style='text-align: justify;' markdown>
	&emsp;&emsp;In the previous tutorial, we learned how to link events with their event handlers using the 
	`EventLinker`. Now, let's dive into the process of dispatching events and triggering the associated callbacks.
	This tutorial will introduce you to the `EventEmitter` class, which plays a crucial role in this event-driven
	system.
</p>

## What is an Event Emitter?

<p style='text-align: justify;' markdown>
	&emsp;&emsp;In event-driven programming, an Event Emitter is a variation of the [Observer pattern](https://refactoring.guru/design-patterns/observer)
	that allows you to easily manage and handle events in a decoupled manner. The Observer pattern provides a way for 
	objects to subscribe to and receive notifications from a subject when its state changes. Similarly, an Event Emitter
	enables objects/functions to subscribe to and receive notifications when specific events occur.
</p>

## Pyventus Event Emitter

<p style='text-align: justify;' markdown>
	&emsp;&emsp;In Pyventus, the Event Emitter concept remains largely the same, but with a few unique features of its 
	own. The Pyventus Event Emitter focuses only on emitting events, while the association logic is handled by the
	Event Linker class. This separation of concerns makes both classes cleaner and easier to understand, as well as 
	allowing them to be modified independently as needed. Furthermore, it offers the flexibility to change the event
	emitter instance at runtime without the need to reconfigure all connections.
</p>

<p style='text-align: justify;' markdown>
	&emsp;&emsp;So, what exactly is the Pyventus `EventEmitter`? It is an abstract base class that provides a common 
	interface for emitting events and notifying registered callbacks when those events occur. It serves as the 
	foundation for implementing custom event emitters with specific dispatch strategies.
</p>

### Purpose of Pyventus Event Emitter

<p style='text-align: justify;' markdown>
	&emsp;&emsp;The main goal of the `EventEmitter` base class is to decouple the event emission process from the 
	underlying implementation. This decoupling promotes flexibility, adaptability, and adheres to the
	[Open-Closed principle](https://www.cs.utexas.edu/users/downing/papers/OCP-1996.pdf), allowing 
	the implementation of custom event emitters without impacting existing consumers.
</p>

<p style='text-align: justify;' markdown>
	&emsp;&emsp;The `EventEmitter` presents a unified API with two key methods: `emit()` and `_process()`. These methods
	can be used in both synchronous and asynchronous contexts to emit events and handle their emission. The `emit()`
	method is used to invoke an event, while the `_process()` method is an abstract method responsible for processing 
	the execution of the emitted event.
</p>

### Built-in Event Emitters

<p style='text-align: justify;' markdown>
	&emsp;&emsp;Pyventus includes several [*built-in*](../../getting-started.md/#optional-dependencies) event emitters 
	by default. For instance, the `AsyncIOEventEmitter`	leverages the `AsyncIO` framework to handle the execution of
	event emissions, while the `RQEventEmitter`	utilizes Redis Queue pub/sub system with workers to manage the 
	execution of event emissions.
</p>

!!! info "Driving Innovation Through Collaboration"

    <p style='text-align: justify;' markdown>
    Pyventus is an open source project that welcomes community involvement. If you wish to contribute additional
    event emitters, improvements, or bug fixes, please check the [Contributing](../../contributing.md) section for
    guidelines on collaborating. Together, we can further the possibilities of event-driven development.
    </p>

## Custom Event Emitters

<p style='text-align: justify;' markdown>
	&emsp;&emsp;Pyventus provides a powerful abstraction layer for creating custom event emitters, allowing you to
	tailor their behavior and capabilities to suit your specific needs. In this section, we will guide you through
	the process of creating a custom event emitter specifically designed for the [FastAPI](https://fastapi.tiangolo.com/)
	framework.
</p>

<p style='text-align: justify;' markdown>
	&emsp;&emsp;The objective is to leverage FastAPI's [BackgroundTasks](https://fastapi.tiangolo.com/reference/background/)
	feature to efficiently process the execution of event emissions within your FastAPI application. Before we jump into 
	the	implementation details, make sure you have FastAPI properly [installed](https://fastapi.tiangolo.com/?h=#installation)
	and set up in your development environment.
</p>

### Defining and Implementing the Custom Event Emitter Class

<p style='text-align: justify;' markdown>
	&emsp;&emsp;To create the custom event emitter for FastAPI, we'll define a class called `FastAPIEventEmitter`. This
	class will extend the base `EventEmitter` class and implement the abstract `_process()` method using the
	FastAPI's background tasks to handle the event emission properly.
</p>

```Python linenums="1" hl_lines="6 10-11 13-14"
from fastapi import BackgroundTasks

from pyventus import EventEmitter, EventLinker


class FastAPIEventEmitter(EventEmitter):
    """A custom event emitter that uses the FastAPI background tasks."""

    def __init__(self, background_tasks: BackgroundTasks):
        super().__init__(event_linker=EventLinker, debug=False)
        self._background_tasks = background_tasks  # (1)!

    def _process(self, event_emission: EventEmitter.EventEmission) -> None:
        self._background_tasks.add_task(event_emission)  # (2)!
```

1. Stores the FastAPI background tasks object.
2. Executes the event handler callbacks as background tasks.

<p style='text-align: justify;' markdown>
	Once the custom event emitter is defined, you can integrate it into your code as follows:
</p>

```Python linenums="15" hl_lines="1 10 11 15-18 20"
@EventLinker.on("ConsolePrintEvent")
async def handle_console_print_event(message: str):
    await sleep(randint(0, 3))  # (1)!
    print(message)


app = FastAPI()


@app.get("/print")
async def console_print_endpoint(background_tasks: BackgroundTasks):
    """ FastAPI endpoint that triggers the console_print event. """

    def app_service(event_emitter: EventEmitter) -> None:
        event_emitter.emit(
	        event="ConsolePrintEvent",
	        message=f"\n{type(event_emitter).__name__}",
        )

    fastapi_event_emitter = FastAPIEventEmitter(background_tasks)
    app_service(event_emitter=fastapi_event_emitter)

    return {"message": "Console print triggered!"}
```

1. Simulate a random delay.

??? example "To test the custom event emitter integration follow these steps..."

    <p style='text-align: justify;' markdown>
    	[Run the server](https://fastapi.tiangolo.com/#run-it) with:
    </p>

    ```console
    uvicorn main:app --reload
    ```

    <p style='text-align: justify;' markdown>
    	Open your browser at [http://127.0.0.1:8000/print](http://127.0.0.1:8000/print). You will see the JSON
    	response as:
    </p>

    ```JSON
    { "message": "Console print triggered!" }
    ```
    <p style='text-align: justify;' markdown>
    	And also you are going see the outputs of the event emitter in the console logs as:
    </p>

    ```console
    INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
    INFO:     Started reloader process [28720]
    INFO:     Started server process [28722]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    INFO:     127.0.0.1:52391 - "GET /print HTTP/1.1" 200 OK

    FastAPIEventEmitter
    ```

!!! tip "Official `FastAPIEventEmitter` Integration"

    <p style='text-align: justify;' markdown>
    In case you're interested in integrating Pyventus with FastAPI, you can refer to the official Pyventus
    [*FastAPI Event Emitter*](../../learn/emitters/fastapi/index.md) implementation.
    </p>

## Runtime Flexibility

<p style='text-align: justify;' markdown>
	&emsp;&emsp;Another key feature of the Pyventus `EventEmitter` is the decoupling of event dispatching from the
	underlying implementation that processes the event handlers. This, combined with the `EventLinker`, allows
	you to change the event emitter at runtime without reconfiguring all the connections or any complex logic. We can
	use the base `EventEmitter` as a `dependency` and then change the concrete instance to suit your needs. Let's
	demonstrate this using the `AsyncIOEventEmitter` and `ExecutorEventEmitter`:
</p>

```Python linenums="1" hl_lines="10-11 14 16"
from pyventus import EventLinker, EventEmitter, AsyncIOEventEmitter, ExecutorEventEmitter


@EventLinker.on("GreetEvent")
def handle_greet_event(name: str = "World"):
    print(f"Hello, {name}!")


if __name__ == "__main__":
    def main(event_emitter: EventEmitter) -> None:
        event_emitter.emit("GreetEvent", name=type(event_emitter).__name__)


    main(event_emitter=AsyncIOEventEmitter())
    with ExecutorEventEmitter() as executor_event_emitter:
        main(event_emitter=executor_event_emitter)
```

<p style='text-align: justify;' markdown>
	&emsp;&emsp;In the example above, we defined a helper function `handle_greet_event` that accepts an `EventEmitter`
	instance as a parameter. This allows us to dynamically switch between the `AsyncIOEventEmitter` and the
	`ExecutorEventEmitter` depending on our requirements. This flexibility enables us to adapt the event
	emitter implementation at runtime without modifying the core application logic.
</p>

## Using Custom Event Linkers

<p style='text-align: justify;' markdown>
	&emsp;&emsp;By default, event emitters come with the base `EventLinker` registry assigned to the `event_linker` 
	property. However, you have the flexibility to specify the `EventLinker` class that will be used by the 
	`EventEmitter`. To configure this option, simply manually set the EventLinker class in the constructor.
</p>

```Python linenums="1" hl_lines="4 9 14 19"
from pyventus import EventEmitter, EventLinker, AsyncIOEventEmitter


class UserEventLinker(EventLinker, max_event_handlers=10):
    """ EventLinker for User's events only """
    pass  # Additional logic can be added here if needed...


@UserEventLinker.once("PasswordResetEvent")
async def handle_users_password_reset_event(email: str):
    print("User's PasswordResetEvent received!")


@EventLinker.once("PasswordResetEvent")
async def handle_any_password_reset_event(email: str):
    print("Any PasswordResetEvent received!")


event_emitter: EventEmitter = AsyncIOEventEmitter(event_linker=UserEventLinker)
event_emitter.emit("PasswordResetEvent", "example@email.com")
```

<p style='text-align: justify;' markdown>
	&emsp;&emsp;In the example above, we have assigned a custom event linker to the specific class of the `EventEmitter`.
	When we emit the `PasswordResetEvent`, we can see that only the `handle_users_password_reset_event()`, which was
	registered within the `UserEventLinker` namespace, gets triggered and removed. The `handle_any_password_reset_event()`
	callback, registered in a different `EventLinker` context, does not get triggered.
</p>

## Debug Mode

<p style='text-align: justify;' markdown>
	&emsp;&emsp;Pyventus' `EventEmitter` offers a useful debug mode feature to help you understand the flow of events
	and troubleshoot your event-driven application. You can enable debug mode in the `EventEmitter` using the following
	options:
</p>

### Global Debug Mode

<p style='text-align: justify;' markdown>
	&emsp;&emsp;By default, Pyventus makes use of Python's global debug tracing feature. To activate the global debug
	mode, simply run your code in an IDE's debugger mode. This allows you to observe the execution of events and trace
	their paths.
</p>

<p align="center">
   <img src="../../../images/examples/debug-mode-example.png" alt="Pyventus" width="900px">
</p>

### Instance Debug Flag

<p style='text-align: justify;' markdown>
    &emsp;&emsp;Alternatively, if you want to enable or disable debug mode for a specific `EventEmitter` instance, you
	can use the `debug` flag provided by the concrete implementation. Setting the `debug` flag to `True` enables
	debug mode for that instance, while setting it to `False` disables debug mode. Here's an example:
</p>

=== "Debug flag `On`"

    ```Python linenums="1" hl_lines="2"
    # Enable debug mode for a specific EventEmitter instance
    event_emitter: EventEmitter = AsyncIOEventEmitter(debug=True)
    event_emitter.emit("Hello", "Pyventus")
    ```

=== "Debug flag `Off`"

    ```Python linenums="1" hl_lines="2"
    # Disable debug mode for a specific EventEmitter instance
    event_emitter: EventEmitter = AsyncIOEventEmitter(debug=False)
    event_emitter.emit("Hello", "Pyventus")
    ```

## Best Practices

<p style='text-align: justify;' markdown>
	&emsp;&emsp;To fully leverage the power of the `EventEmitter`, it is recommended to **use the base** `EventEmitter` **as a
	dependency** instead of any concrete implementation. This allows you to easily switch between different event
	emitter implementations at runtime, providing flexibility and adaptability to your code.
</p>

## Recap

<p style='text-align: justify;' markdown>
	&emsp;&emsp;In this tutorial, we learned about the `EventEmitter` component and its role in dispatching events and
	triggering associated callbacks. We explored the base `EventEmitter` class, its unified async/sync API, and
	the process of creating custom event emitters. We also covered the usage of custom event linkers, best
	practices for using the `EventEmitter`, and the debug mode options provided by Pyventus.
</p>

<br>
