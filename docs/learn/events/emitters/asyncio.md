# AsyncIO Event Emitter

<p style="text-align: justify;">
	&emsp;&emsp;In Pyventus, you can easily integrate Event Emitters with the AsyncIO framework through the AsyncIO Processing Service. Simply create an instance of the AsyncIO Processing Service and pass it as the event processor when setting up the Event Emitter, or you can use the factory method called AsyncIO Event Emitter to handle the setup in a single step.
</p>

=== ":material-console: Manual Configuration"

    ```Python linenums="1" hl_lines="1 2 4"
    from pyventus.events import EventEmitter
    from pyventus.core.processing.asyncio import AsyncIOProcessingService

    event_emitter = EventEmitter(event_processor=AsyncIOProcessingService())
    event_emitter.emit("MyEvent")
    ```

=== ":material-factory: Factory Method"

    ```Python linenums="1" hl_lines="1 4"
    from pyventus.events import AsyncIOEventEmitter, EventEmitter


    event_emitter: EventEmitter = AsyncIOEventEmitter()
    event_emitter.emit("MyEvent")
    ```

<p style="text-align: justify;">
	&emsp;&emsp;By utilizing the AsyncIO Processing Service, the execution of each event emission will be handled by the AsyncIO event loop.
</p>

## AsyncIO Behavior

<p style="text-align: justify;" markdown>
	&emsp;&emsp;It is important to note that the AsyncIO Processing Service handles the execution of each event emission differently depending on whether an AsyncIO loop is already running (async context) or not (sync context). If there isn’t an active loop, it uses the `asyncio.run()` method to execute the event emission, creating a new loop, waiting for the event emission to finish, and finally closing it. If a loop is already running, the service simply schedules the event emission as a background task using the `asyncio.create_task()`.
</p>

!!! tip "Event Emission is Silently Discarded"

    <p style="text-align: justify;">
        &emsp;&emsp;When working with async contexts, it is important to properly handle the underlying AsyncIO loop, as the AsyncIO Processing Service simply schedules tasks to it. If the AsyncIO loop closes before all submitted callbacks are complete, they will be discarded.
    </p>

## Practical Example

=== "`Sync` contexts"

    ```Python linenums="1" hl_lines="3 12 18 19"
    import asyncio

    from pyventus.core.processing.asyncio import AsyncIOProcessingService
    from pyventus.events import EventEmitter, EventLinker


    async def handle_event_with_delay():
        await asyncio.sleep(1.5)
        print("Done!")


    def main():
        print("Starting...")

        EventLinker.subscribe("MyEvent", event_callback=handle_event_with_delay)
        EventLinker.subscribe("MyEvent", event_callback=handle_event_with_delay)

        event_processor = AsyncIOProcessingService()
        event_emitter = EventEmitter(event_processor=event_processor)

        event_emitter.emit("MyEvent")
        event_emitter.emit("MyEvent")

        print("Closing...")



    main()
    ```

=== "`Async` contexts"

    ```Python linenums="1" hl_lines="3 12 18 19 25"
    import asyncio

    from pyventus.core.processing.asyncio import AsyncIOProcessingService
    from pyventus.events import EventEmitter, EventLinker


    async def handle_event_with_delay():
        await asyncio.sleep(1.5)
        print("Done!")


    async def main():
        print("Starting...")

        EventLinker.subscribe("MyEvent", event_callback=handle_event_with_delay)
        EventLinker.subscribe("MyEvent", event_callback=handle_event_with_delay)

        event_processor = AsyncIOProcessingService()
        event_emitter = EventEmitter(event_processor=event_processor)

        event_emitter.emit("MyEvent")
        event_emitter.emit("MyEvent")

        print("Closing...")
        await event_processor.wait_for_tasks()


    asyncio.run(main())
    ```
