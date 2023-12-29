# RQ Event Emitter

<p style='text-align: justify;' markdown>
	&emsp;&emsp;In the previous sections, we explored different event emitters, such as `AsyncIOEventEmitter` and 
	`ExecutorEventEmitter`. Now, let's dive into the `RQEventEmitter`, a powerful tool for handling events that 
	involve intensive asynchronous background tasks.
</p>

## What is it?

<p style='text-align: justify;' markdown>
	&emsp;&emsp;The `RQEventEmitter` is a concrete implementation of the `EventEmitter` that takes advantage of the
	`Redis Queue` pub/sub and `worker` system to execute event emissions.
</p>

<p style='text-align: justify;' markdown>
	&emsp;&emsp;This event emitter is particularly useful when dealing with events that require resource-intensive
	tasks like model optimization or video processing. By leveraging RQ workers, it enables non-blocking execution
	and enhances performance.
</p>

## How it Works

<p style='text-align: justify;' markdown>
	&emsp;&emsp;The `RQEventEmitter` seamlessly handles the emission and processing of events by utilizing the
	[RQ](https://python-rq.org/) package. Here's how it works:
</p>

<ol style='text-align: justify;' markdown>

<li style='text-align: justify;' markdown>**Event emission:**
When an event is emitted, all associated event handlers are bundled into an [EventEmission](/pyventus/api/emitters/#pyventus.EventEmitter.EventEmission) 
object, which is then enqueued into the Redis Queue system.
</li>

<li style='text-align: justify;' markdown>**Workers processing:**
The enqueued event emission object is asynchronously processed by available Python RQ workers, enabling efficient 
parallel execution.
</li>

</ol>

## Usage

<p style='text-align: justify;' markdown>
	To start using the `RQEventEmitter`, follow these steps:
</p>

<ol style='text-align: justify;' markdown>

<li style='text-align: justify;' markdown>**Install Python RQ:**
Before proceeding, make sure you have installed the [Redis Queue (RQ) optional dependency](/pyventus/getting-started/#optional-dependencies).
</li>

<li style='text-align: justify;' markdown>**Python RQ worker configuration:**
The Python RQ workers act as processors for event emission objects. They listen to the `Redis Queue` pub/sub channel
and process tasks when enqueued. To configure the workers, create a file named `worker.py` and include the worker
configuration code. You can refer to the official [RQ documentation](https://python-rq.org/docs/workers/) for 
more advanced configurations.

```Python title="worker.py" linenums="1" hl_lines="9-10 24-25 43-46"
from multiprocessing import Process
from typing import List

from redis import Redis
from rq import Queue, SimpleWorker
from rq.timeouts import TimerDeathPenalty

# Creates a new Redis connection with the given URL
redis_conn = Redis.from_url("redis://default:redispw@localhost:6379")
default_queue: Queue = Queue(name="default", connection=redis_conn)


def worker_process() -> None:
    """Creates a new Worker instance and starts the work loop."""

    class WindowsSimpleWorker(SimpleWorker):
        """
        A class that inherits from SimpleWorker and is used to
        create a new worker instance in a Windows based system.
        """
        death_penalty_class = TimerDeathPenalty

    worker = WindowsSimpleWorker(
        connection=redis_conn,
        queues=[default_queue]
    )
    worker.work()


if __name__ == "__main__":
    # Test connection
    redis_conn.ping()

    # Set the number of workers. For auto-assignment
    # use: multiprocessing.cpu_count()
    num_workers = 1  # Default 1

    # Workers list
    worker_processes: List[Process] = []

    # Creates and starts new
    # Processes for each worker
    for _ in range(num_workers):
        p = Process(target=worker_process)
        worker_processes.append(p)
        p.start()

    # Join every worker process
    for process in worker_processes:
        process.join()
```

</li>

<li style='text-align: justify;' markdown>**Define event handlers:**
After defining the worker file, let's focus on the event handlers. According to the RQ documentation, these
functions should not reside in the main module. Therefore, we need to create another module where all our event
handlers can be placed. For this example, let's create a file called `event_handlers.py` and add the handlers
to be processed.

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

<li style='text-align: justify;' markdown>**Emitting events:**
Once the previous steps have been completed, the RQ workers can be started by running the `worker.py` script. Following
that, a `main.py` file should be created to instantiate an `RQEventEmitter` and configure the `Queue` where the event
emission objects will be enqueued. For full details on the configuration options, please refer to the RQ website and
documentation on the enqueue method settings. At this point, we are ready to emit our first event using the 
`RQEventEmitter`.

```Python title="main.py" linenums="1" hl_lines="8 14-15"
from redis import Redis
from rq import Queue

from pyventus import EventEmitter
from pyventus.emitters.rq import RQEventEmitter

# To ensure Python recognizes the existence of the event handlers, we need to import them.
from event_handlers import slow_sync_event_callback, slow_async_event_callback

redis_conn = Redis.from_url("redis://default:redispw@localhost:6379")
default_queue: Queue = Queue(name="default", connection=redis_conn)

if __name__ == "__main__":
    event_emitter: EventEmitter = RQEventEmitter(queue=default_queue)
    event_emitter.emit("StringEvent")
```

</li>

</ol>

## Recap

<p style='text-align: justify;' markdown>
	&emsp;&emsp;We've seen how the `RQEventEmitter` provides an asynchronous approach to event handling using 
	`Redis Queues` and RQ workers. The main points are:
</p>

<ul style='text-align: justify;' markdown>

<li style='text-align: justify;' markdown>
It leverages existing `Redis Queue` infrastructure for asynchronous task processing.
</li>

<li style='text-align: justify;' markdown>
Event emissions are enqueued in Redis, and workers independently process them.
</li>

<li style='text-align: justify;' markdown>
This distributed model scales efficiently regardless of workload volume.
</li>

</ul>

<br>
