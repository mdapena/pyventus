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
    <a href="#">
        <img src="./images/logo/pyventus-logo-name-slogan.svg" alt="Pyventus" width="900px">
    </a>
</p>

---

**Documentation**: <a href="#" target="_blank">https://github.com/NachoDPP/pyventus</a>

**Source Code**: <a href="#" target="_blank">https://github.com/NachoDPP/pyventus</a>

---

<p style='text-align: justify;'>
    &emsp;&emsp;Welcome to the official documentation of Pyventus, a modern and robust Python package specifically 
    designed for event-driven programming in Python. It offers a comprehensive suite of tools and utilities that 
    streamline event emission, event listener management, and dynamic event emitters. With Pyventus, you can 
    effortlessly implement event-driven architectures and construct modular, and decoupled systems.
</p>

## Why use Pyventus?

<p style='text-align: justify;'>
    Pyventus is a powerful event-driven programming package that brings several benefits to your 
    Python projects:
</p> 

<ul style='text-align: justify;'>

    <li><strong>Simplified Event-Driven Architecture</strong> ─ 
    Pyventus simplifies the implementation of event-driven architecture in your applications. It provides a clean and 
    intuitive API for defining events and event listeners, allowing you to organize your code around discrete events 
    and their associated actions.
    </li>

    <li><strong>Versatile Handling of Sync and Async Code</strong> ─ 
    Whether your codebase is synchronous or asynchronous, Pyventus seamlessly handles both <code>sync</code> and 
    <code>async</code> functions and contexts. You can define event listeners as either synchronous or asynchronous 
    functions, and Pyventus automatically adapts to the execution context during event emissions.
    </li>

    <li><strong>Clear Separation of Concerns</strong> ─ 
    Pyventus promotes a clear separation of concerns by decoupling the event dispatcher, event listeners, and event 
    linkers. This separation enhances code readability, reusability, and testability. Each component has a distinct role,
    making it easier to understand and modify specific functionalities without impacting the entire system.
    </li>

    <li><strong>Dynamic Event Emitter and Extensibility</strong> ─ 
    Pyventus offers a dynamic event emitter that can be changed at runtime, providing unparalleled flexibility and 
    extensibility for your applications. By adhering to the Open-Closed principle and employing well-designed 
    abstractions, Pyventus allows you to implement custom event emitters or choose from a variety of pre-existing 
    emitter implementations to suit your specific requirements.
    </li>

    <li><strong>Robust Error Handling</strong> ─ 
    Pyventus ensures robust error handling during event emissions. If an error occurs during the event emission process, 
    Pyventus captures the error and emits an exception event. These exception events can be handled by appropriate 
    exception event listeners, helping you identify and manage errors effectively.
    </li>

    <li><strong>Scalable and Maintainable Codebase</strong> ─ 
    By adopting an event-driven approach with Pyventus, you can create scalable and maintainable codebases. Events 
    provide loose coupling between components, allowing for easier extensibility and modularity in your applications. 
    This makes it simpler to add new functionalities or modify existing ones without disrupting the entire system.
    </li>

    <li><strong>Extensive Documentation</strong> ─ 
    Pyventus provides extensive documentation to guide developers in effectively utilizing the library's features and 
    functionalities. The documentation covers detailed explanations of the API, usage examples, best practices, and 
    implementation guidelines.
    </li>

</ul>

## Requirements

<p style='text-align: justify;'>
    &emsp;&emsp;Pyventus was designed for intuitive and lightweight usage. It aims to have minimal dependencies 
    and an easy installation process. Pyventus is implemented using pure Python, requiring:
</p>

<ul style='text-align: justify;'>
    <li><strong>Python 3.8</strong> or <strong>higher</strong> </li>
    <li><strong>Asyncio</strong> module (bundled with Python 3.5+)</li>
</ul>


<p style='text-align: justify;'>
    &emsp;&emsp;Additional optional dependencies may be needed depending on the specific event emitter implementation. 
    Refer to each emitter's documentation for details. By default, Pyventus relies on features available in the Python 
    standard library for its core functionality. This keeps the base requirements minimal without external packages.
</p>

## Installation

<p style='text-align: justify;'>
    &emsp;&emsp;Pyventus is published as a Python package and can be installed with <code>pip</code>, ideally by using 
    a virtual environment. Open up a terminal and install Pyventus with:
</p>

``` sh
$ pip install pyventus #(1)!
```

1. :material-format-list-group-plus: **Note** ─ Additionally, Pyventus provides optional event emitters that may have
   extra requirements. Refer to the documentation for details on available emitters.

## Hello World! Example

<p style='text-align: justify;'>
    &emsp;&emsp;Now that Pyventus is installed, let's explore a simple <code>"Hello World"</code> example to 
    demonstrate its core event-driven functionality and basic usage.
</p>

```Python title="Hello World with Pyventus."
from pyventus import EventLinker, AsyncioEventEmitter


@EventLinker.on('MyEvent')
def handle_my_event():  # (1)!
    """ Event listener for handling MyEvent. """
    print(f"Hello world!")


# Create an instance of the event emitter
event_emitter = AsyncioEventEmitter()  # (2)!

# Emit a MyEvent
event_emitter.emit('MyEvent')  # (3)!
```

1. :material-format-list-group-plus: **Note** ─ With Pyventus, you can confidently handle both `sync` and `async`
   functions.
2. :material-format-list-group-plus: **Note** ─ The event emitter can be dynamically changed based on the requirements.
3. :material-format-list-group-plus: **Note** ─ The emit method of the Pyventus event emitter works seamlessly in both
   `sync` and `async` contexts.

??? info "You can also work with <code>async</code> functions or within an asynchronous context..."

    <p style='text-align: justify;'>
        &emsp;&emsp;If your code utilizes asynchronous programming patterns like <code>async</code> and <code>await</code>, 
        Pyventus supports defining event handlers asynchronously using <code>async def</code>. It also handles event 
        emission natively in async contexts.
    </p>
    
    ```Python title="Async Hello World with Pyventus." hl_lines="5"
    from pyventus import EventLinker, AsyncioEventEmitter
    
    
    @EventLinker.on('MyEvent')
    async def handle_my_event():
        """ Async event listener for handling MyEvent. """
        print(f"Hello world!")
    
    
    # Create an instance of the event emitter
    event_emitter = AsyncioEventEmitter()
    
    # Emit a MyEvent
    event_emitter.emit('MyEvent')  
    ```

<p style='text-align: justify;'>
    &emsp;&emsp;As we can see from the <code>Hello World</code> example, Pyventus follows a simple and intuitive 
    workflow for event-driven programming. In this example, we start by defining an event listener using the 
    <code>@EventLinker.on</code> decorator, which allows us to associate the handler function with the desired event. 
    This step establishes the foundation for event-driven programming, as it specifies how our application should 
    respond to the event.
</p>

<p style='text-align: justify;'>
    &emsp;&emsp;To complete the workflow, we create an instance of the event emitter using Pyventus. This event emitter 
    enables us to seamlessly emit events using the emit method provided by Pyventus. By invoking the emit method and 
    specifying the appropriate event, we trigger the execution of the associated event listener function.
</p>

<p style='text-align: justify;'>
    &emsp;&emsp;The <code>Hello World</code> example showcases how Pyventus simplifies event handling and demonstrates 
    its effectiveness in streamlining event-driven programming tasks. With Pyventus, developers can easily define 
    event handlers, associate them with events, and emit events, making event-driven programming more 
    straightforward and efficient.
</p>

## Support for Synchronous and Asynchronous Code

<p style='text-align: justify;'>
    &emsp;&emsp;Pyventus is designed from the ground up to seamlessly support asynchronous and synchronous programming
    models. It provides a unified asynchronous and synchronous API that functions transparently regardless of context.
</p>

<p style='text-align: justify;'>
    &emsp;&emsp;At its core, Pyventus handles event emission and propagation automatically within asynchronous or 
    synchronous contexts. When in an asynchronous context like an async function, event emissions will be handled 
    asynchronously. Similarly, in synchronous code event emissions occur synchronously.
</p>

<p style='text-align: justify;'>
    &emsp;&emsp;Pyventus also excels at robust error handling. If an error occurs during event emission, it will
    capture the error and emit an exception event. Exception events can then be handled by dedicated exception
    listeners, ensuring errors are properly managed.
</p>

### Event Listeners for `sync` and `async` Code

```Python 
@EventLinker.on(MyEvent)
def sync_event_handler(event: MyEvent):
    # Synchronous event handling code
    pass


@EventLinker.on(MyEvent)
async def async_event_handler(event: MyEvent):
    # Asynchronous event handling code
    pass
```

### Event Emissions in `sync` or `async` Contexts

```Python 
async def async_function():
    # Emitting an event within an async function
    event_emitter.emit(MyEvent())


def sync_function():
    # Emitting an event within a sync function
    event_emitter.emit(MyEvent())
```

### Exception Handling

```Python
@EventLinker.on(EventEmitterExceptionEvent)
def handle_emitter_exception(event: EventEmitterExceptionEvent):
    # Handle exception events here
    pass
```

## **Practical Example**

<p style='text-align: justify;'>
    &emsp;&emsp;To demonstrate Pyventus in a realistic scenario, we will examine how to implement a portion of the 
    password reset workflow using an event-driven approach.
</p>

<p style='text-align: justify;'>
    &emsp;&emsp;A common part of the password reset process involves notifying the user that a reset was requested. 
    In traditional implementations, the code to validate the reset request may be tightly coupled with the logic to
    communicate this to the user. With Pyventus, we can model these steps as distinct events that are emitted after 
    validation and handled asynchronously. This decouples the notification process from validation and allows 
    flexible integration.
</p>

<p style='text-align: justify;'>
    &emsp;&emsp; In this example, we will focus on integrating the notification subsystem through events. Upon 
    validating a reset request, we will emit a "PasswordResetRequested" event containing user details. This 
    event will then trigger the sending of a confirmation email through an asynchronous handler.
</p>

```Python title="Practival Example with Pyventus"
from dataclasses import dataclass
from smtplib import SMTPConnectError

from pyventus import Event, EventLinker, AsyncioEventEmitter


@dataclass(frozen=True)
class PasswordResetRequestedEvent(Event):
    """ Event triggered when a password reset is requested. """
    user_id: str
    token: str
    ip_address: str
    email: str


@EventLinker.on(PasswordResetRequestedEvent)
async def send_password_reset_email(event: PasswordResetRequestedEvent):
    """ Event listener for sending a password reset email. """
    # For example purpose, uncomment the following lines to test it!
    # print(event)
    # raise SMTPConnectError(421, "service not available")
    pass


@EventLinker.on('PasswordResetRequestedEvent')
async def notify_recovery_email_of_password_reset(event: PasswordResetRequestedEvent):
    """ Event listener for notifying the recovery email of a password reset. """
    # For example purpose, uncomment the following lines to test it!
    # print(event)
    pass


@EventLinker.on(SMTPConnectError)
def password_reset_email_exception(exception: SMTPConnectError):
    """ Event listener for handling exceptions related to sending password reset emails. """
    # For example purpose, uncomment the following line to test it!
    # Example: print(exception)
    pass


# Create an instance of the event emitter
event_emitter: EventEmitter = AsyncioEventEmitter()

# Emit a PasswordResetRequestedEvent
event_emitter.emit(
    PasswordResetRequestedEvent(
        user_id='33171591-5a4e-42ae-b719-8e7b525337e5',
        token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyZXNldF91dWlkIjoiM',
        ip_address='192.168.0.1',
        email='user@example.com'
    )
)
```

## Optional Dependencies

<p style='text-align: justify;'>
    &emsp;&emsp;Pyventus follows the principles of the <a href="https://www.cs.utexas.edu/users/downing/papers/OCP-1996.pdf" target="_blank">Open-Closed Principle</a>, 
    allowing for seamless extension of its functionality through additional <code>EventEmitter</code> implementations,
    without the need to replace existing ones. By default, Pyventus relies solely on the Python standard library. 
    However, users have the flexibility to leverage additional features by selecting an alternate emitter or even
    creating custom ones.
</p>


<ul style='text-align: justify;'>

    <li><strong>RqEventEmitter</strong> ─ 
    The RqEventEmitter integration connects Pyventus with <a href="https://python-rq.org/" target="_blank">RQ</a> 
    queueing using Redis pub/sub. This integration enables the execution of event listeners as background jobs 
    using RQ's asynchronous workers. This is useful for intensive or long-running tasks like video processing, 
    model optimization, or any workloads better suited to async execution that leverage RQ's powerful features. 
    The <code>RqEventEmitter</code> relies on the RQ package as a dependency, which can be installed separately
    to take advantage of this integration.
    </li>

</ul>

## Licence

<p style='text-align: justify;'>
    &emsp;&emsp;Pyventus is released under the <a href="https://choosealicense.com/licenses/mit/" target="_blank">MIT License</a>. 
    You can find the full text of the license in the <code>LICENSE</code> file of the <a href="https://github.com/NachoDPP/pyventus" target="_blank">Pyventus repository</a>.
</p>

!!! info "Interesting Fact"

    <p style='text-align: justify;'>
        &emsp;&emsp;Pyventus gets its name from the fusion of `Python` and `Eventus`, a Latin word meaning "event".
        This name reflects the library's focus on enabling event-driven programming in Python.
    </p>

