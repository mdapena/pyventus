import gc
import random
from dataclasses import dataclass
from enum import Enum
from math import isqrt
from statistics import mean, median
from time import perf_counter
from typing import Final

import pyventus
from tqdm.auto import tqdm

# Attempt to import EventLinker, EventEmitter and AsyncIOEventEmitter from
# pyventus.events. If the import fails, fall back to importing from pyventus.
try:
    from pyventus.events import AsyncIOEventEmitter, EventEmitter, EventLinker
except ImportError:
    from pyventus import AsyncIOEventEmitter, EventEmitter, EventLinker  # type: ignore[attr-defined, no-redef]


class EventEmitterBenchmark:
    """A benchmark class for evaluating the performance of the EventEmitter's emit method."""

    PYVENTUS_VERSION: Final[str] = pyventus.__version__
    """The version of the Pyventus library being used for the benchmark."""

    class EventSubscriptionMode(Enum):
        """Defines the behavior of event subscriptions in the benchmark."""

        SINGLE = "SINGLE"
        """Subscribe exclusively to the specified event; each subscriber is limited to one event only."""

        RANDOM = "RANDOM"
        """Subscribe to the specified event along with a random selection of additional events from the registry."""

        ALL = "ALL"
        """Subscribe to the specified event and all other registered events."""

    class OneTimeSubscriptionMode(Enum):
        """Defines the behavior of one-time subscriptions in the benchmark."""

        NONE = "NONE"
        """No one-time subscribers will be registered; the `once` property is set to `False`."""

        RANDOM = "RANDOM"
        """The `once` property is randomized; some subscriptions may be one-time subscribers while others are not."""

        ALL = "ALL"
        """All subscriptions will be one-time subscribers; the `once` property is always set to `True`."""

        @staticmethod
        def once_value(mode: "EventEmitterBenchmark.OneTimeSubscriptionMode") -> bool:
            """
            Determine the 'once' value based on the specified one-time subscription mode.

            :param mode: The one-time subscription mode to evaluate.
            :return: `True` or `False` based on the specified mode.
            """
            if mode == EventEmitterBenchmark.OneTimeSubscriptionMode.NONE:
                return False
            elif mode == EventEmitterBenchmark.OneTimeSubscriptionMode.RANDOM:
                return bool(random.getrandbits(1))
            elif mode == EventEmitterBenchmark.OneTimeSubscriptionMode.ALL:
                return True
            else:
                raise ValueError(f"Invalid mode: {mode}")

    @dataclass(frozen=True, slots=True)
    class Measurement:
        """Represents a measurement of an event emission benchmark."""

        num_subscriptions: int
        """The number of subscriptions registered in the `EventLinker`."""

        execution_time: float
        """The time taken to execute the event emission, measured in seconds."""

    @dataclass
    class Report:
        """Represents the results of the benchmark test, including various metrics and configurations."""

        title: str
        """The title of the benchmark report."""

        pyventus_version: str
        """The version of the Pyventus library used during the benchmark."""

        benchmark_duration: float
        """The total duration of the benchmark test, measured in seconds."""

        event_subscription_mode: str
        """The mode of event subscription used during the benchmark."""

        onetime_subscription_mode: str
        """The mode of one-time subscription used during the benchmark."""

        subscription_sizes: list[int]
        """A list of different subscription sizes used in the benchmark."""

        num_repeats: int
        """The number of times the benchmark was repeated."""

        num_executions: int
        """The total number of executions performed during the benchmark."""

        measurements: list["EventEmitterBenchmark.Measurement"]
        """A list of measurements taken during the benchmark."""

    @staticmethod
    def dummy_event_callback() -> None:
        """A no-op callback used for benchmarking."""
        pass

    def __init__(
        self,
        event_subscription_mode: EventSubscriptionMode,
        onetime_subscription_mode: OneTimeSubscriptionMode,
        subscription_sizes: list[int],
        num_repeats: int,
        num_executions: int,
    ) -> None:
        """
        Initialize an instance of `EventEmitterBenchmark`.

        :param event_subscription_mode: The mode of event subscription to be used during the benchmark.
        :param onetime_subscription_mode: The mode for one-time subscriptions to be used during the benchmark.
        :param subscription_sizes: A list of different subscription sizes to test during the benchmark.
        :param num_repeats: The number of times to repeat the benchmark for reliability.
        :param num_executions: The number of times to execute the emit method per repeat.
        """
        # Set the benchmark title.
        self.title: str = (
            f"EventEmitterBenchmark(event_subscription_mode={event_subscription_mode.value}, "
            f"onetime_subscription_mode={onetime_subscription_mode.value})"
        )

        # Store the subscription sizes for benchmarking.
        self.subscription_sizes: list[int] = subscription_sizes

        # Set the event and one-time subscription modes.
        self.event_subscription_mode: EventEmitterBenchmark.EventSubscriptionMode = event_subscription_mode
        self.onetime_subscription_mode: EventEmitterBenchmark.OneTimeSubscriptionMode = onetime_subscription_mode

        # Store the repeat and execution counts for the benchmark.
        self.num_repeats = num_repeats
        self.num_executions = num_executions

        # Initialize the timer and the list to store benchmark measurements.
        self.timer = perf_counter

    def __setup(self, num_subscriptions: int) -> tuple[type[EventLinker], EventEmitter]:
        """
        Set up a new event emitter with an isolated EventLinker configured for benchmarking.

        **Notes:**

        -   A mathematical formula is used to proportionally subdivide the number of events and
            subscribers based on the given number of subscriptions.

        -   Depending on the event subscription mode, the number of subscribers per event may exceed the
            calculated proportion. For example, if the event subscription mode is set to `ALL`, each subscriber
            will be registered across all event sets, meaning that the length of each event set will be equal
            to `num_subscriptions`.

        :param num_subscriptions: The total number of subscriptions to register in the event linker registry.
        :return: A tuple containing an isolated EventLinker and an EventEmitter.
        """

        # Define a new isolated event linker.
        class IsolatedEventLinker(EventLinker): ...

        # Calculate the number of events and subscribers based on
        # a proportional subdivision of the number of subscriptions.
        num_events: int = isqrt(num_subscriptions)
        num_subscribers: int = num_subscriptions // num_events

        # Calculate any remaining subscriptions.
        remaining: int = num_subscriptions - (num_events * num_subscribers)

        # Create a list of event names.
        event_names: list[str] = [f"Event{e}" for e in range(num_events)]

        # Subscribe to events based on the specified mode.
        if self.event_subscription_mode == self.__class__.EventSubscriptionMode.SINGLE:
            for event in event_names:
                for _ in range(num_subscribers):
                    IsolatedEventLinker.subscribe(
                        event,
                        event_callback=self.__class__.dummy_event_callback,
                        once=self.__class__.OneTimeSubscriptionMode.once_value(self.onetime_subscription_mode),
                    )
        elif self.event_subscription_mode == self.__class__.EventSubscriptionMode.RANDOM:
            for event in event_names:
                for _ in range(num_subscribers):
                    IsolatedEventLinker.subscribe(
                        event,
                        *random.sample(event_names, k=random.randint(0, num_events)),
                        event_callback=self.__class__.dummy_event_callback,
                        once=self.__class__.OneTimeSubscriptionMode.once_value(self.onetime_subscription_mode),
                    )
        elif self.event_subscription_mode == self.__class__.EventSubscriptionMode.ALL:
            for _ in event_names:
                for _ in range(num_subscribers):
                    IsolatedEventLinker.subscribe(
                        *event_names,
                        event_callback=self.__class__.dummy_event_callback,
                        once=self.__class__.OneTimeSubscriptionMode.once_value(self.onetime_subscription_mode),
                    )
        else:
            raise ValueError(f"Invalid event subscription mode: {self.event_subscription_mode}")

        # Subscribe the remaining ones to complete the number of subscriptions.
        for r in range(remaining):
            IsolatedEventLinker.subscribe(
                event_names[r],
                event_callback=self.__class__.dummy_event_callback,
                once=self.__class__.OneTimeSubscriptionMode.once_value(self.onetime_subscription_mode),
            )

        # Create and return the isolated event linker and emitter.
        return IsolatedEventLinker, AsyncIOEventEmitter(event_linker=IsolatedEventLinker)

    def __call__(self) -> Report:
        """
        Run the event emission benchmark for various subscription sizes.

        :return: Benchmark report.
        """
        # Initialize a list to hold benchmark measurements.
        measurements: list[EventEmitterBenchmark.Measurement] = []

        # Record the start time for the benchmark duration
        benchmark_start_time: float = self.timer()

        # Iterate over each subscription size to perform the benchmark.
        for num_subscriptions in tqdm(
            self.subscription_sizes, desc=f"{self.title}", total=len(self.subscription_sizes), colour="GREEN"
        ):
            # List to store median execution times for each repetition.
            medians: list[float] = []

            # Repeat the benchmark for the specified number of times.
            for _ in tqdm(
                range(self.num_repeats), desc="          Repeats", total=self.num_repeats, leave=False, colour="BLUE"
            ):
                # List to track elapsed times for each execution.
                elapsed_times: list[float] = []

                # Execute the event emission multiple times.
                for _ in tqdm(
                    range(self.num_executions), desc="       Executions", total=self.num_executions, leave=False
                ):
                    # Clean up memory before execution.
                    gc.collect()

                    # Disable garbage collection to minimize timing noise.
                    gc.disable()

                    try:
                        # Set up the event linker and emitter for benchmarking.
                        event_linker, event_emitter = self.__setup(num_subscriptions)

                        # Record the start time of the event emission.
                        t0: float = self.timer()

                        # Emit the event to measure execution time.
                        event_emitter.emit("Event0")

                        # Record the end time and calculate elapsed time.
                        t1: float = perf_counter()
                        elapsed_times.append(t1 - t0)

                        # Clear the event linker registry.
                        event_linker.remove_all()
                    finally:
                        # Re-enable the garbage collector.
                        gc.enable()

                        # Force a garbage collection.
                        gc.collect()

                # Sort elapsed times to compute the median.
                elapsed_times.sort()

                # Store the median execution time for this repetition.
                medians.append(median(elapsed_times))

            # Calculate the average of the medians for the current subscription size.
            measurements.append(
                EventEmitterBenchmark.Measurement(
                    num_subscriptions=num_subscriptions,
                    execution_time=mean(medians),
                )
            )

        # Record the end time for the benchmark duration
        benchmark_end_time: float = self.timer()

        # Return a report summarizing the benchmark results.
        return EventEmitterBenchmark.Report(
            title=self.title,
            pyventus_version=self.__class__.PYVENTUS_VERSION,
            benchmark_duration=(benchmark_end_time - benchmark_start_time),
            event_subscription_mode=self.event_subscription_mode.value.capitalize(),
            onetime_subscription_mode=self.onetime_subscription_mode.value.capitalize(),
            subscription_sizes=self.subscription_sizes.copy(),
            num_repeats=self.num_repeats,
            num_executions=self.num_executions,
            measurements=measurements,
        )
