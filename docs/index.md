---
hide:
  - navigation
---

<style>
    .md-content .md-content__inner.md-typeset h1 { height: 0; margin: 0; color: transparent; }
    .md-content .md-content__inner.md-typeset::before { height: 0; } 
</style>


<br>


<p align="center">
   <img src="./images/logo/pyventus-logo-name-slogan.svg" alt="Pyventus" width="900px">
</p>

<br>

<p align="center">

<a href="https://github.com/mdapena/pyventus/actions?query=workflow%3ATests+event%3Apush+branch%3Amaster" target="_blank">
    <img src="https://github.com/mdapena/pyventus/actions/workflows/run-tests.yml/badge.svg?branch=master" alt="Tests">
</a>

<a href="https://github.com/mdapena/pyventus/actions?query=workflow%3ADocs+event%3Apush+branch%3Amaster" target="_blank">
    <img src="https://github.com/mdapena/pyventus/actions/workflows/deploy-docs.yml/badge.svg?branch=master" alt="Docs">
</a>

<a href='https://coveralls.io/github/mdapena/pyventus?branch=master'>
	<img src='https://coveralls.io/repos/github/mdapena/pyventus/badge.svg?branch=master' alt='Coverage Status'/>
</a>

<a href="https://pypi.org/project/pyventus" target="_blank">
    <img src="https://img.shields.io/pypi/v/pyventus?color=blue" alt="Package version">
</a>

<a href="https://pypi.org/project/pyventus" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/pyventus?color=blue" alt="Supported Python versions">
</a>

<a href="https://www.pepy.tech/projects/pyventus" target="_blank">
    <img src="https://static.pepy.tech/badge/pyventus/month" alt="Last 30 days downloads for the project">
</a>

<a href="https://github.com/psf/black">
	<img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style: black">
</a>

</p>


---

**Documentation**: <a href="https://mdapena.github.io/pyventus" target="_blank">https://mdapena.github.io/pyventus</a>

**Source Code**: <a href="https://github.com/mdapena/pyventus" target="_blank">https://github.com/mdapena/pyventus</a>

---

<p style='text-align: justify;' markdown>
    &emsp;&emsp;Pyventus is a modern and robust Python package for event-driven programming. It offers a comprehensive
	suite of tools to easily define, emit, and orchestrate events using customizable event emitters and flexible
	responses. With Pyventus, you can easily build scalable, extensible, and loosely-coupled event-driven applications.
</p>

## More than just Events

<p style='text-align: justify;'>
	Pyventus offers several key features that make it a powerful event-driven programming package for your 
	Python projects:
</p> 


<ul style='text-align: justify;'>

<li><b>An Intuitive API</b> ─ 
Pyventus provides a user-friendly API for defining events, emitters, and handlers. Its design simplifies the process
of working with events, enabling you to organize your code around discrete events and their associated actions.
</li>

<li><b>Sync and Async Support</b> ─ 
Whether your code is synchronous or asynchronous, Pyventus allows you to define event handlers as either sync or async
callbacks and emit events from both scopes. 
</li>

<li><b>Runtime Flexibility</b> ─ 
Pyventus' runtime flexibility allows you to switch seamlessly between different official or custom event emitter
implementations on the fly.
</li>

<li><b>Customization</b> ─ 
Whether you choose official emitters or custom ones, Pyventus allows you to customize the behavior and capabilities of
the event emitters to perfectly align with your unique requirements.
</li>

<li><b>Reliable Event Handling</b> ─ 
Pyventus allows you to define handlers to customize how events are processed upon completion. Attach success and
failure logic to take targeted actions based on the outcome of each event execution. 
</li>

<li><b>Scalability and Maintainability</b> ─ 
By adopting an event-driven approach with Pyventus, you can create scalable and maintainable code thanks to the loose
coupling between its components that enables extensibility and modularity.
</li>

<li><b>Comprehensive Documentation</b> ─ 
Pyventus provides a comprehensive documentation suite that includes API references, usage examples, best practices
guides, and tutorials to effectively leverage all the features and capabilities of the package.
</li>

</ul>

## <code>Hello, World!</code> Example

<p style='text-align: justify;'>
    &emsp;&emsp;Experience the power of Pyventus through a simple <code>Hello, World!</code> example that illustrates 
	the core concepts and basic usage of the package. This example will walk you through the essential steps of 
	creating an event handler and triggering events within your application.
</p>

```Python title="Hello, World! example with Pyventus" linenums="1"
from pyventus import EventLinker, EventEmitter, AsyncIOEventEmitter


@EventLinker.on("MyEvent")
def event_callback():  # (1)!
    print("Hello, World!")


event_emitter: EventEmitter = AsyncIOEventEmitter()  # (2)!
event_emitter.emit("MyEvent")  # (3)!
```

1. The event handler callback can be either `sync` or `async` depending on your needs.
2. By using the base `EventEmitter` as a dependency the concrete implementation can be seamlessly switched at runtime.
3. The `emit()` method of the event emitter is designed to be called from both synchronous and asynchronous contexts.

<details markdown="1" class="info">
<summary>You can also work with <code>async</code> functions and contexts...</summary>

```Python title="Hello, World! example with Pyventus (Async version)" linenums="1" hl_lines="5 14"
from pyventus import EventLinker, EventEmitter, AsyncIOEventEmitter


@EventLinker.on("MyEvent")
async def event_callback():
    print("Hello, World!")


event_emitter: EventEmitter = AsyncIOEventEmitter()
event_emitter.emit("MyEvent")
```

</details>

<p style='text-align: justify;'>
    &emsp;&emsp;As we can see from the <code>Hello, World!</code> example, Pyventus follows a simple and intuitive 
	workflow for event-driven programming. Let's recap the essential steps involved:
</p>

<ol style='text-align: justify;'>

<li>
<b>Defining the event handler callback:</b> We defined the function <code>event_callback()</code> and used the 
<code>@EventLinker.on()</code> decorator to associate it with the string event <code>MyEvent</code>. This decorator
indicates that the function should be triggered when <code>MyEvent</code> occurs.
</li>

<li>
<b>Creating the event emitter instance:</b> We instantiated the <code>AsyncIOEventEmitter</code> class, which acts as 
the event emitter responsible for dispatching events and invoking the associated event handler callbacks.
</li>

<li>
<b>Emitting the event:</b> By utilizing the <code>emit()</code> method of the event emitter, we emitted the string 
event <code>MyEvent</code>. This action subsequently execute the registered event handler callbacks, which in this case
is the <code>event_callback()</code>.
</li>

</ol>

<p style='text-align: justify;'>
    &emsp;&emsp;Having gained a clear understanding of the workflow showcased in the <code>Hello, World!</code> example,
	you are now well-equipped to explore more intricate event-driven scenarios and fully harness the capabilities of 
	Pyventus in your own projects.
</p>

!!! example "Next steps"

	<p style='text-align: justify;' markdown>
	    Feel free to experiment and build upon this example to explore the full potential of Pyventus in your own 
		projects. You can register **additional event handlers**, handle **events with different event types**
		or **metadata**, implement **custom event emitters** and **event linkers** based on your application's 
		requirements. 
	</p>

## A Practical Example

<p style='text-align: justify;' markdown>
    &emsp;&emsp;To demonstrate Pyventus in a realistic scenario, we will examine how to implement a portion of the 
    password reset workflow using an event-driven approach.
</p>

<p style='text-align: justify;' markdown>
    &emsp;&emsp;A common part of the password reset process involves notifying the user that a reset was requested. 
    In traditional implementations, the code to validate the reset request may be tightly coupled with the logic to
    communicate this to the user. With Pyventus, we can model these steps as distinct events that are emitted after 
    validation and handled asynchronously. This decouples the notification process from validation and allows 
    flexible integration.
</p>

<p style='text-align: justify;' markdown>
    &emsp;&emsp; In this example, we will focus on integrating the notification subsystem through events. Upon 
    validating a reset request, we will emit a `PasswordResetRequested` event containing user details. This 
    event will then trigger the sending of a confirmation email through an asynchronous handler.
</p>

```Python title="Practical Example with Pyventus" linenums="1"
from dataclasses import dataclass
from smtplib import SMTPConnectError

from pyventus import Event, EventLinker, EventEmitter, AsyncIOEventEmitter


@dataclass(frozen=True)
class PasswordResetRequestedEvent(Event):
    """Event triggered when a password reset is requested."""

    user_id: str
    token: str
    ip_address: str
    email: str


@EventLinker.on("PasswordResetRequestedEvent")
async def notify_recovery_email_of_password_reset(event: PasswordResetRequestedEvent):
    """Event handler for notifying the recovery email of a password reset."""
    print("Recovery email notified!")


with EventLinker.on(PasswordResetRequestedEvent) as linker:
    @linker.on_event
    async def send_password_reset_email(event: PasswordResetRequestedEvent):
        """Event handler for sending a password reset email."""
        print(event)
        raise SMTPConnectError(421, "service not available")


    @linker.on_failure
    def password_reset_email_exception(exc: Exception):
        """Event handler for handling exceptions related to sending password reset emails."""
        if isinstance(exc, SMTPConnectError):
            print(f"SMTPConnectError received!")


@EventLinker.on(Event)
def logging(*args, **kwargs):
    """Event handler for general logging of events and exceptions."""
    print(f"\nLogging: args: {args}, kwargs: {kwargs}\n")


# Create an instance of the event emitter
event_emitter: EventEmitter = AsyncIOEventEmitter()

# Emit a PasswordResetRequestedEvent
event_emitter.emit(
    PasswordResetRequestedEvent(
        user_id="33171591-5a4e-42ae-b719-8e7b525337e5",
        token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyZXNldF91dWlkIjoiM",
        ip_address="192.168.0.1",
        email="user@example.com",
    )
)
```

## Support for Synchronous and Asynchronous code

<p style='text-align: justify;'>
    &emsp;&emsp;Pyventus is designed from the ground up to seamlessly support both synchronous and asynchronous
	programming models. Its unified sync/async API allows you to define event handler callbacks and emit events
	across <code>sync</code> and <code>async</code> contexts. Let's take a look at some use cases that illustrate 
	how the API handles event registration and dispatch transparently.
</p>

### Registering Event Handlers as <code>Sync</code> and <code>Async</code> Callbacks

```Python 
@EventLinker.on("MyEvent")
def sync_event_callback():
    # Synchronous event handling
    print("Event received!")


@EventLinker.on("MyEvent")
async def async_event_callback():
    # Asynchronous event handling
    print("Event received!")  
```

### Emitting Events from <code>Sync</code> and <code>Async</code> Contexts

```Python 
# Emitting an event within a sync function
def sync_function(event_emitter: EventEmitter):
    event_emitter.emit("MyEvent")


# Emitting an event within an async function
async def async_function(event_emitter: EventEmitter):
    event_emitter.emit("MyEvent")
```

<details markdown="1" class="info" open>
<summary>Event Propagation Within Different Contexts</summary>

<p style='text-align: justify;'>
    &emsp;&emsp;While Pyventus provides a base <code>EventEmitter</code> class with a unified sync/async API, the 
	specific propagation behavior when emitting events may vary depending on the concrete <code>EventEmitter</code>
	used. For example, the <code>AsyncIOEventEmitter</code> implementation leverages the <code>AsyncIO</code> event
	loop to schedule callbacks added from asynchronous contexts without blocking. But alternative emitters could 
	structure propagation differently to suit their needs.
</p>

</details>

## Runtime Flexibility and Customization

<p style='text-align: justify;'>
    &emsp;&emsp;At its core, Pyventus utilizes a modular event emitter design that allows you to switch seamlessly
	between different built-in or custom event emitter implementations on the fly. Whether you opt for official
	emitters or decide to create your custom ones, Pyventus allows you to tailor the behavior and capabilities
	of the event emitters to perfectly align with your unique requirements.
</p>

<p style='text-align: justify;'>
    &emsp;&emsp;By leveraging the principles of dependency inversion and open-close, Pyventus decouples the event
	emission process from the underlying implementation that handles the event emission and enables you, in conjunction
	with the <code>EventLinker</code>, to change the event emitter at runtime without the need to reconfigure all 
	connections or employ complex logic.
</p>

### Seeing it in Action

<p style='text-align: justify;'>
    &emsp;&emsp;Now let's put Pyventus' flexibility to the test with a practical example. First, we'll build a
	custom <a href="https://fastapi.tiangolo.com/" target="_blank">FastAPI</a> EventEmitter to properly handle
	the event emission using the framework's <a href="https://fastapi.tiangolo.com/reference/background/" target="_blank">BackgroundTasks</a>
	workflow. Then, we'll illustrate Pyventus' dynamic capabilities by swapping this custom emitter out for a built-in
	alternative on the fly.
</p>

<p style='text-align: justify;'>
    &emsp;&emsp;To follow along, please ensure that you have the FastAPI framework <a href="https://fastapi.tiangolo.com/?h=#installation" target="_blank">installed</a>. 
	Once that is complete, let's dive into the step-by-step implementation:
</p>

<ol style='text-align: justify;'>

<li>
Create a <code>main.py</code> file with:

```Python title="main.py" linenums="1"  hl_lines="9 16-17 37 40"
from asyncio import sleep
from random import randint

from fastapi import BackgroundTasks, FastAPI

from pyventus import EventEmitter, EventLinker, AsyncIOEventEmitter


class FastAPIEventEmitter(EventEmitter):
    """Custom event emitter class that leverages the FastAPI's asynchronous workflow."""

    def __init__(self, background_tasks: BackgroundTasks):
        super().__init__()
        self._background_tasks = background_tasks  # Store the FastAPI background tasks object          

    def _process(self, event_emission: EventEmitter.EventEmission) -> None:
        self._background_tasks.add_task(event_emission)  # Execute the event emission as background tasks


@EventLinker.on("console_print")
async def console_print(message: str):
    await sleep(randint(0, 3))  # Simulate a random delay
    print(message)


app = FastAPI()


@app.get("/print")
async def console_print_endpoint(background_tasks: BackgroundTasks):
    """FastAPI endpoint that triggers the console_print event."""

    def console_print_app_service(event_emitter: EventEmitter) -> None:
        event_emitter.emit("console_print", message=f"\nHello, {event_emitter.__class__.__name__}!")

    # Emit the console_print event using FastAPIEventEmitter
    console_print_app_service(event_emitter=FastAPIEventEmitter(background_tasks))

    # Emit the console_print event using AsyncIOEventEmitter
    console_print_app_service(event_emitter=AsyncIOEventEmitter())

    return {"message": "Console print triggered!"}
```

</li> 



<li>
<a href="https://fastapi.tiangolo.com/#run-it" target="_blank">Run the server</a> with:

```console
uvicorn main:app --reload
```

</li>

<li>
Open your browser at <a href="http://127.0.0.1:8000/print" target="_blank">http://127.0.0.1:8000/print</a>. You will 
see the JSON response as:

```JSON
{ "message": "Console print triggered!" }
```

You'll also be able to see the outputs of the event emitters in the console logs as follows:

```console
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [28720]
INFO:     Started server process [28722]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     127.0.0.1:52391 - "GET /print HTTP/1.1" 200 OK

Hello, FastAPIEventEmitter!

Hello, AsyncIOEventEmitter!
```

</li>

</ol> 

<p style='text-align: justify;'>
    &emsp;&emsp;As we can see from this practical example, we were able to easily adapt the event emitter to the
	context of the FastAPI framework. We defined and implemented a custom emitter tailored for FastAPI's workflow,
	using background tasks to handle the event emission accordingly.
</p>

<p style='text-align: justify;'>
    &emsp;&emsp;We also saw Pyventus' dynamic flexibility firsthand - swapping emitters in real-time required no
	intricate reconfiguration or re-establishing of handlers. Simply changing the concrete emitter allowed for
	a seamless transition between implementations.
</p>

<details markdown="1" class="tip" open>
<summary>Official <code>FastAPIEventEmitter</code> integration</summary>
<p style='text-align: justify;'>
No need for manual implementation! Pyventus now offers an official <b><a href="/pyventus/tutorials/emitters/fastapi">FastAPIEventEmitter</a></b>
integration.
</p>
</details>

## Defining Event Response Logic

<p style='text-align: justify;'>
    &emsp;&emsp;As we mentioned earlier, Pyventus allows you to customize how events are processed upon completion in
	success or error scenarios by attaching custom handlers. To utilize this functionality, Pyventus provides a simple
	yet powerful Pythonic syntax through its <code>event linkage context</code>.
</p>

<p style='text-align: justify;'>
    &emsp;&emsp;The <code>event linkage context</code> enables defining the event workflow and completion handlers in an
	organized manner. This is done by using the <code>EventLinker.on</code> method within a <code>with</code> statement
	block. Let's examine examples demonstrating how success and failure handlers can be attached using the event linkage
	context:
</p>

### Success and Error Handling Example

=== "Success execution"

	```Python linenums="1"  hl_lines="9 11-13"
	from pyventus import EventLinker, EventEmitter, AsyncIOEventEmitter
	

	with EventLinker.on("StringEvent") as linker: # (1)!

	    @linker.on_event
	    def event_callback() -> str:
	        print("Event received!")
	        return "Event succeeded!"
	
	    @linker.on_success
	    def success_callback(msg: str) -> None:
	        print(msg)
	
	    @linker.on_failure
	    def failure_callback(exc: Exception) -> None:
	        print(exc)
	

	event_emitter: EventEmitter = AsyncIOEventEmitter()
	event_emitter.emit("StringEvent")
	```

	1. When the `Eventlinker.on` method is used as a context manager via the `with` statement, it allows multiple
       callbacks to be associated with events within the `linkage context block`, defining the event workflow.

	<p style='text-align: justify;' markdown>
		When we emit this event, the success handler we attached is invoked, printing `Event succeeded!` to the console.
	</p>

	```console
	Event received!
	Event succeeded!
	```

=== "Error execution"

	```Python linenums="1"  hl_lines="8 15-17"
	from pyventus import EventLinker, EventEmitter, AsyncIOEventEmitter
	

	with EventLinker.on("StringEvent") as linker: # (1)!

	    @linker.on_event
	    def event_callback() -> str:
	        raise ValueError("Something went wrong!")
	        return "Event succeeded!"
	
	    @linker.on_success
	    def success_callback(msg: str) -> None:
	        print(msg)
	
	    @linker.on_failure
	    def failure_callback(exc: Exception) -> None:
	        print(exc)
	

	event_emitter: EventEmitter = AsyncIOEventEmitter()
	event_emitter.emit("StringEvent")
	```

	1. When the `Eventlinker.on` method is used as a context manager via the `with` statement, it allows multiple
       callbacks to be associated with events within the `linkage context block`, defining the event workflow.

	<p style='text-align: justify;' markdown>
		When we emit this event, the failure handler we attached is invoked, printing `Something went wrong!` to the
		console.
	</p>

	```console
	[Logger] 2023-12-12 11:50:00 AM    ERROR [EventHandler] Exception: Something went wrong!
	Something went wrong!
	```

<p style='text-align: justify;'>
    &emsp;&emsp;As we have seen from the examples, Pyventus' event linkage context provides a reliable and Pythonic way
	to manage the event workflow and response to different completion outcomes through the use of custom handlers.
</p>

## Continuous Evolution

<p style='text-align: justify;'>
	&emsp;&emsp;Pyventus continuously adapts to support developers across technological and programming domains. Its
	aim is to remain at the forefront of event-driven design. Future development may introduce new official event 
	emitters, expanding compatibility with different technologies through seamless integration.
</p>

<p style='text-align: justify;'>
	&emsp;&emsp;Current default emitters provide reliable out-of-the-box capabilities for common use cases. They
	efficiently handle core event operations and lay the foundation for building event-driven applications.
</p>

<details markdown="1" class="info" open>
<summary>Driving Innovation Through Collaboration</summary>

<p style='text-align: justify;'>
    &emsp;&emsp;Pyventus is an open source project that welcomes community involvement. If you wish to contribute
	additional event emitters, improvements, or bug fixes, please check the <a href="/pyventus/contributing/">Contributing</a> 
	section for guidelines on collaborating. Together, we can further the possibilities of event-driven development.
</p>

</details>

## Get Started Today!

<p style='text-align: justify;' markdown>
    &emsp;&emsp;Are you ready to dive into event-driven programming with Pyventus? Follow these steps to integrate Pyventus into
	your project and start building event-driven applications. Click the button below to navigate to the Pyventus 
	Getting Started page and explore detailed instructions, examples, and more:
</p>

---

<p style='text-align: center;' markdown>
	[:material-star-outline:&emsp;Getting Started&emsp;:material-star-outline:](/pyventus/getting-started/){ .md-button }
</p>

---

## License

<p style='text-align: justify;' markdown>
    &emsp;&emsp;Pyventus is distributed as open source software and is released under the <a href="https://choosealicense.com/licenses/mit/" target="_blank">MIT License</a>. 
    You can view the full text of the license in the <a href="https://github.com/mdapena/pyventus/blob/master/LICENSE" target="_blank"><code>LICENSE</code></a> 
	file located in the Pyventus repository.
</p>

