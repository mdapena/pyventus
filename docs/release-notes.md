---
hide:
  - navigation
---

[//]: # (--------------------------------------------------------------------------------------------------------------)

## v0.2.0

### What's Changed

- **GitHub Actions:** This release introduces the "publish to PyPI" workflow, automating the uploading of package builds
  when new releases are created. Additionally, it includes minor bug fixes and refactoring in the "deploy-docs" and "
  run-tests" workflows.
- **Academic Citations:** To facilitate academic citations, a CITATION.cff file has been added in this release.
- **Code of conduct:** A code of conduct has been added to the project using
  the [Contributor Covenant v2.1](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).
- **Project Badges:** Badges have been added to the main page of the documentation as well as the readme file.
- **git-authors mkdocs material:** The mkdocs.yml file has been updated to include the "git-authors" plugin, which lists
  the names of documentation contributors on their respective pages.
- **Documentation Improvements:** Fixed issues with relative links in the documentation.

[//]: # (--------------------------------------------------------------------------------------------------------------)

## v0.1.0

### What's Changed

- **Initial implementation of Pyventus by [@mdapena](https://github.com/mdapena)
  in [#2](https://github.com/mdapena/pyventus/pull/2):** This release
  introduces Pyventus 0.1.0, a modern and robust Python package for event-driven programming. Pyventus provides
  developers with a comprehensive suite of tools and utilities to define, emit, and orchestrate events. It empowers
  developers to build scalable, extensible, and loosely-coupled event-driven applications.
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
