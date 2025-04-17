<style>
    .terminal-command {
        .go:before {
            content: "$";
            padding-right: 1.17647em;
        }
    }
</style>

# FastAPI Event Emitter

<p style="text-align: justify;">
	&emsp;&emsp;In Pyventus, you can easily integrate Event Emitters with the FastAPI framework through the FastAPI Processing Service. Simply create an instance of the FastAPI Processing Service and pass it as the event processor when setting up the Event Emitter, or you can use the factory method called FastAPI Event Emitter to handle the setup in a single step.
</p>

=== ":material-console: Manual Configuration"

    ```Python linenums="1" hl_lines="1-3 5 9 10"
    from fastapi import BackgroundTasks, FastAPI
    from pyventus.core.processing.fastapi import FastAPIProcessingService
    from pyventus.events import EventEmitter

    app = FastAPI()


    @app.get("/")
    def read_root(background_tasks: BackgroundTasks):
    	event_emitter = EventEmitter(event_processor=FastAPIProcessingService(background_tasks))
    	event_emitter.emit("MyEvent")
    	return {"Event": "Emitted"}
    ```

=== ":material-factory: Factory Method"

    ```Python linenums="1" hl_lines="1-2 4 8"
    from fastapi import Depends, FastAPI
    from pyventus.events import EventEmitter, FastAPIEventEmitter

    app = FastAPI()


    @app.get("/")
    def read_root(event_emitter: EventEmitter = Depends(FastAPIEventEmitter())):
    	event_emitter.emit("MyEvent")
    	return {"Event": "Emitted"}
    ```

<p style="text-align: justify;">
	&emsp;&emsp;By utilizing the FastAPI Processing Service, the execution of each event emission will be handled by the FastAPI's Background Tasks system.
</p>

## Practical Example

<p style="text-align: justify;">
	To start using the Event Emitter with FastAPI, follow these steps:
</p>

1.  <p style="text-align: justify;"><b>Install Dependencies:</b>
        Before proceeding, ensure that you have installed the optional [FastAPI dependency](../../../getting-started.md/#optional-dependencies).
    </p>

2.  <p style="text-align: justify;"><b>Subscribe and Emit:</b>
        Once you have everything installed and configured, using Pyventus with FastAPI is straightforward. Simply define your subscribers and events, instantiate an Event Emitter configured for FastAPI, and emit your events.
    </p>

    ```Python title="main.py" linenums="1" hl_lines="3-4 7-8 14 20 22"
    import time

    from fastapi import Depends, FastAPI
    from pyventus.events import EventEmitter, EventLinker, FastAPIEventEmitter


    @EventLinker.on("SendEmail")
    def handle_email_notification(email: str) -> None:
    	print(f"Sending email to: {email}")
    	time.sleep(2.5)  # Simulate sending delay.
    	print("Email sent successfully!")


    app = FastAPI()


    @app.get("/email")
    def send_email(
    	email_to: str,
    	event_emitter: EventEmitter = Depends(FastAPIEventEmitter()),
    ) -> None:
    	event_emitter.emit("SendEmail", email_to)
    	return {"message": "Email sent!"}
    ```

    To start the FastAPI server, run the following command:

    <div class="terminal-command">
    ```console
    fastapi dev main.py
    ```
    </div>

    Open your browser and navigate to <a href="http://127.0.0.1:8000/email?email_to=email@email.com" target="_blank">http://127.0.0.1:8000/email?email_to=email@email.com</a>. You should see the following JSON response:

    ```JSON
    { "message": "Email sent!" }
    ```

    Additionally, you will be able to view the output of the functions in the console logs.

    ```console
    INFO   Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
    INFO   Started reloader process [12604] using WatchFiles
    INFO   Started server process [7008]
    INFO   Waiting for application startup.
    INFO   Application startup complete.
    INFO   127.0.0.1:49763 - "GET /email?email_to=email@email.com HTTP/1.1" 200
    Sending email to: email@email.com
    Email sent successfully!
    ```
