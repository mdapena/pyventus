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
	[tutorials](/tutorials) or [API reference](/api).
</p>

## Requirements

<p style='text-align: justify;' markdown>
	&emsp;&emsp;Pyevents **only requires Python 3.10+** by default, which includes the [`AsyncIOEventEmitter`](/tutorials/emitters/asyncio-event-emitter)
	and the [`ExecutorEventEmitter`](/tutorials/emitters/executor-event-emitter) with no additional dependencies.
	However, your requirements may expand if you opt to use alternative built-in event emitter implementations.
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


<ul style='text-align: justify;' markdown>

<li markdown> [**Redis Queue (RQ)**](https://redis.com/glossary/redis-queue/) ─ Pyventus provides support for Redis 
Queue (RQ) integration through the [`RQEventEmitter`](/tutorials/emitters/rq-event-emitter). The RQEventEmitter 
seamlessly integrates with <a href="https://python-rq.org/" target="_blank">Python-RQ</a>, a widely-used library for
managing task queues using Redis Queue pub/sub system. By incorporating the RQEventEmitter into Pyventus, you gain the
ability to execute event handler callbacks as background jobs using RQ’s asynchronous workers. You can install it using
the following command:

```console
pip install pyventus[rq]
```

</li>

</ul>
