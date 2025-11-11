---
hide:
    - navigation
---

<style>
    .terminal-command {
        .go:before {
            content: "$";
            padding-right: 1.17647em;
        }
    }
</style>

# Contribution Guidelines

<p style="text-align: justify;">
    &emsp;&emsp;Thank you for being interested in contributing to Pyventus! In this section, you will discover how to effectively contribute to this project, as well as best practices for reporting issues, submitting pull requests, and engaging with the community ❤️
</p>

## Getting Started

<p style="text-align: justify;" markdown>
    &emsp;&emsp;Before creating an issue or pull request, please make sure to check if a similar discussion already exists. We encourage you to actively participate by engaging in existing issues.
</p>

## Reporting Issues

<p style="text-align: justify;">
    &emsp;&emsp;If you have any questions, bug reports, or feature requests, please open a new <a href="https://github.com/mdapena/pyventus/issues/new/choose" target="_blank">issue or discussion</a>. When reporting issues, be sure to provide clear steps to reproduce the problem. For security vulnerabilities, please refer to the <a href="https://github.com/mdapena/pyventus/security/policy" target="_blank">Pyventus Security Policy</a>.
</p>

## Submitting Changes

<p style="text-align: justify;">
	&emsp;&emsp;We greatly appreciate your contributions and want to ensure they align with the project's goals and quality standards. Unless your proposed change is trivial, such as fixing a typo or tweaking documentation, we recommend creating an issue or discussion to talk about the proposed change before submitting a pull request. This allows us to provide feedback, clarify requirements, and ensure your efforts are focused in the right direction. To make a contribution, please follow these steps:
</p>

1.  <p style="text-align: justify;">Fork the repository and create a new branch.</p>
2.  <p style="text-align: justify;">Implement your changes in the new branch.</p>
3.  <p style="text-align: justify;" markdown>Ensure that [formatting, linting, and tests pass](#pre-submission-testing-and-validation).</p>
4.  <p style="text-align: justify;">Include tests whenever possible to cover the lines of code you added or modified.</p>
5.  <p style="text-align: justify;">Commit your changes and submit a pull request with a clear, detailed message.</p>

<p style="text-align: justify;">
	&emsp;&emsp;We will review your pull request to ensure it meets the project's quality standards before merging it into the main codebase. Please feel free to ask any questions along the way!
</p>

### Development Setup

<p style="text-align: justify;" markdown>
	&emsp;&emsp;To ensure that project dependencies are isolated and do not interfere with other projects, we recommend using a <a href="https://docs.python.org/3/library/venv.html" target="_blank_">virtual environment</a> for development. To set up a new virtual environment, please follow these steps:
</p>

1.  Create a new virtual environment with:<div class="terminal-command">

    ```console
    python -m venv venv
    ```

    </div>

2.  Activate the environment with:

    === ":material-apple: macOS"

        <div class="terminal-command">
        ```console
        . venv/bin/activate
        ```
        </div>

    === ":fontawesome-brands-windows: Windows"

        <div class="terminal-command">
        ```console
        . venv/Scripts/activate
        ```
        </div>

    === ":material-linux: Linux"

        <div class="terminal-command">
        ```console
        . venv/bin/activate
        ```
        </div>

3.  Install development dependencies with:<div class="terminal-command">

    ```console
    pip install -e .[dev]
    ```

    </div>

### Running Tests

<p style="text-align: justify;">
	&emsp;&emsp;To run the test suite of Pyventus, you can either perform a manual execution with <a href="https://docs.pytest.org/en/stable/" target="_blank">pytest</a> or use <a href="https://hatch.pypa.io/latest/" target="_blank">Hatch</a> to run the test suite across all supported Python versions.
</p>

=== ":material-console: Manual"

    <div class="terminal-command">
    ```console
    pytest -v
    ```
    </div>

=== ":material-package-variant-plus: Using Hatch"

    <div class="terminal-command">
    ```console
    hatch run tests:test
    ```
    </div>

### Code Coverage

<p style="text-align: justify;" markdown>
	&emsp;&emsp;To evaluate the test coverage of your code, you can either perform a manual evaluation with <a href="https://coverage.readthedocs.io/en/7.3.3/" target="_blank">Coverage.py</a> or use <a href="https://hatch.pypa.io/latest/" target="_blank">Hatch</a> to evaluate test coverage across all supported Python versions.
</p>

=== ":material-console: Manual"

    <div class="terminal-command">
    ```console
    coverage run -m pytest -v
    ```
    </div>

=== ":material-package-variant-plus: Using Hatch"

    <div class="terminal-command">
    ```console
    hatch run tests:cov
    ```
    </div>

### Checking Types

<p style="text-align: justify;">
	&emsp;&emsp;To check the static typing of your code, you can either perform a manual check with <a href="https://www.mypy-lang.org/" target="_blank">mypy</a> or use <a href="https://hatch.pypa.io/latest/" target="_blank">Hatch</a> to check static typing across all supported Python versions.
</p>

=== ":material-console: Manual"

    <div class="terminal-command">
    ```console
    mypy
    ```
    </div>

=== ":material-package-variant-plus: Using Hatch"

    <div class="terminal-command">
    ```console
    hatch run tests:typing
    ```
    </div>

### Linting and Formatting

<p style="text-align: justify;">
	&emsp;&emsp;To check the linting and formatting of your code, you can either manually use <a href="https://docs.astral.sh/ruff/" target="_blank">Ruff</a> or use <a href="https://hatch.pypa.io/latest/" target="_blank">Hatch</a> to perform these checks across all supported Python versions.
</p>

=== ":material-console: Manual"

    <div class="terminal-command">
    ```console
    ruff check & ruff format --check
    ```
    </div>

=== ":material-package-variant-plus: Using Hatch"

    <div class="terminal-command">
    ```console
    hatch run tests:style
    ```
    </div>

## Pyventus Documentation

<p style="text-align: justify;">
	&emsp;&emsp;The Pyventus documentation is written in Markdown and built with <a href="https://squidfunk.github.io/mkdocs-material/" target="_blank">Material for MkDocs</a>. To get started in development mode, run one of the following commands:
</p>

=== ":material-console: Manual"

    <div class="terminal-command">
    ```console
    mkdocs serve --dev-addr localhost:8000
    ```
    </div>

=== ":material-package-variant-plus: Using Hatch"

    <div class="terminal-command">
    ```console
    hatch run docs:serve
    ```
    </div>

## Project Structure and Conventions

<p style="text-align: justify;">
	&emsp;&emsp;This project follows the <a href="https://blog.ionelmc.ro/2014/05/25/python-packaging/" target="_blank">src-layout</a> convention for Python packages. This convention improves code organization, facilitates easy testing and usage, and allows developers to install the package in <a href="https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/#working-in-development-mode" target="_blank">editable mode</a>. By adhering to this convention, we can validate the package thoroughly in a realistic environment, leading to a higher quality and user-friendly product.
</p>

### Code Standards

<p style="text-align: justify;">
	&emsp;&emsp;At Pyventus, ensuring a high-quality and maintainable codebase is essential. Therefore, the following code standards have been established to guide the development process as well as promote consistency:
</p>

-   <p style="text-align: justify;"><b>PEP-8 Compliance</b> ─ 
    	Follow the guidelines outlined in <a href="https://peps.python.org/pep-0008/" target="_blank">PEP-8</a> to ensure clean and readable Python code. Adhering to these standards promotes consistency, enhances code comprehension, and facilitates collaboration among contributors.
    </p>

-   <p style="text-align: justify;"><b>Meaningful Naming</b> ─ 
    	Use descriptive and meaningful names for variables, functions, and classes. Clear and intuitive naming enhances code comprehension, making it easier for everyone to understand and work with the code.
    </p>

-   <p style="text-align: justify;"><b>Modularity and Reusability</b> ─ 
    	Encourage the development of modular and reusable code. Breaking down complex tasks into smaller, self-contained components promotes maintainability, reduces complexity, and allows for scalability and extensibility.
    </p>

-   <p style="text-align: justify;"><b>Optimization and Efficiency</b> ─ 
    	Strive for efficient code by considering algorithmic complexity and optimizing where necessary. Writing code that is both correct and performant ensures responsive and scalable applications.
    </p>

-   <p style="text-align: justify;" class="annotate" markdown><b>Class Structure</b> ─ 
    	While there are no strict rules for structuring classes in Python beyond common sense and readability, Pyventus has established a recommended class structure that provides a foundation for a consistent codebase.(1)
    </p>

    1.  <h2 style="margin-top: 0;">Recommended Class Structure</h2>

        ```sh
        Class Name

        1. Inner Classes and Class Attributes
           └── Access Modifiers: private, protected, public

        2. Static Methods
           ├── @staticmethod
           └── Access Modifiers: private, protected, public

        3. Class Methods
           ├── @classmethod
           └── Access Modifiers: private, protected, public

        4. Special Attributes
           ├── __slots__, __init__, __repr__

        5. Properties
           ├── @property
           └── Access Modifiers: private, protected, public

        6. Abstract Methods
           ├── @abstractmethod
           └── Access Modifiers: private, protected, public

        7. Instance Methods
           └── Access Modifiers: private, protected, public

        8. Other Magic Methods

        ```

### Documentation Style

<p style="text-align: justify;">
	&emsp;&emsp;When contributing to Pyventus, please make sure that all code is well documented. The following should be documented using properly formatted docstrings:
</p>

-   Modules.
-   Class definitions.
-   Function definitions.
-   Module-level variables.

<p style="text-align: justify;">
	&emsp;&emsp;Pyventus uses <a href="https://www.sphinx-doc.org/en/master/" target="_blank">Sphinx docstrings</a> formatted according to <a href="https://peps.python.org/pep-0257/" target="_blank">PEP 257</a> guidelines. For more examples and detailed guidance on using Sphinx-style docstrings, please refer to the official <a href="https://www.sphinx-doc.org/en/master/#user-guides" target="_blank">Sphinx documentation</a>.
</p>

### Pre-Submission Testing and Validation

<p style="text-align: justify;">
	&emsp;&emsp;Before submitting your pull request, it is crucial to ensure that your changes pass all necessary checks. To do so, simply run the following command:
</p>

<div class="terminal-command">
```console
hatch run tests:all
```
</div>

<p style="text-align: justify;">
	&emsp;&emsp;This command will trigger the Hatch project manager to initiate a comprehensive testing process across all supported Python versions. It will run tests, perform type checks, ensure code linting and formatting, and measure code coverage. This ensures that your changes meet the required quality standards.
</p>

!!! info "Testing for Specific Python Versions"

    === ":material-language-python: Python 3.10"

    	<div class="terminal-command">
    	```console
    	hatch run +py=3.10 tests:all
    	```
    	</div>

    === ":material-language-python: Python 3.11"

    	<div class="terminal-command">
    	```console
    	hatch run +py=3.11 tests:all
    	```
    	</div>

    === ":material-language-python: Python 3.12"

    	<div class="terminal-command">
    	```console
    	hatch run +py=3.12 tests:all
    	```
    	</div>

    === ":material-language-python: Python 3.13"

    	<div class="terminal-command">
    	```console
    	hatch run +py=3.13 tests:all
    	```
    	</div>

    === ":material-language-python: Python 3.14"

    	<div class="terminal-command">
    	```console
    	hatch run +py=3.14 tests:all
    	```
    	</div>

!!! warning "Troubleshooting Hatch Environment Errors"

    <p style="text-align: justify;">
    	&emsp;&emsp;If commands run successfully when executed manually but produce unexpected errors or misbehavior when run within a Hatch environment, even though the dependencies are declared correctly, this could indicate an issue with the Hatch environment cache. To resolve potential cache-related issues, you can remove the environment and clear its cache by running:
    </p>

    <div class="terminal-command">
    ```console
    hatch env remove [ENV_NAME]
    ```
    </div>

    <p style='text-align: justify;'>
    	&emsp;&emsp;Alternatively, if you prefer to take a more comprehensive approach by removing all environments and clearing their caches, you can do so by running the following command:
    </p>

    <div class="terminal-command">
    ```console
    hatch env prune
    ```
    </div>

## Code of Conduct

<p style="text-align: justify;">
	&emsp;&emsp;This project is committed to fostering a welcoming and inclusive environment for all participants. The <a href="https://github.com/mdapena/pyventus/blob/master/.github/CODE_OF_CONDUCT.md" target="_blank">Pyventus Code of Conduct</a> applies to this project and everyone involved in it. By participating, you agree to uphold these standards and contribute to a positive experience for everyone.
</p>

<p style="text-align: justify;">
	&emsp;&emsp;If you witness or experience any unacceptable behavior, we encourage you to report it to the project maintainers. Your feedback is important in helping us maintain a respectful community.
</p>
