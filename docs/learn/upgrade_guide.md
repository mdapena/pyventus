<style>
    .text-section{
        p {
            text-align: justify;

            &:before {
                content: '';
                display: inline-block;
                width: 1.5rem;
            }
        }

        li {
            text-align: justify;
        }

        .task-list-control {
            input {
                cursor: pointer !important;
                z-index: 1 !important;
            }
        }
    }

    .terminal-command {
        .go:before {
            content: "$";
            padding-right: 1.17647em;
        }
    }
</style>

<div class="text-section" markdown>

# Upgrade Guide

Welcome to the Upgrade Guide for Pyventus `v0.7`! In this section, you will learn how to properly upgrade your application from Pyventus `v0.6` to `v0.7`, as well as address any potential issues related to breaking changes, ensuring a smooth transition to the latest version.

## Upgrading to the Latest Version

Pyventus is published as a <a href="https://pypi.org/project/pyventus/" target="_blank">Python package</a> and can be easily upgraded with `pip`. To get started, open up a terminal and upgrade Pyventus with the following command:

<div class="terminal-command">
```console
pip install -U pyventus
```
</div>

## Reviewing Key Breaking Changes

Please review the following breaking changes and apply the necessary actions to effectively update your application. You can mark each item as complete to track your progress.

-   [ ] All previous event-driven features must now be imported from the new inner package `pyventus.events` instead of directly from `pyventus` or its submodules.
-   [ ] The inheritance structure of the `EventEmitter` has been replaced with composition using the `ProcessingService`. Custom event emitters must now be implemented through the `ProcessingService` interface and composed with the `EventEmitter` class.
-   [ ] The `EventLinker` has experienced some method renames and return type modifications to align with the new redesigned codebase:
    -   [ ] `remove_event_handler()` → `remove_subscriber()`.
    -   [ ] `get_event_handlers()` → `get_subscribers()`: Now returns a `set` instead of a `list`.
    -   [ ] `get_events_by_event_handler()` → `get_events_from_subscribers()`: Now returns a `set` instead of a `list` and supports retrieving events for multiple subscribers.
    -   [ ] `get_event_handlers_by_events()` → `get_subscribers_from_events()`: Now returns a `set` instead of a `list` and includes a new flag `pop_onetime_subscribers`.
    -   [ ] `unsubscribe()` → `remove()`: Now removes one event from a subscriber at a time.
    -   [ ] Parameters named `event_handler` have been renamed to `subscriber` in all methods.
    -   [ ] `get_events()`: Now returns a `set` instead of a `list` with non-duplicates.
-   [ ] The `RQEventEmitter` has been renamed to `RedisEventEmitter`.
-   [ ] The `CeleryEventEmitter.Queue` has been removed, and the `CeleryEventEmitter` now requires a `Celery` instance. Security aspects have been delegated to the `Celery` app.
-   [ ] Dependency injection for the `FastAPIEventEmitter` through FastAPI's `Depends()` function has been simplified; use `Depends(FastAPIEventEmitter())` for all scenarios.
-   [ ] The `ExecutorEventEmitter` can no longer be used as a context manager; for this purpose, use the new `ExecutorEventEmitterCtx`.

## Questions and Issues

If you have any questions or run into issues during the upgrade process, please feel free to open a <a href="https://github.com/mdapena/pyventus/issues/new/choose" target="_blank">new issue or start a discussion</a>. Before doing so, it is recommended to check for existing inquiries to avoid duplicates.

</div>
