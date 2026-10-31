# Observables

<p style="text-align: justify;" markdown>
	&emsp;&emsp;In reactive programming, an `Observable` is a push-based data source that emits values, errors, and completion signals over time. In Pyventus, this concept remains roughly the same and is formalized through the abstract `Observable` base class.
</p>

<p style="text-align: justify;" markdown>
	&emsp;&emsp;However, it's important to note that the `Observable` class cannot be instantiated or used directly on its own, as it serves as an abstract base class for essential shared logic across all observable types, including but not limited to subscription management and notification forwarding. The purpose of this class is to eliminate boilerplate logic and allow concrete implementations to focus solely on the process of notifying subscribed observers rather than the underlying implementation.
</p>

## Key Features

<p style="text-align: justify;" markdown>
  The `Observable` base class provides the following functionality:
</p>

- <p style="text-align: justify;" markdown><b>Subscription Management:</b>
  Each `Observable` instance maintains an internal registry of active subscribers and exposes a unified interface to manage them: `subscribe()` for attaching new observers, `remove()` for detaching them individually, and `remove_all()` to clear the registry entirely.
  </p>

- <p style="text-align: justify;" markdown><b>Thread-Safe Operations:</b>
  Registry access and subscription mutations (`subscribe()`, `remove()`, and `remove_all()`) are synchronized internally to prevent race conditions in multi-threaded or concurrent workflows.
  </p>

- <p style="text-align: justify;" markdown><b>Sync & Async Interoperability:</b>
  Regardless of whether subscribers rely on synchronous or asynchronous execution, the `Observable` base class coordinates and dispatches their notifications seamlessly within the same emission cycle.
  </p>

- <p style="text-align: justify;" markdown><b>Notification Types:</b>
  An `Observable` communicates with its subscribers through three distinct notification types:
  </p>

    - <p style="text-align: justify;" markdown><b>Next:</b>
      Emitted whenever the observable produces a new value, result, or state update.
      </p>
    - <p style="text-align: justify;" markdown><b>Error:</b>
      Emitted when a failure occurs or an exception is explicitly propagated, allowing subscribers to handle the error gracefully.
      </p>
    - <p style="text-align: justify;" markdown><b>Complete:</b>
      Emitted to inform subscribers that the current sequence of emissions has concluded.
      </p>

- <p style="text-align: justify;" markdown><b>Concurrent Signal Dispatch:</b>
  Whenever a `next`, `error`, or `complete` signal is triggered, the `Observable` dispatches the notification to all registered subscribers concurrently rather than sequentially, preventing slow consumers from blocking the propagation of the stream.
  </p>
  
- <p style="text-align: justify;" markdown><b>Reusable Lifecycle:</b>
  Rather than becoming permanently disposed after emitting a `complete` signal, observables in Pyventus are reusable across multiple cycles. Upon completion, the observable automatically clears its subscriber registry, leaving the instance intact and ready to accept new subscriptions for future notifications.
  </p>

- <p style="text-align: justify;" markdown><b>Multicast by Design:</b>
  Built from the ground up to support both unicast and multicast scenarios, an `Observable` seamlessly scales from a single consumer to broadcasting signals across multiple independent subscribers simultaneously.
  </p>

## Custom Observables

<p style="text-align: justify;" markdown>
	&emsp;&emsp;While Pyventus provides built-in observables that cover the most common reactive workflows (`ObservableTask`, `ObservableValue`, and `ObservableStream`), the `Observable` base class can always be extended for any custom requirement. Subclassing the `Observable` base class allows you to implement domain-specific state and emission rules without reimplementing the core boilerplate.
</p>
