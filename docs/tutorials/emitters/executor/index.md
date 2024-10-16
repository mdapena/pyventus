# Executor Event Emitter

<p style='text-align: justify;' markdown>
	&emsp;&emsp;The `ExecutorEventEmitter` leverages Python's `concurrent.futures` module to asynchronously execute
	event emissions across threads or processes. This approach helps optimize performance for applications with
	I/O-intensive or CPU-bound tasks by utilizing all available CPU resources.
</p>

## What is it?

<p style='text-align: justify;' markdown>
	&emsp;&emsp;The `ExecutorEventEmitter` inherits from the base `EventEmitter` class and uses an `Executor` interface
	to asynchronously run event emissions in either threads or processes. This flexibility in execution models allows
	you to choose the optimal approach based on your specific application requirements.
</p>

## How it Works

<p style='text-align: justify;' markdown>
	&emsp;&emsp;This class utilizes the concurrent.futures `Executor` interface to handle asynchronous execution of
	event handlers. It can work with either `ThreadPoolExecutor` for thread-based execution or `ProcessPoolExecutor`
	for process-based execution. When an event is emitted, its execution is submitted to the executor to run 
	asynchronously in either threads (ThreadPoolExecutor) or processes (ProcessPoolExecutor).
</p>

!!! warning "ProcessPoolExecutor"

	<p style='text-align: justify;' markdown>
	    &emsp;&emsp;The `ProcessPoolExecutor` utilizes Python's multiprocessing module to run event emissions in
		separate processes instead of threads. This sidesteps the Global Interpreter Lock to enable true parallel
		execution. However, **only pickleable objects can be executed and returned**.
	</p>

## Usage

<p style='text-align: justify;' markdown>
	&emsp;&emsp;Using the `ExecutorEventEmitter` is straightforward. To get started, simply create a new instance of
	the class, pass the desired executor concrete instance and call its `emit()` methods.
</p>

!!! info "Executor Management"

	<p style='text-align: justify;' markdown>
	    &emsp;&emsp;It is important to properly manage the underlying `Executor` when using this event emitter. Once
		finished emitting events, call the `shutdown()` method to signal the executor to free any resources for 
		pending futures or use the `with` statement, which will shut down the Executor automatically.
	</p>

### ThreadPoolExecutor Example

=== "Using the `with` statement"

	```Python linenums="1" hl_lines="23-25"
	import asyncio
	import time
	from concurrent.futures import ThreadPoolExecutor
	
	from pyventus import EventLinker, ExecutorEventEmitter
	
	
	@EventLinker.on("StringEvent")
	def sync_event_callback():
	    print("[Sync] Started!")
	    time.sleep(1)
	    print("[Sync] Finished!")
	
	
	@EventLinker.on("StringEvent")
	async def async_event_callback():
	    print("[Async] Started!")
	    await asyncio.sleep(1)
	    print("[Async] Finished!")
	

	if __name__ == "__main__":
	    with ExecutorEventEmitter() as event_emitter: #(1)!
	        event_emitter.emit("StringEvent")
	        event_emitter.emit("StringEvent")
	```

	1.  The `ExecutorEventEmitter` uses the `ThreadPoolExecutor` by default, but you can customize it by providing your
	    own instance.

=== "Using the `shutdown()` method"

	```Python linenums="1" hl_lines="22-25"
	import asyncio
	import time
	from concurrent.futures import ThreadPoolExecutor
	
	from pyventus import EventLinker, ExecutorEventEmitter
	
	
	@EventLinker.on("StringEvent")
	def sync_event_callback():
	    print("[Sync] Started!")
	    time.sleep(1)
	    print("[Sync] Finished!")
	
	
	@EventLinker.on("StringEvent")
	async def async_event_callback():
	    print("[Async] Started!")
	    await asyncio.sleep(1)
	    print("[Async] Finished!")
	
	if __name__ == "__main__":
	    event_emitter = ExecutorEventEmitter()
	    event_emitter.emit("StringEvent")
	    event_emitter.emit("StringEvent")
	    event_emitter.shutdown(wait=True)
	```

### ProcessPoolExecutor Example

=== "Using the `with` statement"

	```Python linenums="1" hl_lines="23-25"
	import asyncio
	import time
	from concurrent.futures import ProcessPoolExecutor
	
	from pyventus import EventLinker, ExecutorEventEmitter
	
	
	@EventLinker.on("StringEvent")
	def sync_event_callback():
	    print("[Sync] Started!")
	    time.sleep(1)
	    print("[Sync] Finished!")
	
	
	@EventLinker.on("StringEvent")
	async def async_event_callback():
	    print("[Async] Started!")
	    await asyncio.sleep(1)
	    print("[Async] Finished!")
	
	
	if __name__ == "__main__":
	    with ExecutorEventEmitter(executor=ProcessPoolExecutor()) as event_emitter:
	        event_emitter.emit("StringEvent")
	        event_emitter.emit("StringEvent")
	```

=== "Using the `shutdown()` method"

	```Python linenums="1" hl_lines="22-25"
	import asyncio
	import time
	from concurrent.futures import ProcessPoolExecutor
	
	from pyventus import EventLinker, ExecutorEventEmitter
	
	
	@EventLinker.on("StringEvent")
	def sync_event_callback():
	    print("[Sync] Started!")
	    time.sleep(1)
	    print("[Sync] Finished!")
	
	
	@EventLinker.on("StringEvent")
	async def async_event_callback():
	    print("[Async] Started!")
	    await asyncio.sleep(1)
	    print("[Async] Finished!")
	
	if __name__ == "__main__":
	    event_emitter = ExecutorEventEmitter(executor=ProcessPoolExecutor())
	    event_emitter.emit("StringEvent")
	    event_emitter.emit("StringEvent")
	    event_emitter.shutdown(wait=True)
	```

## Recap

<p style='text-align: justify;' markdown>
    &emsp;&emsp;By learning how this event emitter leverages executors for concurrent/parallel execution, you can
	optimize your applications to take full advantage of multicore systems through balanced workload distribution.
	Proper use of this approach can significantly improve performance.
</p>

<br>
