---
hide:
    - navigation
---

<style>
    .terminal-command {
        .go:before {
            content: "$";
            padding-right: 1.17647em;
        }
    }
</style>

<p style="text-align: justify;" markdown>
    &emsp;&emsp;Welcome to the Getting Started section! In this guide, you will learn how to install Pyventus, as well as enable any of its optional dependencies. For more detailed information on how to use this library, you can refer to the Pyventus [Tutorials](tutorials/index.md) or [API Reference](api/index.md).
</p>

## Installation

<p style="text-align: justify;">
    &emsp;&emsp;Pyventus is published as a <a href="https://pypi.org/project/pyventus/" target="_blank">Python package</a> and can be installed using <code>pip</code>, ideally in a <a href="https://realpython.com/python-virtual-environments-a-primer/" target="_blank">virtual environment</a> for proper dependency isolation. To get started, open up a terminal and install Pyventus with the following command:
</p>

<div class="terminal-command">
```console
pip install pyventus
```
</div>

<p style="text-align: justify;">
    &emsp;&emsp;By default, Pyventus relies on the Python standard library and <b>requires Python 3.10 or higher</b> with no additional dependencies aside from <a href="https://pypi.org/project/typing-extensions/" target="_blank"><code>typing-extensions</code></a>, which is primarily used to support advanced typing features in older versions of Python.
</p>

## Optional Dependencies

<p style="text-align: justify;" markdown>
	&emsp;&emsp;While Pyventus primarily relies on the Python standard library, it also supports optional dependencies to access additional features, such as different processing services[^1]. Below is a list of supported integrations:
</p>

### Supported Library Integrations

-   <p style="text-align: justify;" markdown><a href="https://docs.celeryq.dev/en/stable/getting-started/introduction.html" target="_blank"><b>Celery</b></a> ─ 
        Pyventus integrates with Celery through the `CeleryProcessingService`, which is a concrete implementation of the `ProcessingService` interface that leverages the Celery framework to handle the execution of calls. To install Pyventus with Celery support, use the following command:
    </p>

    <div class="terminal-command annotate" markdown>
    ```console
    pip install pyventus[celery] (1)
    ```
    </div>

    1.  <h2 style="margin-top: 0;">Optional Package Dependencies</h2>
        <p style="text-align: justify;">
            &emsp;&emsp;This package also includes optional dependencies. For more information, please visit the <a href="https://docs.celeryq.dev/en/stable/getting-started/introduction.html#bundles" target="_blank">Celery documentation</a>.
        </p>

    ***

-   <p style="text-align: justify;" markdown><a href="https://python-rq.org/" target="_blank"><b>Redis Queue (RQ)</b></a> ─ 
        Pyventus integrates with Redis Queue through the `RedisProcessingService`, which is a concrete implementation of the `ProcessingService` interface that leverages the Redis Queue framework to handle the execution of calls. To install Pyventus with Redis Queue support, use the following command:
    </p>

    <div class="terminal-command annotate" markdown>
    ```console
    pip install pyventus[rq]
    ```
    </div>

### Supported Framework Integrations

-   <p style="text-align: justify;" markdown><a href="https://fastapi.tiangolo.com/" target="_blank"><b>FastAPI</b></a> ─ 
        Pyventus integrates with FastAPI through the `FastAPIProcessingService`, which is a concrete implementation of the `ProcessingService` interface that utilizes the FastAPI's `BackgroundTasks` to handle the execution of calls. To install Pyventus with FastAPI integration, use the following command:
    </p>

    <div class="terminal-command annotate" markdown>
    ```console
    pip install pyventus[fastapi] (1)
    ```
    </div>

    1.  <h2 style="margin-top: 0;">Optional Package Dependencies</h2>
        <p style="text-align: justify;">
            &emsp;&emsp;This package also includes optional dependencies. For more information, please visit the <a href="https://fastapi.tiangolo.com/#additional-optional-dependencies" target="_blank">FastAPI documentation</a>.
        </p>

---

You can install all of these integrations simultaneously using:

<div class="terminal-command" markdown>
```console
pip install pyventus[all]
```
</div>

[^1]: These processing services expand the capabilities of Pyventus by providing different strategies for processing calls. For instance, the `EventEmitter` class leverages these services to decouple the processing of each event emission from the underlying implementation, resulting in a more flexible and efficient execution mechanism that enhances the responsiveness and scalability of event handling.
