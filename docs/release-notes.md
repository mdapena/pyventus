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

- Optimized the size of the source distribution (sdist) build by including only essential files and directories, such
  as the `/src` and `/tests` directories, as well as the following files: `.gitignore`, `pyproject.toml`,
  `CITATION.cff`, `README`, and `LICENSE`.
- Refactored documentation dependencies into an optional dependency called `docs`.
- Updated the `deploy-docs.yml` GitHub workflow to leverage the new optional dependency `docs`.
- Updated the `EventEmission` class with the `@final` decorator from the typing module, indicating that it is meant for
  internal use only and should not be subclassed.

##### Fixed

- Addressed minor errors and details in the documentation.

[//]: # (--------------------------------------------------------------------------------------------------------------)

## [v0.4.0](https://github.com/mdapena/pyventus/releases/tag/0.4.0) <small>January 6, 2024</small> { id="0.4.0" }

<hr class="divider">

##### Added

- Added `FastAPIEventEmitter` implementation to facilitate seamless integration with the `FastAPI` framework.
- Added tests for `FastAPIEventEmitter` to validate its behavior and ensure proper operation.
- Added documentation for `FastAPIEventEmitter`, including tutorials and API references.
- Integrated the `Coveralls.io` workflow to generate coverage badge and reports.
- Included coverage badges on the main documentation page and the readme file.
- Introduced permalinks within the documentation for easy navigation.

##### Changed

- Updated `pyproject.toml` with the new optional dependency for `FastAPI` integration.

##### Fixed

- Addressed minor errors in the Pyventus documentation to improve accuracy and clarity.

[//]: # (--------------------------------------------------------------------------------------------------------------)

## [v0.3.0](https://github.com/mdapena/pyventus/releases/tag/0.3.0) <small>December 29, 2023</small> { id="0.3.0" }

<hr class="divider">

##### Breaking Changes

- Introduced `EventEmission` object to encapsulate the processing of event emissions. This changes the `_execute()`
  method of `EventEmitter` but provides a cleaner, more scalable, and efficient approach.
- Renamed all debug flags from `debug_mode` to `debug` for enhanced clarity and consistency.
- Renamed EventEmitter's `_execute()` method to `_process()` to better reflect its purpose of processing event
  emissions.

##### Added

- Added `CeleryEventEmitter` implementation to leverage the Celery distributed task queue for event handling.
- Added tests for `CeleryEventEmitter` to validate its behavior and ensure proper operation.
- Added documentation for `CeleryEventEmitter`, including tutorials and API references.

##### Changed

- Restructured the documentation for event emitters tutorials and API references to improve organization and clarity.
- Updated the `contributing.md` page to include the *Troubleshooting Hatch Environment Errors* section.
- Updated the `EventEmitter` API documentation to include the `EventEmission` class reference.
- Updated `pyproject.toml` with the new optional dependency for `Celery` integration.
- Updated `mypy` ignore flags to properly silence specific false positive error codes.

##### Fixed

- Addressed minor errors in the Pyventus documentation.

[//]: # (--------------------------------------------------------------------------------------------------------------)

## [v0.2.1](https://github.com/mdapena/pyventus/releases/tag/0.2.1) <small>December 17, 2023</small> { id="0.2.1" }

<hr class="divider">

##### Changed

- Updated docstring links throughout the package to refer to the official documentation.
- Updated the `RQEventEmitter` API Reference and Tutorials docs to reflect the new optional import.

##### Fixed

- Resolved the issue where the `RQEventEmitter` class was automatically imported in the main package, requiring the
  installation of its optional dependency to use any of the package's core functionalities. It is now fully optional.
- Fixed issues with invalid links in the documentation.

[//]: # (--------------------------------------------------------------------------------------------------------------)

## [v0.2.0](https://github.com/mdapena/pyventus/releases/tag/0.2.0) <small>December 16, 2023</small> { id="0.2.0" }

<hr class="divider">

##### Added

- Introduced the `publish to PyPI` workflow, automating the uploading of package builds when new releases are created.
- Added the `mkdocs-git-authors` plugin to display git authors of a markdown page in the documentation.
- Added badges to the main page of the documentation as well as the readme file.
- Added a code of conduct for the project, using
  the [Contributor Covenant v2.1](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).
- Included a `CITATION.cff` file to facilitate academic citations.

##### Changed

- Renamed the `tests.yml` workflow to `run-tests.yml`.
- Updated the `deploy-docs.yml` workflow with the `mkdocs-git-authors` plugin dependency.
- Modified the `mkdocs.yml` config file by adding the `site_url` and `site_author` properties.
- Updated the `pyproject.toml` file with the `mkdocs-git-authors` plugin dependency and python package keywords.

##### Fixed

- Fixed the python version in the `deploy-docs.yml` workflow.
- Resolved issues with relative links in the documentation.

[//]: # (--------------------------------------------------------------------------------------------------------------)

## [v0.1.0](https://github.com/mdapena/pyventus/releases/tag/0.1.0) <small>December 15, 2023</small> { id="0.1.0" }

<hr class="divider">

##### Initial Implementation

&emsp;&emsp;This release introduces Pyventus v0.1.0, a modern and robust Python package for event-driven programming.
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
