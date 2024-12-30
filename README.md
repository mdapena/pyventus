[//]: # "--------------------------------------------------------------------------------------------------------------"

<br>
<p align="center">
   <img src="https://raw.githubusercontent.com/mdapena/pyventus/refs/heads/master/docs/images/logo/pyventus-logo-name-slogan.svg" alt="Pyventus" width="750px">
</p>
<br>

[//]: # "--------------------------------------------------------------------------------------------------------------"

<p align="center">
    <a href="https://github.com/mdapena/pyventus/actions?query=workflow%3ATests+event%3Apush+branch%3Amaster" target="_blank">
        <img src="https://github.com/mdapena/pyventus/actions/workflows/run-tests.yml/badge.svg?branch=master" alt="Tests">
    </a>
    <a href="https://github.com/mdapena/pyventus/actions?query=workflow%3ADocs+event%3Apush+branch%3Amaster" target="_blank">
        <img src="https://github.com/mdapena/pyventus/actions/workflows/deploy-docs.yml/badge.svg?branch=master" alt="Docs">
    </a>
    <a href="https://coveralls.io/github/mdapena/pyventus?branch=master" target="_blank">
        <img src="https://coveralls.io/repos/github/mdapena/pyventus/badge.svg?branch=master" alt="Coverage Status"/>
    </a>
    <a href="https://pypi.org/project/pyventus" target="_blank">
        <img src="https://img.shields.io/pypi/v/pyventus?color=0097a8" alt="Package Version">
    </a>
    <a href="https://pypi.org/project/pyventus" target="_blank">
        <img src="https://img.shields.io/pypi/pyversions/pyventus?color=0097a8" alt="Supported Python Versions">
    </a>
    <a href="https://pypi.org/project/pyventus" target="_blank">
        <img src="https://img.shields.io/pypi/dm/pyventus.svg?color=0097a8" alt="Monthly Downloads">
    </a>
</p>

[//]: # "--------------------------------------------------------------------------------------------------------------"

---

**Documentation**: <a href="https://mdapena.github.io/pyventus" target="_blank">https://mdapena.github.io/pyventus</a>

**Source Code**: <a href="https://github.com/mdapena/pyventus" target="_blank">https://github.com/mdapena/pyventus</a>

---

[//]: # "--------------------------------------------------------------------------------------------------------------"

<p style="text-align: justify;">
    &emsp;&emsp;Pyventus is a powerful Python library for event-driven and reactive programming, designed to simplify the development of asynchronous and event-based applications in Python.
</p>

[//]: # "--------------------------------------------------------------------------------------------------------------"

## Key Features

<p style="text-align: justify;">
    Pyventus offers several key features, such as:
</p>

<ul style="text-align: justify;">

<li><b>Event-Driven & Reactive Programming</b> ─
Whether you opt for an event-driven design or a reactive approach, Pyventus lets you select the paradigm that best fits your architecture.
</li>

<li><b>High Performance</b> ─
Pyventus is designed from the ground up with a focus on efficiency, taking into account optimizations for time complexity, memory usage, and Python-specific features.
</li>

<li><b>Sync and Async Support</b> ─
Whether your code is synchronous or asynchronous, Pyventus allows you to seamlessly work with both sync and async callables, as well as access its API from both contexts.
</li>

<li><b>Reliable Asynchronous Processing</b> ─
With Pyventus, you have full control over your asynchronous workflows, allowing you to customize how they are processed upon completion, whether they succeed or encounter errors.
</li>

<li><b>Comprehensive Documentation</b> ─
Pyventus offers a comprehensive documentation suite that includes API references, usage examples, and tutorials to effectively leverage all the features and capabilities of the library.
</li>

<li><b>Intuitive & User-Friendly API</b> ─
Pyventus provides a user-friendly API that simplifies the process of working with event-driven and reactive paradigms, enabling you to organize your code around discrete actions and their responses.
</li>

</ul>

[//]: # "--------------------------------------------------------------------------------------------------------------"

## Quick Start

<p style="text-align: justify;">
 &emsp;&emsp;Pyventus is published as a <a href="https://pypi.org/project/pyventus/" target="_blank">Python package</a> and can be installed using <code>pip</code>, ideally in a <a href="https://realpython.com/python-virtual-environments-a-primer/" target="_blank">virtual environment</a> for proper dependency isolation. To get started, open up a terminal and install Pyventus with the following command:
</p>

```console
pip install pyventus
```

<p style="text-align: justify;">
    &emsp;&emsp;Pyventus by default relies on the Python standard library and <b>requires Python 3.10 or higher</b> with no additional dependencies aside from <a href="https://pypi.org/project/typing-extensions/" target="_blank"><code>typing-extensions</code></a>, which is primarily used to support advanced typing features in older versions of Python. However, this package also includes alternative integrations to access additional features such as asynchronous processing with Redis Queue and Celery. For more information on this matter, please refer to the <a href="https://mdapena.github.io/pyventus/0.7/getting-started/#optional-dependencies">Optional Dependencies</a> section.
</p>

[//]: # "--------------------------------------------------------------------------------------------------------------"

## Basic Usage

<p style="text-align: justify;">
    &emsp;&emsp;Let’s begin with some introductory examples that will not only illustrate the core concepts and basic usage of the library but also provide a foundation for more complex scenarios.
</p>

[//]: # "--------------------------------------------------------------------------------------------------------------"

### A Simple Event-Driven Example

<p style="text-align: justify;">
    &emsp;&emsp;Starting with the event-driven paradigm, let's explore the capabilities of Pyventus through a simple event-based <code>Hello, World!</code> example, where you will learn how to subscribe to events and emit them within your application.
</p>

```Python title="Hello, World! Example" linenums="1"
from pyventus.events import AsyncIOEventEmitter, EventEmitter, EventLinker


@EventLinker.on("GreetEvent")
def handle_greet_event():
    print("Hello, World!")


event_emitter: EventEmitter = AsyncIOEventEmitter()
event_emitter.emit("GreetEvent")
```

<details markdown="1" class="tip">
<summary>You can also work with <code>async</code> functions and contexts...</summary>

```Python title="Hello, World! Example (Async version)" linenums="1" hl_lines="5"
from pyventus.events import AsyncIOEventEmitter, EventEmitter, EventLinker


@EventLinker.on("GreetEvent")
async def handle_greet_event():
    print("Hello, World!")


event_emitter: EventEmitter = AsyncIOEventEmitter()
event_emitter.emit("GreetEvent")
```

</details>

<p style="text-align: justify;">
    &emsp;&emsp;As we can see from the <code>Hello, World!</code> example, Pyventus follows a simple and intuitive workflow for defining and emitting events. Let’s recap the essential steps involved:
</p>

<ol style="text-align: justify;">
<li>
<b>Importing Necessary Components:</b>
We first imported the required components from the <code>events</code> module of Pyventus, which included the <code>EventLinker</code>, the <code>EventEmitter</code>, and the <code>AsyncIOEventEmitter</code> factory method.
</li>

<li>
<b>Linking Events to Callbacks:</b>
Next, we used the <code>@EventLinker.on()</code> decorator to define and link the string event <code>GreetEvent</code> to the function <code>handle_greet_event()</code>, which will print <i>"Hello, World!"</i> to the console whenever the <code>GreetEvent</code> is emitted.
</li>

<li>
<b>Instantiating an Event Emitter:</b>
After that, and in order to trigger our event, we used the <code>AsyncIOEventEmitter</code> factory method to create an instance of the event emitter class, which in this case is preconfigured with the <code>AsyncIOProcessingService</code>.
</li>

<li>
<b>Triggering the Event:</b>
Finally, by using the <code>emit()</code> method of the event emitter instance, we triggered the <code>GreetEvent</code>, resulting in the execution of the <code>handle_greet_event()</code> callback.
</li>
</ol>

<p style="text-align: justify;">
    &emsp;&emsp;Having gained a clear understanding of the workflow showcased in the <code>Hello, World!</code> example, you are now well-equipped to explore more intricate event-driven scenarios and fully harness the capabilities of Pyventus in your own projects. For a deep dive into the package's functionalities, you can refer to the API and Learn sections.
</p>

[//]: # "--------------------------------------------------------------------------------------------------------------"

### A Simple Reactive Example

<p style="text-align: justify;">
    &emsp;&emsp;Now, let's take a look at the capabilities of Pyventus within the reactive paradigm through a simple example, where you will not only learn how to define observables and stream data over time, but also how to subscribe to them.
</p>

```Python title="Simple Counter Example" linenums="1"
from pyventus.reactive import as_observable_task, Completed


@as_observable_task
def simple_counter(stop: int):
    for count in range(1, stop + 1):
        yield count
    raise Completed


obs = simple_counter(stop=16)
obs.subscribe(
    next_callback=lambda val: print(f"Received: {val}"),
    complete_callback=lambda: print("Done!"),
)
obs()
```

<details markdown="1" class="tip">
<summary>You can also work with <code>async</code> functions and contexts...</summary>

```Python title="Simple Counter Example (Async version)" linenums="1" hl_lines="5"
from pyventus.reactive import as_observable_task, Completed


@as_observable_task
async def simple_counter(stop: int):
    for count in range(1, stop + 1):
        yield count
    raise Completed


obs = simple_counter(stop=16)
obs.subscribe(
    next_callback=lambda val: print(f"Received: {val}"),
    complete_callback=lambda: print("All done!"),
)
obs()
```

</details>

<p style="text-align: justify;">
    &emsp;&emsp;As shown in the <code>Simple Counter</code> example, Pyventus follows a simple and intuitive workflow for defining observables and streaming data to subscribers. Let’s recap the essential steps involved:
</p>

<ol style="text-align: justify;">
<li>
<b>Importing Necessary Components:</b>
We first imported the required components from the <code>reactive</code> module of Pyventus, which included the <code>@as_observable_task</code> decorator and the <code>Completed</code> signal.
</li>

<li>
<b>Defining Observables:</b>
After that, and using the <code>@as_observable_task</code> decorator in conjunction with the <code>simple_counter()</code> function, we defined our observable task, which, once executed, will yield a count from one up to the specified number and raise a <code>Completed</code> signal when done.
</li>

<li>
<b>Instantiating Observables:</b>
Then, we called the <code>simple_counter()</code> function to instantiate the observable task, so that we can subscribe to it and control its execution as needed.
</li>

<li>
<b>Subscribing to Observables:</b>
Next, we added a subscriber to the observable instance by calling its <code>subscribe()</code> method and passing the corresponding callbacks. In this case, we used two lambda functions: one to print the received values and another to indicate when the observable has completed emitting values.
</li>

<li>
<b>Executing Observables:</b>
Finally, and in order to initiate the execution of the observable, we called its instance, which resulted in the execution of the <code>simple_counter()</code> function and the streaming of its results.
</li>
</ol>

<p style="text-align: justify;">
    &emsp;&emsp;With a clear understanding of the workflow showcased in the <code>Simple Counter</code> example, you are now well-equipped to explore more intricate reactive scenarios and fully harness the capabilities of Pyventus in your own projects. For a deep dive into the package's functionalities, you can refer to the API and Learn sections.
</p>

[//]: # "--------------------------------------------------------------------------------------------------------------"

## Practical Examples

<p style="text-align: justify;">
    &emsp;&emsp;To truly see Pyventus in action, let’s explore some practical examples that will not only illustrate specific use cases of the library but also showcase its various features and demonstrate how to use them effectively.
</p>

### Dynamic Voltage Monitoring: An Event-Driven Perspective

<p style="text-align: center;">
    <a href="https://unsplash.com/photos/macro-photography-of-black-circuit-board-FO7JIlwjOtU?utm_content=creditShareLink&utm_medium=referral&utm_source=unsplash" target="_blank">
        <img style="border-radius: 0.5rem;" src="https://raw.githubusercontent.com/mdapena/pyventus/refs/heads/master/docs/images/examples/black-circuit-board.jpg" alt="Macro photography of a black circuit board illustrating a voltage sensor in action.">
    </a>
</p>

<p style="text-align: justify;">
    &emsp;&emsp;A common aspect found in many systems is the need to monitor and respond to changes in sensor data. Whether it involves pressure, temperature, or voltage, capturing and reacting accordingly to sensor readings is crucial for any related process.
</p>
<p style="text-align: justify;">
    &emsp;&emsp;In this practical example, we will focus on voltage sensors, where timely detection of low or high voltage conditions can prevent equipment damage and ensure system reliability. However, designing a sensor architecture that is both easy to extend and flexible can be challenging, especially if we want users to simply attach their logic without needing to understand or modify the underlying implementation. This complexity also increases if we aim for an architecture that enables a proper separation of concerns.
</p>

<p style="text-align: justify;">
    &emsp;&emsp;One way to effectively address this challenge is by implementing an event-driven architecture, where each voltage sensor encapsulates its own logic for reading values and only exposes a series of events that users can utilize to attach their domain logic. To translate this into code, we will define a <code>VoltageSensor</code> class that reads voltage levels and emits events based on predefined thresholds using Pyventus. The code below illustrates the implementation of this use case.
</p>

```Python title="Dynamic Voltage Monitoring (Event-Driven Implementation)" linenums="1" hl_lines="4 9 14 27-30 35-36 41-42 47-48 55"
import asyncio
import random

from pyventus.events import AsyncIOEventEmitter, EventEmitter, EventLinker


class VoltageSensor:

    def __init__(self, name: str, low: float, high: float, event_emitter: EventEmitter) -> None:
        # Initialize the VoltageSensor object with the provided parameters
        self._name: str = name
        self._low: float = low
        self._high: float = high
        self._event_emitter: EventEmitter = event_emitter

    async def __call__(self) -> None:
        # Start voltage readings for the sensor
        print(f"Starting voltage readings for: {self._name}")
        print(f"Low: {self._low:.3g}v | High: {self._high:.3g}v\n-----------\n")

        while True:
            # Simulate sensor readings
            voltage: float = random.uniform(0, 5)
            print("\tSensor Reading:", "\033[32m", f"{voltage:.3g}v", "\033[0m")

            # Emit events based on voltage readings
            if voltage < self._low:
                self._event_emitter.emit("LowVoltageEvent", sensor=self._name, voltage=voltage)
            elif voltage > self._high:
                self._event_emitter.emit("HighVoltageEvent", sensor=self._name, voltage=voltage)

            await asyncio.sleep(1)


@EventLinker.on("LowVoltageEvent")
def handle_low_voltage_event(sensor: str, voltage: float):
    print(f"🪫 Starting low-voltage protection for '{sensor}'. ({voltage:.3g}v)\n")
    # Perform action for low voltage...


@EventLinker.on("HighVoltageEvent")
def handle_high_voltage_event(sensor: str, voltage: float):
    print(f"⚡ Starting high-voltage protection for '{sensor}'. ({voltage:.3g}v)\n")
    # Perform action for high voltage...


@EventLinker.on("LowVoltageEvent", "HighVoltageEvent")
async def handle_voltage_event(sensor: str, voltage: float):
    print(f"\033[31m\nSensor '{sensor}' out of range.\033[0m (Voltage: {voltage:.3g})")
    # Perform notification for out of range voltage...


async def main():
    # Initialize the sensor and run the sensor readings
    sensor = VoltageSensor(name="CarSensor", low=0.5, high=3.9, event_emitter=AsyncIOEventEmitter())
    await asyncio.gather(sensor(), )  # Add new sensors inside the 'gather' for multi-device monitoring


asyncio.run(main())
```

[//]: # "--------------------------------------------------------------------------------------------------------------"

### Non-Blocking HTTP Fetcher: A Responsive Approach

<p style="text-align: center;">
    <a href="https://unsplash.com/photos/a-rack-of-electronic-equipment-in-a-dark-room-OnI_TNcIv9U" target="_blank">
        <img style="border-radius: 0.5rem;" src="https://raw.githubusercontent.com/mdapena/pyventus/refs/heads/master/docs/images/examples/rack-of-electronic-equipment.jpg" alt="A set of interconnected electronic devices in a dark room.">
    </a>
</p>

<p style="text-align: justify;">
    &emsp;&emsp;In today's interconnected world, retrieving information from the network is essential for many applications. Whether through WebSocket connections, RESTful APIs, or HTTP requests, these methods facilitate vital data exchange. However, blocking network retrievals can severely impact user experience, making it imperative for applications to remain responsive.
</p>

<p style="text-align: justify;">
    &emsp;&emsp;In this practical example, we will explore the design and implementation of a non-blocking HTTP getter function, along with its integration into a console-style application that mimics the behavior of a simplified web browser. While there are various mechanisms for implementing non-blocking HTTP fetchers, such as Python threads or the asyncio library, we will leverage the reactive paradigm of Pyventus due to its readability, declarative style, and ease of implementation.
</p>

<p style="text-align: justify;">
    &emsp;&emsp;To accomplish this, we will first define a basic blocking HTTP function called <code>http_get()</code>. This function will then be transformed into an observable using the <code>@as_observable_task</code> decorator from Pyventus, allowing us to attach subscribers for result notifications. Finally, we will utilize the <code>ThreadPoolExecutor</code> for concurrent execution of the observables, enabling us to handle multiple requests seamlessly while maintaining an interactive user experience.
</p>

```Python title="Non-Blocking HTTP Fetcher (Reactive Implementation)" linenums="1" hl_lines="5 8-9 51 54 56-57 61-62 66"
from concurrent.futures import ThreadPoolExecutor
from http.client import HTTPConnection, HTTPException, HTTPResponse, HTTPSConnection
from urllib.parse import ParseResult, urlparse

from pyventus.reactive import as_observable_task


@as_observable_task
def http_get(url: str) -> str:
    """Perform an HTTP GET request and return the response data."""
    parsed_url: ParseResult = urlparse(url)  # Parse the URL

    # Create a connection based on the URL scheme (HTTP or HTTPS)
    if parsed_url.scheme == "https":
        connection: HTTPConnection = HTTPSConnection(parsed_url.netloc)
    else:
        connection: HTTPConnection = HTTPConnection(parsed_url.netloc)

    # Send the request, retrieve the response, and close the connection
    connection.request("GET", parsed_url.path)
    response: HTTPResponse = connection.getresponse()
    data: str = response.read().decode()
    connection.close()

    # Raise an exception for HTTP errors; otherwise, return the response
    if response.status >= 400:
        raise HTTPException(response.status, data)
    return data


def main():
    print(
        "🌐  Welcome to the Reactive HTTP Fetcher!\n\n💡  Try searching for:\n"
        "    1. - https://httpbin.org/get\n"
        "    2. - https://httpbin.org/uuid\n"
        "    3. - https://httpbin.org/ip\n"
        "    4. - https://httpbin.org/404"
    )

    prompt = "\n🔗  Enter the URL (Type '\033[36mexit\033[0m' to quit): "
    metrics = {"success_count": 0, "error_count": 0}  # Initialize metrics
    executor = ThreadPoolExecutor()  # Create a thread pool for concurrent execution

    while True:
        # Get user input
        url = input(prompt)
        if url.lower() == "exit":
            break

        # Call the HTTP function, which returns an observable
        obs = http_get(url)

        # Subscribe to the observable using a subscription context
        with obs.subscribe() as subctx:

            @subctx.on_next
            def next(result: str) -> None:
                metrics["success_count"] += 1  # Increment success count
                print(f"\r{' ' * len(prompt)}\r✅  HTTPResponse: {result!r}\n", end=f"{prompt}")

            @subctx.on_error
            def error(error: Exception) -> None:
                metrics["error_count"] += 1  # Increment error count
                print(f"\r{' ' * len(prompt)}\r⚠️   HTTPException: {error!r}\n", end=f"{prompt}")

        obs(executor)  # Execute the observable with the thread pool
        print(f"🔍  Requested URL: \033[32m{url!r}\033[0m \n⏳  Fetching data... ")

    # Shutdown the executor
    executor.shutdown()

    # Print summary of requests
    print(
        f"\n🎯  Summary:\n"
        f"    - Total Requests: {metrics['success_count'] + metrics['error_count']}\n"
        f"    - Successful Requests: \033[32m{metrics['success_count']}\033[0m\n"
        f"    - Error Requests: \033[31m{metrics['error_count']}\033[0m"
    )


main()
```

[//]: # "--------------------------------------------------------------------------------------------------------------"

## Event-Driven Programming: Key Highlights of Pyventus

<p style="text-align: justify;">
    &emsp;&emsp;Alongside the standard functionalities of event-driven programming, Pyventus also introduces some unique aspects that set it apart from other implementations. In this section, we will cover some of these key features and how to use them effectively.
</p>

[//]: # "--------------------------------------------------------------------------------------------------------------"

-   <p style="text-align: justify;"><a href="#ep-event-objects" name="ep-event-objects" title="Permanent link">Event Objects</a> ─ 
        Besides supporting string-based events, as we've seen in previous examples, Pyventus also supports Event Objects, which provide a structured way to define events and encapsulate relevant data payloads.
    </p>

    ```Python linenums="1" hl_lines="1-2 7-8 16-19"
    @dataclass  # Define a Python dataclass to represent an event and its payload.
    class OrderCreatedEvent:
        order_id: int
        payload: dict


    @EventLinker.on(OrderCreatedEvent)  # Use the event class to attach subscribers.
    def handle_order_created_event(event: OrderCreatedEvent):
        # The event instance is automatically passed as the first argument.
        # In methods with self or cls, the event is passed after those arguments.
        print(f"Event Object: {event}")


    event_emitter: EventEmitter = AsyncIOEventEmitter()
    event_emitter.emit(
        event=OrderCreatedEvent(  # Emit an instance of the event!
            order_id=6452879,
            payload={},
        ),
    )
    ```

[//]: # "--------------------------------------------------------------------------------------------------------------"

-   <p style="text-align: justify;"><a href="#ep-global-events" name="ep-global-events" title="Permanent link">Global Events</a> ─ 
        In addition to Event Objects and string-based events, Pyventus also provides support for global events, which are particularly useful for implementing cross-cutting concerns such as logging, monitoring, and analytics. By subscribing event callbacks to <code>...</code>, you can capture all events that may occur within that specific <code>EventLinker</code> context.
    </p>

    ```Python linenums="1" hl_lines="1-2"
    @EventLinker.on(...)
    def logging(*args, **kwargs):
        print(f"Logging:\n- Args: {args}\n- Kwargs: {kwargs}")


    event_emitter: EventEmitter = AsyncIOEventEmitter()
    event_emitter.emit("AnyEvent", name="Pyventus")
    ```

[//]: # "--------------------------------------------------------------------------------------------------------------"

-   <p style="text-align: justify;"><a href="#ep-success-and-error-handling" name="ep-success-and-error-handling" title="Permanent link">Success and Error Handling</a> ─ 
        With Pyventus, you can customize how events are handled upon completion, whether they succeed or encounter errors. This customization is achieved through the configuration of the success and failure callbacks in the event workflow definition, which is done during the subscription process.
    </p>

    ```Python linenums="1" hl_lines="4 6-7 10-11 14-15"
    from pyventus.events import AsyncIOEventEmitter, EventEmitter, EventLinker

    # Create a subscription context for the "DivisionEvent" event
    with EventLinker.on("DivisionEvent") as subctx:

        @subctx.on_event
        def divide(a: float, b: float) -> float:
            return a / b

        @subctx.on_success
        def handle_success(result: float) -> None:
            print(f"Division result: {result:.3g}")

        @subctx.on_failure
        def handle_failure(e: Exception) -> None:
            print(f"Oops, something went wrong: {e}")


    event_emitter: EventEmitter = AsyncIOEventEmitter()  # Create an event emitter
    event_emitter.emit("DivisionEvent", a=1, b=0)  # Example: Division by zero
    event_emitter.emit("DivisionEvent", a=1, b=2)  # Example: Valid division
    ```

    <details markdown="1" class="tip">
    <summary>You can also set up your callbacks using the <code>subscribe()</code> method...</summary>

    <p style="text-align: justify;">
        &emsp;&emsp;Alternatively, for more straightforward definitions, such as lambda functions, or when you have existing functions defined elsewhere in your code, you can utilize the <code>subscribe()</code> method to set up these callbacks.
    </p>

    ```Python linenums="1" hl_lines="3-8"
    from pyventus.events import AsyncIOEventEmitter, EventEmitter, EventLinker

    EventLinker.subscribe(
        "DivisionEvent",
        event_callback=lambda a, b: a / b,
        success_callback=lambda result: print(f"Division result: {result:.3g}"),
        failure_callback=lambda e: print(f"Oops, something went wrong: {e}"),
    )

    event_emitter: EventEmitter = AsyncIOEventEmitter()  # Create an event emitter
    event_emitter.emit("DivisionEvent", a=1, b=0)  # Example: Division by zero
    event_emitter.emit("DivisionEvent", a=1, b=2)  # Example: Valid division
    ```

    </details>

[//]: # "--------------------------------------------------------------------------------------------------------------"

-   <p style="text-align: justify;"><a href="#ep-sync-and-async-support" name="ep-sync-and-async-support" title="Permanent link">Sync and Async Support</a> ─ 
        Pyventus is designed from the ground up to seamlessly support both synchronous and asynchronous programming models. Its unified sync/async API allows you to define event callbacks as either <code>sync</code> or <code>async</code> callables, as well as emit events from both contexts.
    </p>

    ```Python linenums="1" hl_lines="2 7"
    @EventLinker.on("MyEvent")
    def sync_event_callback():
        pass  # Synchronous event handling


    @EventLinker.on("MyEvent")
    async def async_event_callback():
        pass  # Asynchronous event handling
    ```

    <details markdown="1" class="tip">
    <summary>You can optimize the execution of your callbacks based on their workload...</summary>

    <p style="text-align: justify;">
        &emsp;&emsp;By default, event subscribers in Pyventus are executed concurrently during an event emission, running their <code>sync</code> and <code>async</code> callbacks as defined. However, if you have a <code>sync</code> callback that involves I/O or non-CPU bound operations, you can enable the <code>force_async</code> parameter to offload it to a thread pool, ensuring optimal performance and responsiveness. The offloading process is handled by the <a href="https://docs.python.org/3/library/asyncio-task.html#running-in-threads" target="_blank"><code>asyncio.to_thread()</code></a> function.
    </p>

    ```Python linenums="1" hl_lines="1"
    @EventLinker.on("BlockingIO", force_async=True)
    def blocking_io():
        print(f"start blocking_io at {time.strftime('%X')}")
        # Note that time.sleep() can be replaced with any blocking
        # IO-bound operation, such as file operations.
        time.sleep(1)
        print(f"blocking_io complete at {time.strftime('%X')}")
    ```

    </details>

    ```Python linenums="1" hl_lines="3 8"
    def sync_function(event_emitter: EventEmitter):
        # Emitting events from sync functions
        event_emitter.emit("MyEvent")


    async def async_function(event_emitter: EventEmitter):
        # Emitting events from async functions
        event_emitter.emit("MyEvent")
    ```

    <details markdown="1" class="info">
    <summary>Considerations on the processing of event emissions...</summary>
    <p style="text-align: justify;">
        &emsp;&emsp;It's important to note that, while Pyventus provides a unified sync/async API, the processing of each event emission will depend on the concrete implementation of the <code>ProcessingService</code> used in the event emitter. For example, an event emitter configured with the <code>AsyncIOProcessingService</code> will leverage the <code>AsyncIO</code> framework to handle the execution of the event emission, whereas other implementations may structure their propagation differently.
    </p>
    </details>

[//]: # "--------------------------------------------------------------------------------------------------------------"

-   <p style="text-align: justify;"><a href="#ep-runtime-flexibility" name="ep-runtime-flexibility" title="Permanent link">Runtime Flexibility</a> ─ 
        At its core, Pyventus utilizes a modular event emitter design that, along with the <code>EventLinker</code>, allows you to change the event emitter at runtime without needing to reconfigure all subscriptions or apply complex logic.
    </p>

    ```Python linenums="1" hl_lines="11-12 17-18"
    from concurrent.futures import ThreadPoolExecutor

    from pyventus.events import AsyncIOEventEmitter, EventEmitter, EventLinker, ExecutorEventEmitter


    @EventLinker.on("Event")
    def handle_event(msg: str):
        print(msg)


    def main(event_emitter: EventEmitter) -> None:
        event_emitter.emit("Event", msg=f"{event_emitter}")


    if __name__ == "__main__":
        executor = ThreadPoolExecutor()
        main(event_emitter=AsyncIOEventEmitter())
        main(event_emitter=ExecutorEventEmitter(executor))
        executor.shutdown()
    ```

    <p style="margin-top: -1rem;"></p>

[//]: # "--------------------------------------------------------------------------------------------------------------"

## Reactive Programming: Key Highlights of Pyventus

<p style="text-align: justify;">
    &emsp;&emsp;In addition to the standard functionalities of reactive programming, Pyventus also provides some unique aspects that set it apart from other implementations. In this section, we will explore some of these key features and how to use them effectively.
</p>

[//]: # "--------------------------------------------------------------------------------------------------------------"

-   <p style="text-align: justify;"><a href="#rp-python-callables-as-observable-tasks" name="rp-python-callables-as-observable-tasks" title="Permanent link">Python Callables as Observable Tasks</a> ─
        Whether you are working with generators or regular functions, Pyventus allows you to easily convert any Python callable into an observable task. These tasks are specialized observables that encapsulate a unit of work and provide a mechanism for streaming their results to a series of subscribers.
    </p>

    ```Python linenums="1" hl_lines="1-2 5"
    @as_observable_task
    def compute_square(n):
        return n * n

    obs = compute_square(2)
    obs.subscribe(print)
    obs()
    ```

    <details markdown="1" class="tip">
    <summary>You can also work with <code>async</code> functions...</summary>

    ```Python linenums="1" hl_lines="1-2 6"
    @as_observable_task
    async def fetch_data():
        await asyncio.sleep(1)
        return {"data": "Sample Data"}

    obs = fetch_data()
    obs.subscribe(print)
    obs()
    ```

    </details>

    ```Python linenums="1" hl_lines="1-2 4 8"
    @as_observable_task
    def simple_counter(stop: int):
        for count in range(1, stop + 1):
            yield count
        raise Completed


    obs = simple_counter(stop=16)
    obs.subscribe(print)
    obs()
    ```

    <details markdown="1" class="tip">
    <summary>You can also work with <code>async</code> generators...</summary>

    ```Python linenums="1" hl_lines="1-2 5 8"
    @as_observable_task
    async def async_counter(stop: int):
        for count in range(1, stop + 1):
            await asyncio.sleep(0.25)
            yield count
        raise Completed

    obs = async_counter(stop=16)
    obs.subscribe(print)
    obs()
    ```

    </details>

[//]: # "--------------------------------------------------------------------------------------------------------------"

-   <p style="text-align: justify;"><a href="#rp-multicast-support" name="rp-multicast-support" title="Permanent link">Multicast Support</a> ─
        Observables in Pyventus are designed from the ground up to efficiently support both unicast and multicast scenarios. So, it doesn't matter if you need to work with either single or multiple subscribers; Pyventus allows you to utilize these notification models and even optimizes the processing of each to ensure optimal performance.
    </p>

    ```Python linenums="1" hl_lines="9-11"
    @as_observable_task
    def simple_counter(stop: int):
        for count in range(1, stop + 1):
            yield count
        raise Completed


    obs = simple_counter(stop=16)
    obs.subscribe(next_callback=lambda val: print(f"Subscriber 1 - Received: {val}"))
    obs.subscribe(next_callback=lambda val: print(f"Subscriber 2 - Received: {val}"))
    obs.subscribe(next_callback=lambda val: print(f"Subscriber 3 - Received: {val}"))
    obs()
    ```

[//]: # "--------------------------------------------------------------------------------------------------------------"

-   <p style="text-align: justify;"><a href="#rp-success-and-error-handling" name="rp-success-and-error-handling" title="Permanent link">Success and Error Handling</a> ─
    With Pyventus, you can customize how data streams are handled upon completion, whether they succeed or encounter errors. This customization is achieved through the configuration of the complete and error callbacks in the observer definition, which is done during the subscription process.
    </p>

    ```Python linenums="1" hl_lines="11-13"
    @as_observable_task
    async def interactive_counter():
        stop: int = int(input("Please enter a number to count up to: "))  # Can raise ValueError
        for count in range(1, stop + 1):
            yield count
        raise Completed


    obs = interactive_counter()
    obs.subscribe(
        next_callback=lambda val: print(f"Received: {val}"),
        error_callback=lambda err: print(f"Error: {err}"),
        complete_callback=lambda: print("All done!"),
    )
    obs()
    ```

[//]: # "--------------------------------------------------------------------------------------------------------------"

-   <p style="text-align: justify;"><a href="#rp-declarative-subscription-model" name="rp-declarative-subscription-model" title="Permanent link">Declarative Subscription Model</a> ─
        Alongside standard subscription models, such as using lambda functions or predefined callbacks, Pyventus also provides a declarative subscription model that allows you to not only define the observer's callbacks inline and in a step-by-step manner but also to do so right before the subscription takes place.
    </p>

    ```Python linenums="1"  hl_lines="1 3-4 7-8 11-12"
    with obs.subscribe() as subctx:

        @subctx.on_next
        def next(value: int) -> None:
            print(f"Received: {value}")

        @subctx.on_error
        def error(error: Exception) -> None:
            print(f"Error: {error}")

        @subctx.on_complete
        def complete() -> None:
            print("All done!")
    ```

    <details markdown="1" class="tip">
    <summary>You can also use the <code>subscribe()</code> method as a decorator...</summary>

    <p style="text-align: justify;">
        &emsp;&emsp;The <code>subscribe()</code> method, besides being used as a regular function and a context manager, can also be utilized as a decorator. When used this way, it creates and subscribes an observer, using the decorated function as its next callback.
    </p>

    ```Python linenums="1" hl_lines="1-2"
    @obs.subscribe()
    def next(value: int) -> None:
        print(f"Received: {value}")
    ```

    </details>

[//]: # "--------------------------------------------------------------------------------------------------------------"

-   <p style="text-align: justify;"><a href="#rp-simplified-execution-for-observable-tasks" name="rp-simplified-execution-for-observable-tasks" title="Permanent link">Simplified Execution for Observable Tasks</a> ─
        Having to explicitly call each observable task to initiate their execution can be tedious and easily overlooked, especially when working with multiple observables at the same time. However, by using observable tasks within a <code>with</code> statement block, you can avoid this manual work and enable what is known as their execution context, which will allow you to work with them as usual while ensuring that they are called upon exiting the context block.
    </p>

    ```Python linenums="1"  hl_lines="7"
    @as_observable_task
    def simple_counter(stop: int):
        for count in range(1, stop + 1):
            yield count
        raise Completed

    with simple_counter(stop=16) as obs:
        obs.subscribe(lambda val: print(f"Subscriber 1 - Received: {val}"))
        obs.subscribe(lambda val: print(f"Subscriber 2 - Received: {val}"))
    ```

-   <p style="text-align: justify;"><a href="#rp-thread-offloading-for-observable-tasks" name="rp-thread-offloading-for-observable-tasks" title="Permanent link">Thread Offloading for Observable Tasks</a> ─
        By default, the processing of each observable task is handled by the AsyncIO framework, either synchronously or asynchronously depending on the context. However, for multithreaded environments, Pyventus also provides support for running these observable tasks in separate threads.  
    </p>

    ```Python linenums="1" hl_lines="1 12 16 20"
    from concurrent.futures import ThreadPoolExecutor
    from pyventus.reactive import as_observable_task, Completed

    @as_observable_task
    def simple_counter(stop: int):
        for count in range(1, stop + 1):
            yield count
        raise Completed

    if __name__ == "__main__":

        with ThreadPoolExecutor() as executor:

            obs1 = simple_counter(16)
            obs1.subscribe(print)
            obs1(executor)

            obs2 = simple_counter(16)
            obs2.subscribe(print)
            obs2(executor)
    ```

    <details markdown="1" class="tip">
    <summary>Thread offloading is also available for the execution context of observable tasks...</summary>

    ```Python linenums="1" hl_lines="14 17"
    from concurrent.futures import ThreadPoolExecutor
    from pyventus.reactive import as_observable_task, Completed

    @as_observable_task
    def simple_counter(stop: int):
        for count in range(1, stop + 1):
            yield count
        raise Completed

    if __name__ == "__main__":

        with ThreadPoolExecutor() as executor:

            with simple_counter(16).to_thread(executor) as obs1:
                obs1.subscribe(print)

            with simple_counter(16).to_thread(executor) as obs2:
                obs2.subscribe(print)
    ```

    </details>

    <p style="margin-top: -1rem;"></p>

[//]: # "--------------------------------------------------------------------------------------------------------------"

## Additional Highlights

<p style="text-align: justify;">
    &emsp;&emsp;Beyond the core functionalities of event-driven and reactive programming, Pyventus also includes some additional features that are worth noting. In this section, we will explore these aspects and how to use them effectively.
</p>

[//]: # "--------------------------------------------------------------------------------------------------------------"

-   <p style="text-align: justify;"><a href="#ah-debugging-utilities" name="ah-debugging-utilities" title="Permanent link">Debugging Utilities</a> ─
        Debugging plays a crucial role in the development of asynchronous and event-driven applications, as it allows you to understand what’s going on under the hood and provides valuable insights when troubleshooting errors. For this reason, Pyventus offers a clear string representation of each component, along with a debug mode flag that lets you view the package's logs to better understand the processes at work.
    </p>

    <p style="text-align: center;">
        <img style="border-radius: 0.5rem;" src="https://raw.githubusercontent.com/mdapena/pyventus/refs/heads/master/docs/images/examples/debug-mode-example.png">
    </p>

[//]: # "--------------------------------------------------------------------------------------------------------------"

-   <p style="text-align: justify;"><a href="#ah-efficient-import-management" name="ah-efficient-import-management" title="Permanent link">Efficient Import Management</a> ─
        Pyventus encapsulates each paradigm into its own isolated package, so that you can not only have a clear boundary between event-driven and reactive programming features, but also apply Python import optimizations based on the required paradigm. For example, if you are only working with the events module of Pyventus and never import the reactive package, Python does not load it.
    </p>

<p style="margin-top: -1rem;"></p>

[//]: # "--------------------------------------------------------------------------------------------------------------"

## License

<p style="text-align: justify;">
    &emsp;&emsp;Pyventus is distributed as open-source software and is released under the <a href="https://choosealicense.com/licenses/mit/" target="_blank">MIT License</a>. For a detailed view of the license, please refer to the <a href="https://github.com/mdapena/pyventus/blob/master/LICENSE" target="_blank"><code>LICENSE</code></a> file located in the Pyventus repository.
</p>
