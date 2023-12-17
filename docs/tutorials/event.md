<p style='text-align: justify;' markdown>
    &emsp;&emsp;In this first tutorial, you'll learn about defining and handling events in Pyventus. Whether you're new
	to event-driven programming or just getting started with the package, this guide will explain the key concepts.
</p>

## What are Events?

<p style='text-align: justify;' markdown>
    &emsp;&emsp;Events play an important role in Pyventus by allowing different parts of a program to communicate and
	react to changes. The package provides a powerful event system that supports various event types, enabling
	developers to define and handle events effectively.
</p>

## String Events

<p style='text-align: justify;' markdown>
    &emsp;&emsp;We'll begin with Pyventus' basic string event type. These provide an easy way to define and handle
	events using event names as strings. This makes them straightforward to work with and are suited for simpler
	applications requiring a minimal approach.
</p>

### Passing Data

<p style='text-align: justify;' markdown>
    &emsp;&emsp;When subscribing to a String Event, event callbacks can define parameters like regular functions.
	This allows flexibility in passing different data types like strings, integers, etc. The event emitters forward
	any arguments emitted with the string event to handlers using `*args` and `**kwargs`, ensuring they receive the
	same data payload.
</p>

### Usage

<p style='text-align: justify;' markdown>
    Let's look at some code examples of defining and handling `String Events`:
</p>

```Python linenums="1" hl_lines="4 5 12"
from pyventus import EventLinker, EventEmitter, AsyncIOEventEmitter


@EventLinker.on('StringEvent')
def event_handler(param1: str, param2: str, **kwargs):
    print("Parameters:", param1, param2)
    print("**kwargs:", kwargs)


event_emitter: EventEmitter = AsyncIOEventEmitter()

event_emitter.emit('StringEvent', 'value1', param2='value2', key1='value3', key2='value4')
```

<p style='text-align: justify;' markdown>
    You can also use the `subscribe()` method to define and link string-named events:
</p>

```Python linenums="13" hl_lines="8"
from pyventus import EventLinker


def event_handler():
    pass


EventLinker.subscribe('StringEvent', event_callback=event_handler)
```

## Event Objects

<p style='text-align: justify;' markdown>
    &emsp;&emsp;Let's move on to `Event Objects` in Pyventus. They provide a structured way to define events and
	encapsulate relevant data payloads. Some benefits include better organization, validation support, and
	autocomplete when handling events.
</p>

### Defining Event Objects

<p style='text-align: justify;' markdown>
    To create an `Event Object`:
</p>

<ol style='text-align: justify;' markdown>

<li markdown>Define a new class that inherits from the base `Event` class.</li>

<li markdown>Declare fields for the event's payload within the class.</li>

</ol>

<p style='text-align: justify;' markdown>
    For example:
</p>

```Python linenums="1" hl_lines="3 7"
from dataclasses import dataclass

from pyventus import Event


@dataclass(frozen=True)
class CustomEvent(Event):
    param1: str
    param2: float
```

!!! info "Note"

	<p style='text-align: justify;' markdown>
		&emsp;&emsp;The `Event` class is marked with `frozen=True`, to ensure that its attributes cannot be modified
		once the event object is created. This is crucial because Pyventus supports both synchronous and asynchronous
		event handling concurrently. When payloads are accessible from multiple threads, having mutable payloads could
		lead to data inconsistencies. By freezing event objects, their integrity is preserved as they propagate through
		the system.
	</p>

### Adding Validation

<p style='text-align: justify;' markdown>
	&emsp;&emsp;You can also ensure valid data before propagation by adding validation logic to the `Event` class using
	the dataclass' `__post_init__()` method:
</p>

```Python linenums="1" hl_lines="3 7 11-13 16"
from dataclasses import dataclass

from pyventus import Event


@dataclass(frozen=True)
class CustomEvent(Event):
    param1: str
    param2: float

    def __post_init__(self):
        if not isinstance(self.param2, float):
            raise ValueError("Error: 'param2' must be a valid float number!")


CustomEvent(param1="param1", param2=None)
```

### Usage

<p style='text-align: justify;' markdown>
	Here's an example demonstrating subscription and emission:
</p>

```Python linenums="1" hl_lines="3 7 12 13 20-23"
from dataclasses import dataclass

from pyventus import Event, EventLinker, EventEmitter, AsyncIOEventEmitter


@dataclass(frozen=True)
class CustomEvent(Event):
    param1: str
    param2: float


@EventLinker.on(CustomEvent)
def event_handler(event: CustomEvent):
    print(event)


event_emitter: EventEmitter = AsyncIOEventEmitter()

event_emitter.emit(  # (1)!
    event=CustomEvent(
        param1="value1",
        param2=5.31
    )
)  
```

1. You can also emit the `Event` object as a positional argument:
   ```Python linenums="1" hl_lines="2-5"
   event_emitter.emit( 
	   CustomEvent(
		   param1="value1",
		   param2=5.31
	   )
   )  
   ```
   As well as pass extra `*args` and `**kwargs` too:
   ```Python linenums="1" hl_lines="6 7"
   event_emitter.emit( 
	   CustomEvent(
		   param1="value1",
		   param2=5.31
	   ),
		"param1",
		param2="param2",
   )  
   ```

!!! info "Passing Data"

	<p style='text-align: justify;' markdown>
		&emsp;&emsp;When emitting `Event` objects as events using the `emit()` method, the Event object is automatically
		passed to the `Event Handler` as the first positional argument even if you pass extra `*args` or `**kwargs`.
	</p>

### Benefits

<ul style='text-align: justify;' markdown>

<li markdown>**Natural emission of event payloads:**
Emitting an event object is a simple and intuitive process. Once an event object is created, it can be sent using the
event emitter, providing a natural and straightforward approach to event emission. Since the event object carries the
relevant data, the event emitter ensures that the same data is received by the event handlers.
</li>

<li markdown>**Structured and organized event definitions:**
Event objects provide a structured and encapsulated representation of events, enabling better organization and
management of events throughout the system.
</li>

<li markdown>**Custom data validation:**
Event objects can include custom validation logic to ensure the validity of the encapsulated data before propagation.
</li>

<li markdown>**Auto-completion when handling events:**
Event objects benefit from autocompletion integration provided by code editors and IDEs. 
</li>

</ul>

## Handling Exceptions as Events

<p style='text-align: justify;' markdown>
    &emsp;&emsp;In addition to normal events, Pyventus allows exceptions to be treated as first-class events. This enables
	propagating and handling errors in an event-driven manner.
</p>

### Defining Custom Exceptions

<p style='text-align: justify;' markdown>
    To define a custom exception event:
</p>

<ol style='text-align: justify;' markdown>

<li markdown>Create a new class that inherits from any subclass of the `Exception` class.</li>

<li markdown>Add any fields needed to represent the exception.</li>

</ol>

For example:

```Python linenums="1" hl_lines="1 4"
class UserValidationError(ValueError):
    def __init__(self, error: str = "Validation Error"):
        super().__init__(error)
        self.error: str = error
```

### Usage

<p style='text-align: justify;' markdown>
	Let's look at some code examples that demonstrates the usage of event exceptions:
</p>

```Python linenums="1" hl_lines="4 10-11 17-19"
from pyventus import EventLinker, EventEmitter, AsyncIOEventEmitter


class UserValidationError(ValueError):
    def __init__(self, error: str = "Validation Error"):
        super().__init__(error)
        self.error: str = error


@EventLinker.on(UserValidationError)
def handle_validation_error(exc: UserValidationError):
    print(f"Validation failed for; '{exc.error}'")


try:
    raise UserValidationError("username, already in use.")
except UserValidationError as e:
    event_emitter: EventEmitter = AsyncIOEventEmitter()
    event_emitter.emit(e)
```

??? info "You can also work with build-in exceptions..."

	```Python linenums="1" hl_lines="5 11-13"
	from pyventus import EventLinker, EventEmitter, AsyncIOEventEmitter
	
	
	@EventLinker.on(ValueError)
	def handle_validation_error(exc: ValueError):
	    print(f"Validation failed for; '{exc}'")
	
	
	try:
	    raise ValueError("username, already in use.")
	except ValueError as e:
	    event_emitter: EventEmitter = AsyncIOEventEmitter()
	    event_emitter.emit(e)
	```

### Benefits

<p style='text-align: justify;' markdown>
    &emsp;&emsp;By treating exceptions as first-class events, Pyventus provides a unified approach to error handling.
	This approach leverages the existing event-driven infrastructure, promotes code reuse, and enables flexible and
	powerful error handling strategies.
</p>

## Global Events

<p style='text-align: justify;' markdown>
	&emsp;&emsp;In addition to individual events, Pyventus provides support for Global Events within the context
	of an `EventLinker`. This feature allows you to register handlers that respond to event occurrences across
	a specific namespace, regardless of where they happen in your code. Global Events are particularly useful
	for implementing cross-cutting concerns such as logging, monitoring, or analytics. By subscribing handlers
	to the `Event` or `Exception` class, you can capture all events, exception events, or even both that may
	occur in that namespace.
</p>

```Python linenums="1" hl_lines="4 9 14 21 22"
from pyventus import EventLinker, Event, EventEmitter, AsyncIOEventEmitter


@EventLinker.on(Event)  # (1)!
def global_event_handler(*args, **kwargs):
    print("Global Event received!")


@EventLinker.on(Exception)  # (2)! 
def global_exception_event_handler(*args, **kwargs):
    print("Global Exception event received!")


@EventLinker.on(Event, Exception)  # (3)!
def any_event_handler(*args, **kwargs):
    print("Any event received!")


event_emitter: EventEmitter = AsyncIOEventEmitter()

event_emitter.emit('StringEvent', 'Pyventus')
event_emitter.emit(ValueError('Value Error!'))
```

1. This handler will be triggered by any non-Exception event that occurs.
2. This handler will be triggered by any Exception event that occurs.
3. This handler will be triggered by any event type that occurs, including both regular events and exceptions.

## Recap

<p style='text-align: justify;' markdown>
    &emsp;&emsp;In summary, we've covered the different types of events supported by Pyventus - string named events, event
	objects, and exception events. String events provide a simple way to define and handle basic events using names
	as strings. Event objects offer a more structured approach with encapsulated payloads and validation capabilities.
	And exception events allow treating errors as first-class events.
</p>

<p style='text-align: justify;' markdown>
    &emsp;&emsp;Additionally, Pyventus provides support for Global Events within an `EventLinker` context. Global
	Events allow registering handlers across a namespace to respond to events anywhere in the code. This feature
	is useful for implementing cross-cutting concerns like logging, monitoring, or analytics.
</p>

!!! info "Using Different Emitters and Linkers"

	<p style='text-align: justify;' markdown>
	    &emsp;&emsp;The `EventEmitter` and `EventLinker` used in the code examples can be easily replaced with any
		custom or built-in Pyventus implementation of your choice. For more information on available options, consult
		the official documentation.
	</p>

<br>
