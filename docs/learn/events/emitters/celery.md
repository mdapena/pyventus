<style>
    .terminal-command {
        .go:before {
            content: "$";
            padding-right: 1.17647em;
        }
    }
</style>

# Celery Event Emitter

<p style="text-align: justify;">
	&emsp;&emsp;In Pyventus, you can easily integrate Event Emitters with the Celery framework through the Celery Processing Service. Simply create an instance of the Celery Processing Service and pass it as the event processor when setting up the Event Emitter, or you can use the factory method called Celery Event Emitter to handle the setup in a single step.
</p>

=== ":material-console: Manual Configuration"

    ```Python linenums="1" hl_lines="1-2 4 6"
    from pyventus.core.processing.celery import CeleryProcessingService
    from pyventus.events import EventEmitter

    from .worker import celery_app  # (1)!

    event_emitter = EventEmitter(event_processor=CeleryProcessingService(celery=celery_app))
    event_emitter.emit("MyEvent")
    ```

    1.  In order to process each event emission, you must have a Celery app configured with a broker and have workers listening to it. The Celery app in this example comes from:

        ```Python title="worker.py" linenums="1" hl_lines="1 2 5 8 12"
        from celery import Celery
        from pyventus.core.processing.celery import CeleryProcessingService

        # Initialize a Celery app with Redis as an example broker; other brokers are also supported.
        celery_app: Celery = Celery(broker="redis://default:redispw@localhost:6379")

        # Register the Pyventus shared task.
        CeleryProcessingService.register()

        # Start the Celery worker.
        if __name__ == "__main__":
            celery_app.start()
        ```

=== ":material-factory: Factory Method"

    ```Python linenums="1" hl_lines="1 3 6"
    from pyventus.events import CeleryEventEmitter

    from .worker import celery_app  # (1)!


    event_emitter = CeleryEventEmitter(celery=celery_app)
    event_emitter.emit("MyEvent")
    ```

    1.  In order to process each event emission, you must have a Celery app configured with a broker and have workers listening to it. The Celery app in this example comes from:

        ```Python title="worker.py" linenums="1" hl_lines="1 2 5 8 12"
        from celery import Celery
        from pyventus.core.processing.celery import CeleryProcessingService

        # Initialize a Celery app with Redis as an example broker; other brokers are also supported.
        celery_app: Celery = Celery(broker="redis://default:redispw@localhost:6379")

        # Register the Pyventus shared task.
        CeleryProcessingService.register()

        # Start the Celery worker.
        if __name__ == "__main__":
            celery_app.start()
        ```

<p style="text-align: justify;">
	&emsp;&emsp;By utilizing the Celery Processing Service, the execution of each event emission will be handled by a Celery worker.
</p>

## Practical Example

<p style="text-align: justify;">
	To start using the Event Emitter with Celery, follow these steps:
</p>

1.  <p style="text-align: justify;"><b>Install Dependencies:</b>
        Before proceeding, ensure that you have installed the optional [Celery dependency](../../../getting-started.md/#optional-dependencies) along with the appropriate broker.
    </p>

2.  <p style="text-align: justify;"><b>Define Subscribers:</b>
    	If you're using Python's built-in functions, you can skip this step. If you're working with your own functions, you'll need to let Celery know where they are defined. However, to avoid circular dependencies between modules, it's important to place these functions in a separate module from both your worker module and the event emitter.
    </p>

    ```Python title="subscribers.py" linenums="1"
    from pyventus.events import EventLinker


    @EventLinker.on("MyEvent")
    def handle_my_event() -> None:
        print("Handling 'MyEvent'!")
    ```

3.  <p style="text-align: justify;"><b>Create a Worker:</b>
    	Now that you’ve defined your subscribers, the next step is to create the script for the Celery worker. This worker will listen to the Celery distributed task queue and process each event emission.
    </p>

    ```Python title="worker.py" linenums="1" hl_lines="1 2 4 6 8 11"
    from celery import Celery
    from pyventus.core.processing.celery import CeleryProcessingService

    from .subscribers import handle_my_event  # (1)!

    celery_app: Celery = Celery(broker="redis://default:redispw@localhost:6379")  # (2)!

    CeleryProcessingService.register()  # (3)!

    if __name__ == "__main__":
        celery_app.start()  # (4)!
    ```

    1.  Import the `subscribers.py` module to let Celery know about the available functions.
    2.  Initialize a Celery app with Redis; other Celery-supported brokers can also be used.
    3.  Register the Pyventus shared task.
    4.  Start the Celery worker only if this script is run directly.

    <p style="text-align: justify;">
    	With the previous configuration in place, you can now launch the Celery worker. There are a few differences depending on your operating system:
    </p>

    === ":material-apple: macOS / :material-linux: Linux"

        <div class="terminal-command annotate" markdown>
        ```console
        celery -A worker worker -l INFO (1)
        ```
        </div>

        1.  For more information on configuring and using Celery workers, please refer to the [Celery Workers Guide](https://docs.celeryq.dev/en/stable/userguide/workers.html).

    === ":fontawesome-brands-windows: Windows"

        <div class="terminal-command annotate" markdown>
        ```console
        celery -A worker worker -l INFO --pool=solo (1)
        ```
        </div>

        1.  For more information on configuring and using Celery workers, please refer to the [Celery Workers Guide](https://docs.celeryq.dev/en/stable/userguide/workers.html).

4.  <p style="text-align: justify;"><b>Emitting events:</b>
    	Now that your workers are up and running, it’s time to start emitting events! Just create an Event Emitter configured with the Celery Processing Service, and you’re all set to emit an event.
    </p>

    ```Python title="main.py" linenums="1" hl_lines="1 3 5 6"
    from pyventus.events import CeleryEventEmitter, EventEmitter

    from .worker import celery_app

    event_emitter: EventEmitter = CeleryEventEmitter(celery=celery_app)  # (1)!
    event_emitter.emit("MyEvent")
    ```

    1.  If you're working with a specific queue name, you can set it up when creating the Celery Processing Service or its counterpart, the Celery Event Emitter, as follows:

        ```Python title="main.py" linenums="1" hl_lines="5"
        from pyventus.events import CeleryEventEmitter, EventEmitter

        from .worker import celery_app

        event_emitter: EventEmitter = CeleryEventEmitter(celery=celery_app, queue="QueueName")
        event_emitter.emit("MyEvent")
        ```

        ```Python title="main.py" linenums="1" hl_lines="6"
        from pyventus.core.processing.celery import CeleryProcessingService
        from pyventus.events import EventEmitter

        from .worker import celery_app

        event_emitter = EventEmitter(event_processor=CeleryProcessingService(celery=celery_app, queue="QueueName"))
        event_emitter.emit("MyEvent")
        ```

    !!! warning "Security Considerations"

        <p style="text-align: justify;" markdown>
            &emsp;&emsp;To enhance security in message communication, it is recommended to employ the Celery `auth` serializer. While the Celery Processing Service is serializer-agnostic, it relies on the pickling process to convert callbacks and their arguments into transmittable data, making security a critical consideration. For more information, please refer to: [Celery Security](https://docs.celeryq.dev/en/stable/userguide/security.html).
        </p>
