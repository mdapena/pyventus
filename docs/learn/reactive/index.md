---
hide:
  - toc
---

# Reactive Programming

<p style="text-align: justify;" markdown>
	&emsp;&emsp;Reactive programming is a declarative programming paradigm centered around data streams and the propagation of change. Grounded in the Observer pattern[^1], it replaces active polling with a push-based model where data producers emit notifications over time, and subscribed consumers automatically react as new values arrive, errors occur, or streams complete.
</p>

<p style="text-align: justify;" markdown>
	&emsp;&emsp;In the context of Pyventus, reactive programming is implemented through an extended form of the Observer pattern tailored for asynchronous and event-driven execution. Rather than relying on a single state-update notification as in the classical pattern, Pyventus structures communication around a three-channel push protocol (`next`, `error`, and `complete`) and supports both unicast and multicast propagation out of the box.
</p>

<p style="text-align: justify;" markdown>
	&emsp;&emsp;What sets Pyventus's implementation apart is its focus on ergonomics and native interoperability between synchronous and asynchronous execution. Instead of requiring complex operator chains or rigid class hierarchies, Pyventus allows you to transform standard Python constructs directly into observables and attach `sync` or `async` callbacks using flexible subscription patterns.
</p>

[^1]: For further reading about the Observer Pattern, you can refer to the <a href="https://en.wikipedia.org/wiki/Observer_pattern" target="_blank">Observer pattern</a> on Wikipedia.
