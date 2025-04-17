<style>
    .terminal-command {
        .go:before {
            content: "$";
            padding-right: 1.17647em;
        }
    }
</style>

# Redis Event Emitter

<p style="text-align: justify;">
	&emsp;&emsp;In Pyventus, you can easily integrate Event Emitters with the Redis Queue framework through the Redis Processing Service. Simply create an instance of the Redis Processing Service and pass it as the event processor when setting up the Event Emitter, or you can use the factory method called Redis Event Emitter to handle the setup in a single step.
</p>

=== ":material-console: Manual Configuration"

    ```Python linenums="1" hl_lines="1-4 6-7 10"
    from pyventus.core.processing.redis import RedisProcessingService
    from pyventus.events import EventEmitter
    from redis import Redis
    from rq import Queue

    redis_conn = Redis.from_url("redis://default:redispw@localhost:6379")
    default_queue: Queue = Queue(name="default", connection=redis_conn)

    if __name__ == "__main__":
        event_emitter: EventEmitter = EventEmitter(event_processor=RedisProcessingService(queue=default_queue))
        event_emitter.emit("MyEvent")
    ```

=== ":material-factory: Factory Method"

    ```Python linenums="1" hl_lines="1-3 5-6 9"
    from pyventus.events import EventEmitter, RedisEventEmitter
    from redis import Redis
    from rq import Queue

    redis_conn = Redis.from_url("redis://default:redispw@localhost:6379")
    default_queue: Queue = Queue(name="default", connection=redis_conn)

    if __name__ == "__main__":
        event_emitter: EventEmitter = RedisEventEmitter(queue=default_queue)
        event_emitter.emit("MyEvent")
    ```

<p style="text-align: justify;">
	&emsp;&emsp;By utilizing the Redis Processing Service, the execution of each event emission will be handled by a Redis Queue worker.
</p>

## Practical Example

<p style="text-align: justify;">
	To start using the Event Emitter with Redis Queue, follow these steps:
</p>

1.  <p style="text-align: justify;"><b>Install Dependencies:</b>
        Before proceeding, ensure that you have installed the optional [Redis Queue dependency](../../../getting-started.md/#optional-dependencies).
    </p>

2.  <p style="text-align: justify;"><b>Define Subscribers:</b>
    	If you're using Python's built-in functions, you can skip this step. If you're working with your own functions, you'll need to let Redis Queue know where they are defined. However, to avoid circular dependencies between modules, it's important to place these functions in a separate module from both your worker module and the event emitter.
    </p>

    ```Python title="subscribers.py" linenums="1"
    from pyventus.events import EventLinker


    @EventLinker.on("MyEvent")
    def handle_my_event() -> None:
        print("Handling 'MyEvent'!")
    ```

3.  <p style="text-align: justify;"><b>Create a Worker:</b>
    	Now that you’ve defined your subscribers, the next step is to create the script for the Redis Queue worker. This worker will listen to the Redis Queue pub/sub channel and process each event emission. For more information about Redis Queue workers, you can refer to the official documentation: [RQ Workers](https://python-rq.org/docs/workers/).
    </p>

    === ":material-apple: macOS / :material-linux: Linux"

        ```Python title="worker.py" linenums="1" hl_lines="1 3-4 6 8-9 12 21-24 26-27"
        from multiprocessing import Process

        from redis import Redis
        from rq import Queue, SimpleWorker

        from .subscribers import handle_my_event  # (1)!

        redis_conn = Redis.from_url("redis://default:redispw@localhost:6379")
        default_queue: Queue = Queue(name="default", connection=redis_conn)


        def worker_process() -> None:  # (2)!
            worker = SimpleWorker(connection=redis_conn, queues=[default_queue])
            worker.work()


        if __name__ == "__main__":
            num_workers = 1  # (3)!
            worker_processes: list[Process] = []

            for _ in range(num_workers):  # (4)!
                p = Process(target=worker_process)
                worker_processes.append(p)
                p.start()

            for process in worker_processes:
                process.join()  # (5)!
        ```

        1.  Import the `subscribers.py` module to let Redis Queue know about the available functions.
        2.  Creates a new Worker instance and starts the work loop.
        3.  Set the number of workers. For auto-assignment use: `multiprocessing.cpu_count()`.
        4.  Creates and starts new Processes for each worker.
        5.  Join every worker process.

    === ":fontawesome-brands-windows: Windows"

        ```Python title="worker.py" linenums="1" hl_lines="1 3-5 7 9-10 13-15 25-28 30-31"
        from multiprocessing import Process

        from redis import Redis
        from rq import Queue, SimpleWorker
        from rq.timeouts import TimerDeathPenalty

        from .subscribers import handle_my_event  # (1)!

        redis_conn = Redis.from_url("redis://default:redispw@localhost:6379")
        default_queue: Queue = Queue(name="default", connection=redis_conn)


        def worker_process() -> None:  # (2)!
            class WindowsSimpleWorker(SimpleWorker):  # (3)!
                death_penalty_class = TimerDeathPenalty

            worker = WindowsSimpleWorker(connection=redis_conn, queues=[default_queue])
            worker.work()


        if __name__ == "__main__":
            num_workers = 1  # (4)!
            worker_processes: list[Process] = []

            for _ in range(num_workers):  # (5)!
                p = Process(target=worker_process)
                worker_processes.append(p)
                p.start()

            for process in worker_processes:
                process.join()  # (6)!
        ```

        1.  Import the `subscribers.py` module to let Redis Queue know about the available functions.
        2.  Creates a new Worker instance and starts the work loop.
        3.  A class that inherits from `SimpleWorker` and is used to create a new worker instance in a Windows based system.
        4.  Set the number of workers. For auto-assignment use: `multiprocessing.cpu_count()`.
        5.  Creates and starts new Processes for each worker.
        6.  Join every worker process.

    <p style="text-align: justify;">
    	With the previous configuration in place, you can now launch the Redis Queue worker.
    </p>

    <div class="terminal-command">
    ```console
    py -m worker
    ```
    </div>

4.  <p style="text-align: justify;"><b>Emitting events:</b>
    	Now that your workers are up and running, it’s time to start emitting events! Just create an Event Emitter configured with the Redis Processing Service, and you’re all set to emit an event.
    </p>

    ```Python title="main.py" linenums="1" hl_lines="1 3 6"
    from pyventus.events import EventEmitter, RedisEventEmitter

    from .worker import default_queue

    if __name__ == "__main__":
        event_emitter: EventEmitter = RedisEventEmitter(queue=default_queue)
        event_emitter.emit("MyEvent")
    ```
