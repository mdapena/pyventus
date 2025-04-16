# Executor Event Emitter

<p style="text-align: justify;">
	&emsp;&emsp;In Pyventus, you can easily integrate Event Emitters with threads or processes through the Executor Processing Service. Simply create an instance of the Executor Processing Service and pass it as the event processor when setting up the Event Emitter, or you can use the factory method called Executor Event Emitter to handle the setup in a single step.
</p>

=== ":material-console: Manual Configuration"

    ```Python linenums="1" hl_lines="1 3 8 10"
    from concurrent.futures import ThreadPoolExecutor

    from pyventus.core.processing.executor import ExecutorProcessingService
    from pyventus.events import EventEmitter


    if __name__ == "__main__":
        executor = ThreadPoolExecutor()

        event_emitter = EventEmitter(event_processor=ExecutorProcessingService(executor))
        event_emitter.emit("MyEvent")

        executor.shutdown()
    ```

=== ":material-factory: Factory Method"

    ```Python linenums="1" hl_lines="1 3 8 10"
    from concurrent.futures import ThreadPoolExecutor

    from pyventus.events import ExecutorEventEmitter



    if __name__ == "__main__":
        executor = ThreadPoolExecutor()

        event_emitter = ExecutorEventEmitter(executor)
        event_emitter.emit("MyEvent")

        executor.shutdown()
    ```

=== ":material-code-block-tags: Context Manager"

    ```Python linenums="1" hl_lines="1 3 7"
    from concurrent.futures import ThreadPoolExecutor

    from pyventus.events import ExecutorEventEmitterCtx


    if __name__ == "__main__":
        with ExecutorEventEmitterCtx(executor=ThreadPoolExecutor()) as event_emitter:
            event_emitter.emit("MyEvent")
    ```

<p style="text-align: justify;">
	&emsp;&emsp;By utilizing the Executor Processing Service, the execution of each event emission will be handled by the given Thread/Process executor.
</p>

## Executor Management

<p style="text-align: justify;" markdown>
    &emsp;&emsp;It is important to properly manage the underlying Executor when using the Executor Processing Service. Once you've finished emitting events, call the `shutdown()` method to signal the executor to free any resources associated with pending futures, or use the `with` statement, which will automatically shut down the Executor.
</p>

## Practical Example

=== "Using `ThreadPoolExecutor`"

    ```Python linenums="1" hl_lines="2 4 18-21"
    import time
    from concurrent.futures import ThreadPoolExecutor

    from pyventus.events import EventLinker, ExecutorEventEmitter


    def handle_event_with_delay():
        time.sleep(1.5)
        print("Done!")


    if __name__ == "__main__":
        print("Starting...")

        EventLinker.subscribe("MyEvent", event_callback=handle_event_with_delay)
        EventLinker.subscribe("MyEvent", event_callback=handle_event_with_delay)

        with ThreadPoolExecutor() as executor:
            event_emitter = ExecutorEventEmitter(executor)
            event_emitter.emit("MyEvent")
            event_emitter.emit("MyEvent")

        print("Closing...")
    ```

=== "Using `ProcessPoolExecutor`"

    ```Python linenums="1" hl_lines="1 3 19-22"
    from concurrent.futures import ProcessPoolExecutor

    from pyventus.events import EventLinker, ExecutorEventEmitter

    def fibonacci(n):
        if n <= 1:
            return n
        return fibonacci(n - 1) + fibonacci(n - 2)

    if __name__ == "__main__":
        print("Starting...")

        EventLinker.subscribe(
            "Fibonacci",
            event_callback=fibonacci,
            success_callback=print,
        )

        with ProcessPoolExecutor() as executor:
            event_emitter = ExecutorEventEmitter(executor)
            event_emitter.emit("Fibonacci", 35)
            event_emitter.emit("Fibonacci", 35)

        print("Closing...")
    ```

    !!! warning "Picklable Objects Required for `ProcessPoolExecutor`"

        <p style="text-align: justify;" markdown>
            &emsp;&emsp;When working with the `ProcessPoolExecutor`, it is essential to ensure that all objects involved in the event emission are picklable.
        </p>
