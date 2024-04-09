# Exploring Event Types

!!! warning "🏗️ Work in Progress"
    This page is a work in progress.

<p style='text-align: justify;' markdown>
    &emsp;&emsp;In this first tutorial, you'll learn about defining and handling events in Pyventus. Whether you're new
	to event-driven programming or just getting started with the package, this guide will explain the key concepts.
</p>

## What are Events?

<p style='text-align: justify;' markdown>
    &emsp;&emsp;In event-driven programming, events refer to specific occurrences or incidents that happen within the 
	program or system. These events play an important role in Pyventus by enabling different parts of a program to 
	communicate and react to changes. Pyventus provides a powerful event system that supports various event types, 
	allowing developers to effectively define and handle events.
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

```Python linenums="1" hl_lines="1-2 8"
@EventLinker.on("StringEvent")
def event_handler(param1: str, param2: str, **kwargs):
    print("Parameters:", param1, param2)
    print("**kwargs:", kwargs)


event_emitter: EventEmitter = AsyncIOEventEmitter()
event_emitter.emit("StringEvent", "value1", param2="value2", key1="value3", key2="value4")
```

<p style='text-align: justify;' markdown>
    You can also use the `subscribe()` method to define and link string-named events:
</p>

```Python linenums="1" hl_lines="1 4"
def event_handler():
    pass

EventLinker.subscribe("StringEvent", event_callback=event_handler)
```

## Event Objects

<p style='text-align: justify;' markdown>
    &emsp;&emsp;Let's move on to `Event Objects` in Pyventus. They provide a structured way to define events and
	encapsulate relevant data payloads. Some benefits include better organization, maintainability, and validation 
	support.
</p>

### Defining Event Objects

<p style='text-align: justify;' markdown>
    To create an `Event Object`:
</p>

<ol style='text-align: justify;' markdown>

<li markdown>Define a Python `dataclass`.</li>

<li markdown>Declare fields for the event's payload within the class.</li>

</ol>

<p style='text-align: justify;' markdown>
    For example:
</p>

```Python linenums="1" hl_lines="1 3-4"
@dataclass
class OrderCreatedEvent:
    order_id: int
    payload: dict[str, any]
```

### Adding Validation

<p style='text-align: justify;' markdown>
	&emsp;&emsp;You can also ensure valid data before propagation by adding validation logic to the `Event` class using
	the dataclass' `__post_init__()` method:
</p>

```Python linenums="1" hl_lines="6-8"
@dataclass
class OrderCreatedEvent:
    order_id: int
    payload: dict[str, any]

    def __post_init__(self):
        if not isinstance(self.order_id, int):
            raise ValueError("Error: 'order_id' must be a valid int number!")
```

### Usage

<p style='text-align: justify;' markdown>
	Here's an example demonstrating subscription and emission:
</p>

```Python linenums="1" hl_lines="1-2 7-8 16-19"
@dataclass  # Define a Python dataclass.
class OrderCreatedEvent:
    order_id: int
    payload: dict[str, any]


@EventLinker.on(OrderCreatedEvent)  # Subscribe event handlers to the event.
def handle_order_created_event(event: OrderCreatedEvent):
    # Pyventus will automatically pass the Event Object 
    # as the first positional argument.
    print(f"Event Object: {event}")


event_emitter: EventEmitter = AsyncIOEventEmitter()
event_emitter.emit( # (1)!
    event=OrderCreatedEvent(  # Emit an instance of the event!
        order_id=6452879,
        payload={},
    ),
)
```

1. You can also emit the `Event` object as a positional argument:
   ```Python linenums="1" hl_lines="2-5"
   event_emitter.emit( 
	   OrderCreatedEvent(
		   order_id=6452879,
		   payload={},
	   ),
   )  
   ```
   As well as pass extra `*args` and `**kwargs` too:
   ```Python linenums="1" hl_lines="6 7"
   event_emitter.emit( 
	   OrderCreatedEvent(
		   order_id=6452879,
		   payload={},
	   ),
       "param1",
	   param2="param2",
   )  
   ```

!!! info "Event Object's Behavior"

	<p style='text-align: justify;' markdown>
		By default, Pyventus retrieves the event name from the event class and automatically passes the instance of the
		Event Object as the first positional argument to the event callback, even if you provide additional `*args` or
		`**kwargs`.
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

## Exception Events

<p style='text-align: justify;' markdown>
    &emsp;&emsp;In addition to normal events, Pyventus allows exceptions to be treated as first-class events. This enables
	propagating and handling errors in an event-driven manner. If you're interested in incorporating error handling
	in event emission, you can check out [Success and Error Handling](/pyventus/tutorials/event-linker/#success-and-error-handling).
</p>

### Usage

<p style='text-align: justify;' markdown>
	Let's look at some code examples that demonstrates the usage of event exceptions:
</p>

```Python linenums="1" hl_lines="1-2 7 9-10"
@EventLinker.on(ValueError)
def handle_validation_error(exc: ValueError):
    print(f"Validation failed for; '{exc}'")


try:
    raise ValueError("`username`, already in use.")
except ValueError as e:
    event_emitter: EventEmitter = AsyncIOEventEmitter()
    event_emitter.emit(e)
```

??? info "You can also work with custom exceptions..."

	```Python linenums="1" hl_lines="1 7-8 13 15-16"
	class UserValidationError(ValueError):
	    def __init__(self, error: str = "Validation Error"):
	        super().__init__(error)
	        self.error: str = error
	
	
	@EventLinker.on(UserValidationError)
	def handle_validation_error(exc: UserValidationError):
	    print(f"Validation failed for; '{exc.error}'")
	
	
	try:
	    raise UserValidationError("`username`, already in use.")
	except UserValidationError as e:
	    event_emitter: EventEmitter = AsyncIOEventEmitter()
	    event_emitter.emit(e)
	```

### Benefits

<p style='text-align: justify;' markdown>
    &emsp;&emsp;By treating exceptions as first-class events, Pyventus provides a unified approach to handling errors in
	an event-driven manner. This approach leverages the existing event-driven infrastructure, promotes code reuse, and 
	enables flexible and powerful error handling strategies.
</p>

## Global Events

<p style='text-align: justify;' markdown>
	&emsp;&emsp;In addition to individual events, Pyventus provides support for Global Events within the context
	of an `EventLinker`. This feature allows you to register handlers that respond to event occurrences across
	a specific namespace, regardless of where they happen in your code. Global Events are particularly useful
	for implementing cross-cutting concerns such as logging, monitoring, or analytics. By subscribing event 
	handlers to `...` or `Ellipsis`, you can capture all events that may occur within that `EventLinker` 
	context.
</p>

```Python linenums="1" hl_lines="1-2 7"
@EventLinker.on(...)
def handle_any_event(*args, **kwargs):  #(1)!
    print(f"Perform logging...\nArgs: {args}\tKwargs: {kwargs}")


event_emitter: EventEmitter = AsyncIOEventEmitter()
event_emitter.emit("GreetEvent", name="Pyventus")
```

1. This handler will be triggered by any event type that occurs.

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
	    The `EventEmitter` and `EventLinker` used in the code examples can be easily replaced with any custom or
		[*built-in*](/pyventus/getting-started/#optional-dependencies) Pyventus implementation of your choice. 
		For more information on available options, consult the official documentation.
	</p>

<br>
