---
hide:
  - navigation
---

<style>
	.go:before {
		content: "$";
		padding-right: 1.17647em;
	}
</style>

<p style='text-align: justify;' markdown>
    &emsp;&emsp;Welcome to the Getting Started section! This guide will help you install and configure Pyventus in
	your project. For more detailed instructions on how to use this package, you can refer to the Pyventus 
    [tutorials](/pyventus/tutorials) or [API reference](/pyventus/api).
</p>

## Requirements

<p style='text-align: justify;' markdown>
	&emsp;&emsp;Pyevents **only requires Python 3.10+** by default, which includes the [`AsyncIOEventEmitter`](/pyventus/tutorials/emitters/asyncio)
	and the [`ExecutorEventEmitter`](/pyventus/tutorials/emitters/executor) with no additional dependencies. However, 
	your requirements may expand if you opt to use alternative built-in event emitter implementations.
</p>

## Installation

<p style='text-align: justify;' markdown>
	&emsp;&emsp;Pyventus is available as a Python package and can be easily installed using `pip`. Open your terminal
	and execute the following command to install it:
</p>

```console
pip install pyventus
```

## Optional Dependencies

<p style='text-align: justify;' markdown>
	&emsp;&emsp; While Pyventus primarily relies on the Python standard library, it also supports optional dependencies
	to access additional features, as shown below:
</p>


### Supported Library Integrations

<ul style='text-align: justify;' markdown>

<li class="annotate" markdown>
<a href="https://docs.celeryq.dev/en/stable/getting-started/introduction.html" target="_blank">**Celery**</a> ─ 
Pyventus integrates with Celery using the [`CeleryEventEmitter`](/pyventus/tutorials/emitters/celery), enabling
event emissions to be executed on Celery worker nodes to improve task processing. To install Pyventus with Celery 
support, use the following command:

```console
pip install pyventus[celery] (1)
```
</li>

1.  <h2 style="margin-top: 0;">Optional Package Dependencies</h2>
    &emsp;&emsp;This package includes some optional dependencies. For more information, please visit the
    <a href="https://docs.celeryq.dev/en/stable/getting-started/introduction.html#bundles" target="_blank">Celery bundles documentation</a>.

    > These optional dependencies can be installed as described in their individual documentation. For example:
       ```console
       install celery[...]
       ```

---
<li markdown> 
<a href="https://python-rq.org/" target="_blank">**Redis Queue (RQ)**</a> ─ 
Pyventus integrates with Redis Queue (RQ) using the [`RQEventEmitter`](/pyventus/tutorials/emitters/rq/), allowing 
event emissions to run as background jobs through RQ's asynchronous workers. To install Pyventus with RQ support,
use the following command:

```console
pip install pyventus[rq]
```
</li>


### Supported Framework Integrations

</ul>

<ul style='text-align: justify;' markdown>

<li class="annotate" markdown>
<a href="https://fastapi.tiangolo.com/" target="_blank">**FastAPI**</a> ─ 
Pyventus integrates with the FastAPI framework using the [`FastAPIEventEmitter`](/pyventus/tutorials/emitters/fastapi), 
enabling event-driven architectures to be built directly into FastAPI applications. The emitter leverages FastAPI's 
background tasks to asynchronously process event emissions without blocking responses. To install Pyventus with 
FastAPI integration, use the following command:

```console
pip install pyventus[fastapi] (1)
```
</li>

1.  <h2 style="margin-top: 0;">Optional Package Dependencies</h2>
    &emsp;&emsp;This package includes some optional dependencies. For more information, please visit the
    <a href="https://fastapi.tiangolo.com/#optional-dependencies" target="_blank">FastAPI optional dependencies</a>.

    >  These optional dependencies can be installed as described in their individual documentation. For example:
       ```console
       install fastapi[...]
       ```

</ul>

---

You can install all of them with:

```console
pip install pyventus[all]
```

<br>
