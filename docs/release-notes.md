---
hide:
  - navigation
---

<style>
	.divider {
		margin-top: -0.5em !important;
		margin-bottom: -0.2em !important;
	}
</style>

[//]: # (--------------------------------------------------------------------------------------------------------------)

## [v0.4.1](https://github.com/mdapena/pyventus/releases/tag/0.4.1) <small>January 30, 2024</small> { id="0.4.1" }

<hr class="divider">

##### Changed

- Optimized the size of the `sdist` build by including only essential files and directories, such as `/src`, `/tests`,
  `.gitignore`, `pyproject.toml`, `CITATION.cff`, `README.md` and `LICENSE`.
- Refactored the dependencies of the docs environment by separating them into an optional dependency called `docs`.
- Updated the `deploy-docs.yml` GitHub workflow to utilize the new `docs` optional dependency.
- Updated the `EventEmission` class with the `@final` decorator from the typing module, indicating that it is meant for
  internal use only and should not be subclassed.

##### Fixed

- Addressed minor errors and fixed broken links in the documentation.

[//]: # (--------------------------------------------------------------------------------------------------------------)

## [v0.4.0](https://github.com/mdapena/pyventus/releases/tag/0.4.0) <small>January 6, 2024</small> { id="0.4.0" }

<hr class="divider">

##### Added

- The `FastAPIEventEmitter` has been added to facilitate seamless integration with `FastAPI` framework and leverage its
  `BackgroundTasks` for event handling.
- Added comprehensive documentation for `FastAPIEventEmitter`, including tutorials and API references.
- A `Coveralls.io` workflow has been added to generate a coverage badge and reports.
- Included permalinks for easy navigation within the documentation.

##### Fixed

- Addressed minor errors in the Pyventus documentation.

[//]: # (--------------------------------------------------------------------------------------------------------------)

## [v0.3.0](https://github.com/mdapena/pyventus/releases/tag/0.3.0) <small>December 29, 2023</small> { id="0.3.0" }

<hr class="divider">

##### Added

- Added `CeleryEventEmitter` implementation to leverage the Celery distributed task queue for event handling.
- Included documentation for `CeleryEventEmitter` including tutorials and API references.

##### Changed

- Restructured documentation for event emitters tutorials and API references.
- Restructured tests for event emitters tutorials and API references.

##### Breaking Changes

- Introduced `EventEmission` object to encapsulate the processing of event emissions. This changes the `_execute()`
  method of EventEmitter but provides a cleaner, more scalable, and efficient approach.
- Renamed EventEmitter's `_execute()` method to `_process()` to better reflect its purpose of processing event
  emissions.
- Renamed all debug flags from `debug_mode` to `debug` for enhanced clarity and consistency.

[//]: # (--------------------------------------------------------------------------------------------------------------)

## [v0.2.1](https://github.com/mdapena/pyventus/releases/tag/0.2.1) <small>December 17, 2023</small> { id="0.2.1" }

<hr class="divider">

##### Fixed

- Fixed issues with invalid links in the documentation.
- Updated docstring links to the official Pyventus documentation.
- Resolved the issue where the `RQEventEmitter` optional dependency had to be installed by default to use the package.
  It is now fully optional.

[//]: # (--------------------------------------------------------------------------------------------------------------)

## [v0.2.0](https://github.com/mdapena/pyventus/releases/tag/0.2.0) <small>December 16, 2023</small> { id="0.2.0" }

<hr class="divider">

##### Added

- This release introduces the `publish to PyPI` workflow, automating the uploading of package builds
  when new releases are created.

##### Changed

- Badges have been added to the main page of the documentation as well as the readme file.
- To facilitate academic citations, a `CITATION.cff` file has been added in this release.
- A code of conduct has been added to the project using
  the [Contributor Covenant v2.1](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).
- The `mkdocs.yml` file has been updated to include the `git-authors` plugin, which lists the names of documentation
  contributors on their respective pages.

##### Fixed

- Minor bug fixes and refactoring have been made in the `deploy-docs` and `run-tests` workflows.
- Fixed issues with relative links in the documentation.

[//]: # (--------------------------------------------------------------------------------------------------------------)

## [v0.1.0](https://github.com/mdapena/pyventus/releases/tag/0.1.0) <small>December 15, 2023</small> { id="0.1.0" }

<hr class="divider">

##### Initial Implementation

&emsp;&emsp;This release introduces Pyventus 0.1.0, a modern and robust Python package for event-driven programming.
Pyventus provides developers with a comprehensive suite of tools and utilities to define, emit, and orchestrate events.
It empowers developers to build scalable, extensible, and loosely-coupled event-driven applications.

- **Implementation Details:** The first implementation includes all the core functionalities of the package,
  encompassing events, event linkers, event emitters, event handlers, and more.
- **Testing and Coverage:** This release includes a test suite that verifies the correctness of the package
  implementation. It also integrates code coverage, achieving 100% test coverage. The tests are configured to run
  automatically via GitHub Actions on both push and pull requests to the master branch.
- **Formatter and Lint Configuration:** A formatter and lint configuration have been added to the project. This ensures
  consistent code style, maintainability, and adherence to the established coding standards defined in the project
  documentation.
- **Documentation:** Additionally, this release includes comprehensive documentation for the package. The documentation
  covers the main page, a detailed getting started guide, tutorials, API reference, and release notes.

[//]: # (--------------------------------------------------------------------------------------------------------------)

<br>
