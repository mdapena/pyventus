---
hide:
  - navigation
---

<p style='text-align: justify;' markdown>
    &emsp;&emsp;Pyventus makes it easy to start building event-driven applications. This guide will walk you through
	properly installation and configuration of Pyventus on your development environment.
</p>

## Installation

<p style='text-align: justify;' markdown>
	&emsp;&emsp;Pyventus is available as a Python package and can be easily installed using `pip`. It is recommended to use a
	virtual environment. Open your terminal and execute the following command to install Pyventus:
</p>

``` sh
$ pip install pyventus
```

## Requirements

<p style='text-align: justify;' markdown>
	 &emsp;&emsp;Pyventus was designed for intuitive and lightweight usage. It aims to have minimal dependencies and an
	easy installation process. Ensure that you have **Python 3.8** or a **higher** version installed to use Pyventus.
</p>

!!! info "Additional Event Emitters"

	<p style='text-align: justify;' markdown>
		By default, Pyventus includes the default `AsyncioEventEmitter` with no additional dependencies required.
		However, depending on your choice of optional dependencies and event emitter implementations, the
		requirements may vary.
	</p>

## Optional Dependencies

<p style='text-align: justify;' markdown>
	&emsp;&emsp;Pyventus follows the <a href="https://www.cs.utexas.edu/users/downing/papers/OCP-1996.pdf" target="_blank">Open-Closed Principle</a>, 
	allowing easy extension of its functionality through alternate `EventEmitter` implementations. While Pyventus
	primarily relies on the Python standard library, it also supports optional dependencies to access additional
	features.
</p>


<ul style='text-align: justify;' markdown>

<li markdown> [`Redis Queue (RQ)`](https://redis.com/glossary/redis-queue/) ─ Pyventus provides support for Redis Queue
(RQ) integration through the RqEventEmitter. The RqEventEmitter seamlessly integrates with <a href="https://python-rq.org/" target="_blank">Python-RQ</a>, 
a widely-used library for managing task queues using Redis pub/sub. By incorporating the RqEventEmitter into Pyventus,
you gain the ability to execute event listeners as background jobs using RQ’s asynchronous workers. You can install
it using the following command:

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
	<small>*For any installation issues, please refer to our **<a href="#" target="_blank">issue tracker</a>** on GitHub.*</small>
</p>

