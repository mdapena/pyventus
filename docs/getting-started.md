---
hide:
  - navigation
---

<p style='text-align: justify;' markdown>
    &emsp;&emsp;Pyventus makes it easy to start building event-driven applications. This guide will walk you through
	properly installing and configuring Pyventus on your development environment.
</p>

## Requirements

<p style='text-align: justify;' markdown>
	 &emsp;&emsp;Pyventus was designed for intuitive and lightweight usage. It aims to have minimal dependencies and an
	easy installation process. To use Pyventus, ensure you have the following:
</p>

<ul style='text-align: justify;' markdown>

<li markdown>**Python 3.8** or **higher** </li>
<li markdown>**Asyncio** module (bundled with Python 3.5+)</li>

</ul>

!!! info "Note"

	<p style='text-align: justify;' markdown>
		By default, Pyventus provides the `AsyncioEventEmitter`, which is included with the package. It does not have 
		any additional dependencies beyond the ones mentioned above. However, depending on the optional dependencies
		and event emitter implementations you choose to utilize, the requirements may vary. 
	</p>

## Installation

<p style='text-align: justify;' markdown>
	&emsp;&emsp;Pyventus is published as a Python package and can be installed with `pip`. It is recommended to use a
	virtual environment. Open your terminal and install Pyventus by running the following command:
</p>

``` sh
$ pip install pyventus
```

### Optional Dependencies

<p style='text-align: justify;' markdown>
	&emsp;&emsp;Pyventus follows the <a href="https://www.cs.utexas.edu/users/downing/papers/OCP-1996.pdf" target="_blank">Open-Closed Principle</a>, 
	which allows for easy extension of its functionality through alternate `EventEmitter` implementations. These 
	optional dependencies provide the flexibility to enhance Pyventus without replacing existing features. While
	Pyventus primarily relies on the Python standard library, it also supports optional dependencies to access
	additional features.
</p>


<ul style='text-align: justify;' markdown>

<li markdown> [`Redis Queue (RQ)`](https://redis.com/glossary/redis-queue/) ─ Pyventus provides support for the
optional dependency of Redis Queue (RQ) integration through the RqEventEmitter. The RqEventEmitter seamlessly
integrates with <a href="https://python-rq.org/" target="_blank">Python-RQ</a>, a widely-used library for managing
task queues using Redis pub/sub. By incorporating the `RqEventEmitter` into Pyventus, you gain the ability to 
execute event listeners as background jobs using RQ's asynchronous workers. To take advantage of the Redis Queue
integration with Pyventus, you can install it using the following command:

``` sh
$ pip install pyventus[rq]
```

</li>

</ul>

## What's Next?

<p style='text-align: justify;' markdown>
	With Pyventus installed, explore our documentation:
</p>

<ul style='text-align: justify;' markdown>

<li markdown>View examples and tutorials</li>
<li markdown>Browse API reference</li>
<li markdown>Learn core concepts</li>

</ul>

---


<p style='text-align: center;' markdown>
	<small>*For any installation issues, please refer to our issue tracker on GitHub.*</small>
</p>

