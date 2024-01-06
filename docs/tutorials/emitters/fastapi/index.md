# FastAPI Event Emitter

<p style='text-align: justify;' markdown>
	&emsp;&emsp;The `FastAPIEventEmitter` provides a powerful way to build reactive [FastAPI](https://fastapi.tiangolo.com/)
	applications using an event-driven architecture. It leverages FastAPI's asynchronous [BackgroundTasks](https://fastapi.tiangolo.com/reference/background/)
	to handle events outside the request-response cycle.
</p>

## What is it?

<p style='text-align: justify;' markdown>
	&emsp;&emsp;The `FastAPIEventEmitter` is a concrete implementation of the `EventEmitter` class that utilizes 
	FastAPI's `BackgroundTasks` for event handling. It provides a convenient way to incorporate event-driven 
	functionality into FastAPI applications, allowing you to implement tasks such as sending emails in a 
	decoupled and asynchronous manner.
</p>

## How it Works

<p style='text-align: justify;' markdown>
	&emsp;&emsp;The `FastAPIEventEmitter` handles the emission and processing of events by utilizing the FastAPI's 
	background tasks queue. When an event is emitted, its execution is scheduled into the FastAPI's background
	tasks to run asynchronously after the response is sent.
</p>

## Usage

<p style='text-align: justify;' markdown>
	To start using the `FastAPIEventEmitter`, follow these steps:
</p>

1. **Install Dependencies:**
    Ensure [FastAPI](https://fastapi.tiangolo.com/#installation) and [Pyventus](/pyventus/getting-started/#optional-dependencies) 
    are installed.

2. **Dependency injection and usage:**
    The `FastAPIEventEmitter` integrates fully with `FastAPI` and can be used in routes or elsewhere via dependency 
    injection. As an example, we'll create a simple `FastAPI` app to simulate a non-blocking email notification.
    Create a `main.py` file and add the following code:

   	=== "Without options"

   	   	```Python title="main.py" linenums="1" hl_lines="21"
   	   	import time
   	   	from typing import Dict
   	   	
   	   	from fastapi import FastAPI, Depends
   	   	
   	   	from pyventus import EventLinker
   	   	from pyventus.emitters.fastapi import FastAPIEventEmitter
   	   	
   	   	
   	   	@EventLinker.on("SendEmail")
   	   	def event_callback(email: str):
   	   		print(f"Sending email to: {email}")
   	   		time.sleep(2)
   	   		print("Email sent successfully!")
   	   	

   	   	app = FastAPI()
   	   	
   	   	@app.get("/")
   	   	async def send_email(
   	   	    event_emitter: FastAPIEventEmitter = Depends(FastAPIEventEmitter),
   	   	) -> Dict[str, str]:
   	   	    event_emitter.emit("SendEmail", "email@pyventus.com")
   	   	    return {"message": "Email sent!"}
   	   	
   	   	```

   	=== "With options"

   	   	```Python title="main.py" linenums="1" hl_lines="21"
   	   	import time
   	   	from typing import Dict
   	
   	   	from fastapi import FastAPI, Depends
   	   	
   	   	from pyventus import EventLinker
   	   	from pyventus.emitters.fastapi import FastAPIEventEmitter
   	   	
   	   	
   	   	@EventLinker.on("SendEmail")
   	   	def event_callback(email: str):
   	   	    print(f"Sending email to: {email}")
   	   	    time.sleep(2)
   	   	    print("Email sent successfully!")
   	   	

   	   	app = FastAPI()
   	   	
   	   	@app.get("/")
   	   	async def send_email(
   	   	    event_emitter: FastAPIEventEmitter = Depends(FastAPIEventEmitter.options(debug=False)),
   	   	) -> Dict[str, str]:
   	   	    event_emitter.emit("SendEmail", "email@pyventus.com")
   	   	    return {"message": "Email sent!"}
   	   	
   	   	```

3. **Run the server:**
	<a href="https://fastapi.tiangolo.com/#run-it" target="_blank">Start the app</a> with:

   	```console
   	uvicorn main:app --reload
   	```

   	Open your browser at <a href="http://127.0.0.1:8000/" target="_blank">http://127.0.0.1:8000/</a>. You will
   	see the JSON response as:

   	```JSON
   	{ "message": "Email sent!" }
   	```

   	You'll also be able to see the outputs of the functions in the console logs as follows:

   	```console
   	INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
   	INFO:     Started reloader process [28720]
   	INFO:     Started server process [28722]
   	INFO:     Waiting for application startup.
   	INFO:     Application startup complete.
   	INFO:     127.0.0.1:57926 - "GET / HTTP/1.1" 200 OK

   	Sending email to: email@pyventus.com
   	Email sent successfully!
   	```

## Recap

<p style='text-align: justify;' markdown>
    &emsp;&emsp;As we have seen, the `FastAPIEventEmitter` allows building reactive `FastAPI` apps using an event-driven 
	architecture. By leveraging background tasks, events can be emitted from routes and processed independently without
	blocking responses. This delivers asynchronous and non-blocking behavior for tasks like emails, jobs, streams and
	more. The emitter integrates seamlessly with `FastAPI` via dependency injection.
</p>

<br>
