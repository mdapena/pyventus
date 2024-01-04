# Celery Event Emitter

<p style='text-align: justify;' markdown>
	&emsp;&emsp;The `CeleryEventEmitter` provides a powerful way to build event-driven applications that can handle high 
	volumes of work in a scalable and asynchronous manner.
</p>

## What is it?

<p style='text-align: justify;' markdown>
	&emsp;&emsp;The `CeleryEventEmitter` is a concrete implementation of the `EventEmitter` that leverages the `Celery`
	distributed task queue system for event handling. It provides the capability to enqueue and process event emissions
	in a scalable and asynchronous manner using Celery. This makes the `CeleryEventEmitter` particularly useful for 
	handling resource-intensive tasks.
</p>

## How it works

<p style='text-align: justify;' markdown>
	&emsp;&emsp;The `CeleryEventEmitter` seamlessly handles the emission and processing of events by utilizing the <a href="https://docs.celeryq.dev/en/stable/getting-started/introduction.html" target="_blank">Celery</a>
	package. Here's a breakdown of how it functions: 
</p>

<ol style='text-align: justify;' markdown>

<li style='text-align: justify;' markdown>**Event emission:**
When an event is triggered, an object is created and submitted as a task to the Celery [queue](/pyventus/api/emitters/celery/#pyventus.emitters.celery.CeleryEventEmitter.Queue).
</li>

<li style='text-align: justify;' markdown>**Task queue:**
The Celery broker stores the task in its queue, where it can be retrieved by workers.
</li>

<li style='text-align: justify;' markdown>**Worker processing:**
Idle Celery workers pull tasks from the queue and execute the event emissions asynchronously in parallel.
</li>

</ol>

## Usage

<p style='text-align: justify;' markdown>
	To start using the `CeleryEventEmitter`, follow these steps:
</p>

<ol style='text-align: justify;' markdown>

<li style='text-align: justify;' markdown>**Install Celery:**
Before proceeding, make sure you have installed the [Celery optional dependency](/pyventus/getting-started/#optional-dependencies).
</li>

<li style='text-align: justify;' markdown>**Define event handlers:**
Let's start with the definition of the event handlers. It is important to note that these functions cannot reside in
the main module. Therefore, we need to create another module where all our event handlers can be placed. For this 
example, let's create a file called `event_handlers.py` and add the handlers to be processed.

```Python title="event_handlers.py" linenums="1" hl_lines="7-11 14-18"
import asyncio
import time

from pyventus.linkers import EventLinker


@EventLinker.on("StringEvent")
async def slow_async_event_callback():
    print("Starting the async slow process...")
    await asyncio.sleep(5)
    print("Finishing the async slow process!")


@EventLinker.on("StringEvent")
def slow_sync_event_callback():
    print("Starting the sync slow process...")
    time.sleep(5)
    print("Finishing the sync slow process!")
```

</li>

<li style='text-align: justify;' markdown>**Celery worker:**
Once you have defined the event handlers, the next step is to configure the Celery workers to process event emissions
within a distributed task queue system. To accomplish this, create a file called `worker.py` and include the following 
worker configuration. These workers will actively listen to a message broker like RabbitMQ or Redis and process 
incoming tasks. For more advanced configurations, refer to the official 
<a href="https://docs.celeryq.dev/en/stable/userguide/application.html" target="_blank">Celery documentation</a>.

<details markdown="1" class="info" open>
<summary>Serialization Security</summary>
<p style='text-align: justify;' markdown>
&emsp;&emsp;It's important to set the content type in the Celery app to `application/x-python-serialize`. This allows the event 
emission object to be serialized and deserialized when tasks are processed. The CeleryEventEmitter queue can 
authenticate and validate any serialized payloads through hashing methods and a secret key. Moreover, a 
custom serializer can be implemented if the default does not meet the specific needs of your project. 
</p>
</details>

```Python title="worker.py" linenums="1" hl_lines="8-12 18 21"
from celery import Celery
from pyventus.emitters.celery import CeleryEventEmitter

# To ensure Python recognizes the existence of the event handlers, we need to import them.
from event_handlers import slow_sync_event_callback, slow_async_event_callback

# Using Redis as a broker for example purpose. For the Redis support 'pip install celery[redis]'
app: Celery = Celery("worker", broker="redis://default:redispw@localhost:6379")

# Optional configuration, see the Celery app user guide.
app.conf.update(result_expires=3600)

# Set the accepted content type to "application/x-python-serialize" in the Celery app.
app.conf.accept_content = ["application/json", "application/x-python-serialize"]

# Create the celery event emitter queue.
celery_event_emitter_queue = CeleryEventEmitter.Queue(celery=app, secret="secret-key")

if __name__ == "__main__":
    app.start()
```
</li>

<li style='text-align: justify;' markdown>**Launching Celery Workers:**
With the previous configuration and setup complete, we can now launch the Celery worker processes. There are a few 
differences depending on your operating system:

<ul>
<li style='text-align: justify;' markdown><b>For Linux/macOS:</b>

```console
celery -A worker worker -l INFO
```

</li>
<li style='text-align: justify;' markdown><b>For Windows:</b> 

```console
celery -A worker worker -l INFO --pool=solo
```

</li>
<li style='text-align: justify;' markdown><b>Specifying a Queue:</b>

```console
celery -A worker worker -l INFO -Q [queue-name]
```

</li>
</ul>

</li>

<li style='text-align: justify;' markdown>**Emitting events:**
To emit events, we will create a `main.py` file where we instantiate the `CeleryEventEmitter` and trigger our first event.

```Python title="main.py" linenums="1" hl_lines="6-8"
from pyventus import EventEmitter
from pyventus.emitters.celery import CeleryEventEmitter

from worker import celery_event_emitter_queue

if __name__ == "__main__":
    event_emitter: EventEmitter = CeleryEventEmitter(queue=celery_event_emitter_queue)
    event_emitter.emit("StringEvent")
```

</li>

</ol>

## Recap

<p style='text-align: justify;' markdown>
	&emsp;&emsp;We've explored how the `CeleryEventEmitter` provides an asynchronous and scalable solution for 
	processing events. Here are the key points:
</p>

<ul style='text-align: justify;' markdown>

<li style='text-align: justify;' markdown>
Events are emitted and serialized into tasks submitted to the Celery queue.
</li>

<li style='text-align: justify;' markdown>
Celery workers then asynchronously process the queued event emissions independently and in parallel.
</li>

<li style='text-align: justify;' markdown>
This distributed approach provides scalable event handling under any workload.
</li>

</ul>

<p style='text-align: justify;' markdown>
	&emsp;&emsp;In summary, the CeleryEventEmitter leverages Celery's distributed task queue architecture to 
	efficiently scale event-driven applications through asynchronous parallel processing of event emissions. 
	This elastic approach allows applications to handle increasing workloads in a scalable manner.
</p>

<br>


