# AsyncIO Event Emitter

<p style='text-align: justify;' markdown>
	&emsp;&emsp;Now that we've covered the base `EventEmitter` interface, let's examine one of its official
	implementations: the `AsyncIOEventEmitter`.
</p>

## What is it?

<p style='text-align: justify;' markdown>
	&emsp;&emsp;The `AsyncIOEventEmitter` is a class that inherits from `EventEmitter` and uses the `AsyncIO`
	framework to handle the execution of event emissions.
</p>

## How it works

<p style='text-align: justify;' markdown>
	&emsp;&emsp;The `AsyncIOEventEmitter` handles the event emission differently depending on whether it is operating in
	a synchronous or asynchronous execution context. In synchronous contexts, it will automatically start an event loop
	to run handlers concurrently. In asynchronous contexts, it leverages any existing event loop. Let's explore the
	AsyncIOEventEmitter's behavior in more detail:
</p>

### Sync context

<p style='text-align: justify;' markdown>
	&emsp;&emsp;When running without an existing `AsyncIO` event loop, the `AsyncIOEventEmitter` automatically
	starts a new loop using `asyncio.run()`. Within this loop, it executes the event emission. The 
	loop then waits for all scheduled tasks to finish before closing. This preserves synchronous 
	execution while still gaining the benefits of the concurrent execution.
</p>

### Async context

<p style='text-align: justify;' markdown>
	&emsp;&emsp;In an asynchronous context where an event loop is already running, the event emission is scheduled and 
	processed on that existing loop. 
</p>

!!! warning "AsyncIO Event Loop Behavior"

	<p style='text-align: justify;' markdown>
	    If the event loop is closed before all callbacks complete, any remaining scheduled tasks will be canceled.
	</p>

## Usage

<p style='text-align: justify;' markdown>
	&emsp;&emsp;Using the `AsyncIOEventEmitter` is straightforward. To get started, simply create a new instance of
	the class and call its `emit()` methods, as shown below:
</p>

=== "`Sync` context"

	```Python title="Usage of the AsyncIOEventEmitter" linenums="1" hl_lines="14-16 19"
	from pyventus import EventLinker, EventEmitter, AsyncIOEventEmitter

	
	@EventLinker.on("StringEvent")
	def sync_event_callback():
	    print("Sync event callback!")
	
	
	@EventLinker.on("StringEvent")
	async def async_event_callback():
	    print("Async event callback!")
	
	
	def main():
	    event_emitter: EventEmitter = AsyncIOEventEmitter()
	    event_emitter.emit("StringEvent")

	
	main()
	```

=== "`Async` context"

	```Python title="Usage of the AsyncIOEventEmitter" linenums="1" hl_lines="14-17 19"
	import asyncio
	from pyventus import EventLinker, EventEmitter, AsyncIOEventEmitter
	
	@EventLinker.on("StringEvent")
	def sync_event_callback():
	    print("Sync event callback!")
	
	
	@EventLinker.on("StringEvent")
	async def async_event_callback():
	    print("Async event callback!")
	
	
	async def main():
	    event_emitter: EventEmitter = AsyncIOEventEmitter()
	    event_emitter.emit("StringEvent")
	    await asyncio.sleep(0.5) # (1)!
	
	asyncio.run(main())
	```

	1.  By awaiting the `asyncio.sleep(0.5)`, we ensure the existing event loop continues running long enough for all
        scheduled tasks to finish processing before concluding. Without waiting, closing the loop prematurely could
        cause unfinished tasks to be canceled.

## Recap

<p style='text-align: justify;' markdown>
	We've explored the `AsyncIOEventEmitter` class in depth:
</p>

<ul style='text-align: justify;' markdown>

<li markdown>
The `AsyncIOEventEmitter` inherits from the `EventEmitter` class
</li>

<li markdown>
To use it, instantiate the class and call methods like `emit()`
</li>

</ul>

<p style='text-align: justify;' markdown>
	&emsp;&emsp;By understanding these concepts, you can effectively utilize the `AsyncIOEventEmitter` to emit events
	in both synchronous and asynchronous contexts, benefiting from the concurrency features provided by the `AsyncIO`
	framework.
</p>

<br>
