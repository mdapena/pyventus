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

---

**Documentation**: <a href="#" target="_blank">https://github.com/mdapena/pyventus</a>

**Source Code**: <a href="#" target="_blank">https://github.com/mdapena/pyventus</a>

---

<p style='text-align: justify;' markdown>
    &emsp;&emsp;Welcome to the official documentation of Pyventus, a modern and robust Python package designed for event-driven
	programming. Pyventus offers a comprehensive suite of tools and utilities that streamline event emission, event
	listener management, and event emitters. Users can easily implement event-driven architectures and construct
	modular, decoupled systems with Pyventus. 
</p>

## More than just Events

<p style='text-align: justify;'>
    Pyventus offers several key features that make it a powerful event-driven programming package for your 
	Python projects:
</p> 

<ul style='text-align: justify;' markdown>

<li markdown>**Event-Driven Architecture** ─ 
Pyventus simplifies the implementation of event-driven architecture in your applications. It *`provides an intuitive 
API for defining events, event emitters and event listeners`*, enabling you to organize your code around discrete 
events and their associated actions.
</li>

<li markdown>**Sync and Async Support** ─ 
Whether your code is synchronous or asynchronous, Pyventus seamlessly *`handles both sync and 
async functions and contexts`*. You can define event listeners as either synchronous or asynchronous 
functions, and Pyventus automatically adapts to the execution context during event emissions.
</li>

<li markdown>**Decoupled Components** ─ 
Pyventus promotes a clear separation of concerns by decoupling the *`event dispatcher, event listeners, and event 
linkers`*. This separation enhances code readability, reusability, and testability, allowing you to modify specific 
functionalities without impacting the entire system.
</li>

<li markdown>**Dynamic Event Emitter** ─ 
Pyventus provides a dynamic *`event emitter that can be changed at runtime`*. This flexibility allows you to implement
custom event emitters or choose from a variety of pre-existing emitter implementations to suit your specific 
requirements.
</li>

<li markdown>**Robust Error Handling** ─ 
Pyventus ensures robust *`error handling during event emissions`*. If an error occurs during the event emission process, 
Pyventus captures the error and emits an exception event. These exception events can be handled by appropriate 
exception event listeners, helping you identify and manage errors effectively.
</li>

<li markdown>**Scalability and Maintainability** ─ 
By adopting an event-driven approach with Pyventus, you can create scalable and maintainable code. The *`loose
coupling between components`* enables easier extensibility and modularity, allowing for the addition or modification
of functionalities without disrupting the entire system.
</li>

<li markdown>**Comprehensive Documentation** ─ 
Pyventus provides *`extensive documentation`*, including API explanations, usage examples, best practices, and 
implementation guidelines, to help you effectively utilize the package's features and functionalities.
</li>

</ul>

## `Hello, World!` Example

<p style='text-align: justify;' markdown>
    &emsp;&emsp;Experience the power of Pyventus through a simple `Hello, World!` example that illustrates the core concepts and
	basic usage of the package. This example will walk you through the essential steps of creating an event listener 
	and triggering events within your application.
</p>

```Python title="Hello, World! example with Pyventus" linenums="1"
from pyventus import EventLinker, AsyncioEventEmitter


@EventLinker.on("MyEvent")
def handle_my_event():  # (1)!
    """ Event listener for handling MyEvent. """
    print("Hello, World!")


# Create an instance of the event emitter
event_emitter = AsyncioEventEmitter()  # (2)!

# Emit a MyEvent
event_emitter.emit("MyEvent")  # (3)!
```

1. :material-format-list-group-plus: **Note** ─ With Pyventus, you can confidently handle both `sync` and `async`
   functions.
2. :material-format-list-group-plus: **Note** ─ The event emitter can be dynamically changed based on the requirements.
   <a href="/">Learn more…</a>
3. :material-format-list-group-plus: **Note** ─ The emit method of the Pyventus event emitter works seamlessly in both
   `sync` and `async` contexts.

??? info "You can also work with <code>async</code> functions or within an asynchronous context..."

    <p style='text-align: justify;' markdown>
        If your code utilizes asynchronous programming patterns like `async` and `await`, Pyventus supports defining
		event handlers asynchronously using `async def`. It also handles event emission natively in async contexts.
    </p>
    
    ```Python title="Async Hello, World! example with Pyventus" hl_lines="5" linenums="1"
    from pyventus import EventLinker, AsyncioEventEmitter
    
    
    @EventLinker.on('MyEvent')
    async def handle_my_event():
        """ Async event listener for handling MyEvent. """
        print(f"Hello, World!")
    
    
    # Create an instance of the event emitter
    event_emitter = AsyncioEventEmitter()
    
    # Emit a MyEvent
    event_emitter.emit('MyEvent')  
    ```

<p style='text-align: justify;' markdown>
    &emsp;&emsp;As we can see from the `Hello, World!` example, Pyventus follows a simple and intuitive 
    workflow for event-driven programming. Let's recap the essential steps involved:
</p>

<ol style='text-align: justify;' markdown>

<li markdown>
**Defining the event listener function:** We defined the function `handle_my_event()` and used the `@EventLinker.on()`
decorator to associate it with the event `MyEvent`. This decorator indicates that the function should be triggered 
when `MyEvent` occurs.
</li>

<li markdown>
**Creating the event emitter instance:** We instantiated the `AsyncioEventEmitter` class, which acts as the event 
emitter responsible for dispatching events and invoking the associated event listener.
</li>

<li markdown>
**Emitting the event:** By utilizing the `emit()` method of the event emitter, we emitted the event `MyEvent`. This
action subsequently executed the registered event listener, `handle_my_event()`.
</li>

</ol>

<p style='text-align: justify;' markdown>
    &emsp;&emsp;Having gained a clear understanding of the workflow showcased in the `Hello, World!` example, you are
	now well-equipped to explore more intricate event-driven scenarios and fully harness the capabilities of Pyventus 
	in your own projects.
</p>

!!! example "Next steps"

	<p style='text-align: justify;' markdown>
	    Feel free to experiment and build upon this example to explore the full potential of Pyventus in your own 
		projects. You can register **additional event listeners**, handle **events with different event types**
		or **metadata**, implement **custom event emitters** and **event linkers** based on your application's 
		requirements. 
	</p>

## Support for Synchronous and Asynchronous Code

<p style='text-align: justify;' markdown>
    &emsp;&emsp;Pyventus is designed from the ground up to seamlessly support both asynchronous and synchronous programming
	models with a unified sync/async API. Its core abstractions handle event emission and propagation transparently
	across execution contexts.
</p>

<p style='text-align: justify;' markdown>
    &emsp;&emsp;The event system architecture in Pyventus is designed to be context-agnostic, allowing event emitters and
	listeners to be used interchangeably in both asynchronous and synchronous scopes. However, the behavior of
	event propagation within asynchronous and synchronous contexts is determined by the specific implementation
	of the event emitter.
</p>

<p style='text-align: justify;' markdown>
    &emsp;&emsp;By default, Pyventus' certified emitters ensure asynchronous event emission in asynchronous contexts and
	synchronous event propagation in synchronous code. This approach preserves the intrinsic nature of asynchronous
	code while maintaining synchronous propagation for synchronous functions.
</p>

<p style='text-align: justify;' markdown>
    &emsp;&emsp;Developers also have the flexibility to implement custom emitters to define alternative propagation behaviors
	as needed. However, in most cases, Pyventus' event system handles the asynchronous/synchronous distinction
	seamlessly out of the box.
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
    event_emitter: EventEmitter = AsyncioEventEmitter()
    event_emitter.emit(MyEvent())


def sync_function():
    # Emitting an event within a sync function
    event_emitter: EventEmitter = AsyncioEventEmitter()
    event_emitter.emit(MyEvent())
```

## Error Handling

<p style='text-align: justify;' markdown>
    &emsp;&emsp;Pyventus event emitters, including the `AsyncioEventEmitter`, are designed with robust error handling
	capabilities to effectively manage errors that may occur during event emission.
</p>

<p style='text-align: justify;' markdown>
    &emsp;&emsp;For instance, the `AsyncioEventEmitter` captures any errors that may arise during event emission and emits an
	exception event for the error listeners. This allows developers to define exception listeners to intercept
	and handle specific types of errors that occur during event emission. Here is an example of exception 
	handling for the `AsyncioEventEmitter`:
</p>

```Python 
@EventLinker.on(ValueError)
def handle_emitter_exception(exception: ValueError):
    # Handle exception events here
    pass
```

<p style='text-align: justify;' markdown>
    &emsp;&emsp;As we can see from the example, the `handle_emitter_exception` function is an exception event listener that
	specifically handles `ValueError` exceptions.
</p>

## Practical Example

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

## Continuous Evolution

<p style='text-align: justify;' markdown>
	&emsp;&emsp;Pyventus continuously adapts to support developers across technological and programming domains. Its
	aim is to remain at the forefront of event-driven design. Future development may introduce new official event 
	emitters, expanding compatibility with different technologies through seamless integration.

<p style='text-align: justify;' markdown>
	&emsp;&emsp;Current default emitters provide reliable out-of-the-box capabilities for common use cases. They
	efficiently handle core event operations and lay the foundation for building event-driven applications.
</p>

!!! info "Driving Innovation Through Collaboration"

	<p style='text-align: justify;' markdown>
	    Pyventus is an open source project that welcomes community involvement. If you wish to contribute
		additional event emitters, improvements, or bug fixes, please check the [**Help**](/help) section for 
		guidelines on collaborating. Together, we can further the possibilities of event-driven development.
	</p>

## Get Started Today!

<p style='text-align: justify;' markdown>
    &emsp;&emsp;Are you ready to dive into event-driven programming with Pyventus? Follow these steps to integrate Pyventus into
	your project and start building event-driven applications. Click the button below to navigate to the Pyventus 
	`Getting Started` page and explore detailed instructions, examples, and more:
</p>


---

<p style='text-align: center;' markdown>
	[:material-star-outline:&emsp;Getting Started&emsp;:material-star-outline:](/getting-started){ .md-button }
</p>

---

## License

<p style='text-align: justify;' markdown>
    &emsp;&emsp;Pyventus is distributed as open source software and is released under the <a href="https://choosealicense.com/licenses/mit/" target="_blank">MIT License</a>. 
    You can view the full text of the license in the `LICENSE` file located in the <a href="https://github.com/mdapena/pyventus" target="_blank">Pyventus repository</a>.
</p>

