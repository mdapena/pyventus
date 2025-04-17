# Event Types

<p style="text-align: justify;">
    &emsp;&emsp;In event-driven programming, events are defined as occurrences or changes in state that trigger responses within an application. They are essential for enabling communication between different components, acting as messages that convey important information and enable dynamic responses.
</p>

## String Events

<p style="text-align: justify;">
    &emsp;&emsp;String events are defined by a string name and are among the simplest types of events to use. They offer a straightforward approach for handling events, making them ideal for basic use cases. However, because they are hardcoded and lack a structured format, they may not be suitable for more complex scenarios.
</p>

```Python linenums="1" hl_lines="4 10"
from pyventus.events import AsyncIOEventEmitter, EventEmitter, EventLinker


@EventLinker.on("GreetEvent")
def handle_greet_event():
    print("Hello, World!")


event_emitter: EventEmitter = AsyncIOEventEmitter()
event_emitter.emit("GreetEvent")
```

??? tip "Sending Data with String Events"

    <p style="text-align: justify;" markdown>
        &emsp;&emsp;To pass data to subscribers in string-based events, simply define parameters in the callback function you are subscribing to, and when emitting the string event with an event emitter, provide the necessary values using the `*args` and `**kwargs` arguments.
    </p>

    ```Python linenums="1" hl_lines="5 10-11"
    from pyventus.events import AsyncIOEventEmitter, EventEmitter, EventLinker


    @EventLinker.on("GreetEvent")
    def handle_greet_event(name: str, formal: bool = False):
        print(f"{'Hello' if formal else 'Hey'}, {name}!")


    event_emitter: EventEmitter = AsyncIOEventEmitter()
    event_emitter.emit("GreetEvent", "Pyventus", formal=True)
    event_emitter.emit("GreetEvent", name="Pyventus")
    ```

## Event Objects

<p style="text-align: justify;">
    &emsp;&emsp;Event Objects are essentially events that are defined through data classes. This event type not only offers a structured way to define events and encapsulate relevant data payloads, but also provides support for additional validations and behaviors.
</p>

```Python linenums="1" hl_lines="1 6-7 12-13 21-24"
from dataclasses import dataclass

from pyventus.events import AsyncIOEventEmitter, EventEmitter, EventLinker


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
    event=OrderCreatedEvent(  # (1)!
        order_id=6452879,
        payload={},
    ),
)
```

1.  You can also emit the event object as a positional argument:
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

??? tip "Adding Validation to Event Objects"

    <p style="text-align: justify;" markdown>
        &emsp;&emsp;To ensure that the payload of an event meets a specific criteria before its propagation, you can use the dataclasss' method `__post_init__()` to implement the necessary validation logic.
    </p>

    ```Python linenums="1" hl_lines="6-10"
    @dataclass
    class OrderCreatedEvent:
        order_id: int
        payload: dict

        def __post_init__(self):
            if not isinstance(self.order_id, int):
                raise ValueError("Error: 'order_id' must be a valid int number!")
            if not self.payload:
                raise ValueError("Error: 'payload' cannot be empty!")
    ```

## Exception Events

<p style="text-align: justify;">
    &emsp;&emsp;In addition to event objects, Pyventus allows exceptions to be treated as first-class events. This enables the propagation and handling of errors in an event-driven manner.
</p>

```Python linenums="1" hl_lines="4-5 10 12-13"
from pyventus.events import AsyncIOEventEmitter, EventEmitter, EventLinker


@EventLinker.on(ValueError)
def handle_validation_error(exc: ValueError):
    print(f"Validation failed for: '{exc}'")


try:
    raise ValueError("`username`, already in use.")
except ValueError as e:
    event_emitter: EventEmitter = AsyncIOEventEmitter()
    event_emitter.emit(e)
```

??? tip "You can also work with custom exceptions..."

    ```Python linenums="1" hl_lines="1 7-8 13 15-16"
    class UserValidationError(ValueError):
        def __init__(self, error: str = "Validation Error"):
            super().__init__(error)
            self.error: str = error


    @EventLinker.on(UserValidationError)
    def handle_validation_error(exc: UserValidationError):
        print(f"Validation failed for: '{exc.error}'")


    try:
        raise UserValidationError("`username`, already in use.")
    except UserValidationError as e:
        event_emitter: EventEmitter = AsyncIOEventEmitter()
        event_emitter.emit(e)
    ```

## Global Events

<p style="text-align: justify;" markdown>
	&emsp;&emsp;Pyventus also provides support for global events, which are particularly useful for implementing cross-cutting concerns such as logging, monitoring, and analytics. By subscribing event callbacks to `...`, you can capture all events that may occur within that specific `EventLinker` context.
</p>

```Python linenums="1" hl_lines="4-5 10"
from pyventus.events import AsyncIOEventEmitter, EventEmitter, EventLinker


@EventLinker.on(...)
def logging(*args, **kwargs):  # (1)!
    print(f"Logging:\n- Args: {args}\n- Kwargs: {kwargs}")


event_emitter: EventEmitter = AsyncIOEventEmitter()
event_emitter.emit("AnyEvent", name="Pyventus")
```

1. This event callback will be triggered by any event type that occurs within the specific context of that `EventLinker`.

## Custom Event Types

<p style="text-align: justify;" markdown>
	&emsp;&emsp;If you wish to support additional event type definitions, such as defining event objects using Pydantic's `BaseModel`, you only need to create a custom `EventLinker` and modify the `get_valid_event_name()` class method. Once you've done that, ensure that you utilize this custom `EventLinker` throughout your application.
</p>

```Python linenums="1" hl_lines="1 5 8-11 14-16 19 25 28-31"
from pydantic import BaseModel, PositiveInt, PositiveFloat
from pyventus.events import AsyncIOEventEmitter, EventEmitter, EventLinker


class CustomEventLinker(EventLinker):

    @classmethod
    def get_valid_event_name(cls, event):
        if isinstance(event, type) and issubclass(event, BaseModel):
            return event.__name__
        return super().get_valid_event_name(event)


class OrderCreatedEvent(BaseModel):
    order_id: PositiveInt
    payload: dict[str, PositiveFloat]


@CustomEventLinker.on(OrderCreatedEvent)
def handle_greet_event(event: OrderCreatedEvent):
    print(f"Event Object: {event}")


event_emitter: EventEmitter = AsyncIOEventEmitter(
    event_linker=CustomEventLinker,
)
event_emitter.emit(
    event=OrderCreatedEvent(
        order_id=6452879,
        payload={"t-shirt": 29.99},
    ),
)
```
