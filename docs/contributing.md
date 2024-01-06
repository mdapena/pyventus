---
hide:
  - navigation
---

<style>
 .go:before {
  content: "$";
  padding-right: 1.17647em;
 }
</style>

# Contribution Guidelines

<p style='text-align: justify;' markdown>
    Thank you for being interested in contributing to Pyventus! Your involvement is greatly appreciated ❤️
</p>

## Getting Started

<p style='text-align: justify;' markdown>
    &emsp;&emsp;Before creating an issue or pull request, please make sure to check if a similar discussion already
	exists. We encourage you to actively participate by engaging in existing issues.
</p>

## Reporting Issues

<p style='text-align: justify;' markdown>
    &emsp;&emsp;If you have any questions, bug reports, or feature requests, please open a new [issue or discussion](https://github.com/mdapena/pyventus/issues/new/choose). 
	When reporting issues, be sure to provide clear steps to reproduce the problem. For security vulnerabilities, 
	please refer to our [security policy](https://github.com/mdapena/pyventus/security/policy).
</p>

## Submitting Changes

<p style='text-align: justify;' markdown>
	&emsp;&emsp;We greatly appreciate your contributions and want to ensure they align with the project's goals and 
	quality standards. Unless your proposed change is trivial, such as fixing a typo or tweaking documentation, we
	recommend creating an issue or discussion to talk about the proposed change before submitting a pull request. 
	This allows us to provide feedback, clarify requirements, and ensure your efforts are focused in the right 
	direction. To make a contribution, please follow these steps:
</p>

<ol style='text-align: justify;' markdown>

<li markdown>Fork the repository and create a new branch.</li>
<li markdown>Implement your changes in the branch.</li>
<li markdown>Ensure that [formatting, linting, and tests pass](/pyventus/contributing/#pre-submission-testing-and-validation).</li>
<li markdown>Whenever possible, include tests to cover the lines of code you added or modified.</li>
<li markdown>Commit your changes and submit a pull request with a clear, detailed message.</li>

</ol>

<p style='text-align: justify;' markdown>
	&emsp;&emsp;We'll review your pull request to ensure it meets our quality standards before merging it into the main
	codebase. Please feel free to ask any questions along the way!
</p>

### Development Setup

<p style='text-align: justify;' markdown>
	&emsp;&emsp;We recommend developing in a [virtual environment](https://docs.python.org/3/library/venv.html) to 
	isolate project dependencies. To set up your development environment, follow these steps:
</p>

1. Create a virtual environment:

	```console
	python -m venv env
	```

2. Activate the virtual environment:

	=== "Linux, macOS"
	
		```console
		source ./env/bin/activate
		```
	
	=== "Windows PowerShell"
	
		```console
		.\env\Scripts\Activate.ps1
		```
	
	=== "Windows Bash"
	
		```console
		source ./env/Scripts/activate
		```

3. Install development dependencies:

	```console
	pip install -e .[dev]
	```

### Running the Tests

<p style='text-align: justify;' markdown>
	During development, you have two options to run the test suite:
</p>

=== "Manual"

	```console
	pytest -v
	```

=== "Using Hatch"

	```console
	hatch run tests:test
	```

!!! tip "Validating New Event Emitters"

	<p style='text-align: justify;' markdown>
		When implementing new event emitters, it is crucial to ensure their seamless integration with other
		event emitters and the entire package. To achieve this, we kindly request that you utilize the provided test 
		suite specifically designed for testing new event emitters.
	</p>

### Checking Types

<p style='text-align: justify;' markdown>
	You can use the [mypy](https://github.com/python/mypy) tool to check the static typing of your code. Simply run the
	following command:
</p>

=== "Manual"

	```console
	mypy
	```

=== "Using Hatch"

	```console
	hatch run tests:typing
	```

### Code Coverage

<p style='text-align: justify;' markdown>
	To check the code [coverage](https://coverage.readthedocs.io/en/7.3.3/) of your changes, run the following command:
</p>

=== "Manual"

	```console
	coverage run -m pytest -v
	```

=== "Using Hatch"

	```console
	hatch run tests:cov
	```

## Pyventus Documentation

<p style='text-align: justify;' markdown>
	&emsp;&emsp;The documentation for our project is written in Markdown and built using [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/).
	Additionally, the API documentation is generated from the docstrings using [mkdocstrings](https://mkdocstrings.github.io/).
	To begin working on the documentation in a development environment, simply execute the following command:
</p>

```console
hatch run docs:serve
```

## Project Structure and Conventions

<p style='text-align: justify;' markdown>
	&emsp;&emsp;This project follows the [src-layout](https://blog.ionelmc.ro/2014/05/25/python-packaging/) convention
	for Python packages. This convention improves code organization, facilitates easy testing and usage, and allows 
	developers to install the package in [editable mode](https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/#working-in-development-mode).
	By adhering to this convention, we can validate the package thoroughly in a realistic environment, leading to a 
	higher quality and user-friendly product.
</p>

### Code Standards

<p style='text-align: justify;' markdown>
	We strive for a high-quality and maintainable codebase. To achieve this, we have established the following code 
	standards:
</p>

<ul style='text-align: justify;' markdown>

<li markdown>**PEP-8 Compliance** ─ 
Please follow the guidelines outlined in [PEP-8](https://peps.python.org/pep-0008/) for consistent code formatting. 
Adhering to these standards ensures readability and maintainability across our codebase.
</li>

<li markdown>**Black Formatter** ─ 
We recommend using the [Black](https://black.readthedocs.io/en/stable/the_black_code_style/index.html) code formatter
to ensure consistent style and formatting. By automatically enforcing a standard style, the Black formatter saves you
time and effort in manual formatting.
</li>

<li markdown>**Meaningful Naming** ─ 
Use descriptive and meaningful names for variables, functions, and classes. Clear and intuitive naming enhances code 
comprehension, making it easier for everyone to understand and work with the code.
</li>

<li markdown>**Modularity and Reusability** ─ 
Encourage the development of modular and reusable code. Breaking down complex tasks into smaller, self-contained 
components promotes maintainability, reduces complexity, and allows for scalability and extensibility.
</li>

<li markdown>**Optimization and Efficiency** ─ 
Strive for efficient code by considering algorithmic complexity and optimizing where necessary. Writing code that is
both correct and performant ensures responsive and scalable applications.
</li>

</ul>

### Documentation Style

<p style='text-align: justify;' markdown>
	&emsp;&emsp;Clear and comprehensive documentation facilitates collaboration and understanding. When contributing
	to this project, please ensure that you document the following items using properly formatted docstrings:
</p>

* Modules.
* Class definitions.
* Function definitions.
* Module-level variables.

<p style='text-align: justify;' markdown>
	&emsp;&emsp;Pyventus uses [Sphinx](https://www.sphinx-doc.org/en/master/) docstrings formatted according to
	PEP 257 guidelines. For more examples and detailed guidance on using Sphinx-style docstrings, we encourage
	you to consult the official [Sphinx documentation](https://www.sphinx-doc.org/en/master/#user-guides).
</p>

### Pre-Submission Testing and Validation

<p style='text-align: justify;' markdown>
	&emsp;&emsp;Before submitting your pull request, it is crucial to ensure that your changes pass all the necessary
	checks. To do so, simply run the following command:
</p>

```console
hatch run tests:all
```

<p style='text-align: justify;' markdown>
	&emsp;&emsp;The above command will trigger the Hatch project manager to initiate the comprehensive testing process
	across all supported Python versions. It will run tests, perform typing checks, ensure code formatting, and measure
	code coverage. This ensures that your changes meet the required quality standards.
</p>

!!! info "Testing for Individual Python Versions"

	<p style='text-align: justify;' markdown>
		If you want to test for specific Python versions, you can do so by specifying the desired versions in the 
		command, as follows:
	</p>

	=== "Python 3.10"

		```console
		hatch run +py=3.10 tests:all
		```

	=== "Python 3.11"

		```console
		hatch run +py=3.11 tests:all
		```

	=== "Python 3.12"

		```console
		hatch run +py=3.12 tests:all
		```

!!! warning "Troubleshooting Hatch Environment Errors"

	<p style='text-align: justify;' markdown>
		If commands run successfully when executed manually but produce unexpected errors or misbehavior when run 
		within a Hatch environment, even though the dependencies are declared correctly, this could indicate an 
		issue with the Hatch environment cache. To resolve potential cache-related issues, you can remove the 
		environment and clear its cache by running:
	</p>

	```console
	hatch env remove [ENV_NAME]
	```
	
	<p style='text-align: justify;' markdown>
		Alternatively, you can remove all environments and their cache by running the following command:
	</p>

	```console
	hatch env prune
	```

## Code of Conduct

<p style='text-align: justify;' markdown>
	&emsp;&emsp;This project and everyone participating in it is governed by the [Pyventus Code of Conduct](https://github.com/mdapena/pyventus/blob/master/.github/CODE_OF_CONDUCT.md). 
	By participating, you are expected to uphold this code. Please report unacceptable behavior.
</p>

## Thanks in Advance!

<p style='text-align: justify;' markdown>
	&emsp;&emsp;Thank you for considering contributing to this project. Your contributions are valuable 
	and greatly appreciated. If you have any questions or need further clarification, please don't 
	hesitate to reach out. We look forward to collaborating with you to enhance this project!
</p>

<br>
