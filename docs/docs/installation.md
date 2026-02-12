# Installation
There are a few different options to install `heat_helper`. I recommend [uv](https://docs.astral.sh/uv/) for easy package and project management. You can also install `heat_helper` with pip.

To install `heat_helper` type either of the following into your terminal:

=== "pip"

    ```Bash
    pip install heat_helper
    ```

=== "uv"

    ```Bash
    uv add heat_helper
    ```

## Dependencies
`heat_helper` has the following dependencies which will also be installed:

- [`pandas`](https://pandas.pydata.org/) - for DataFrames and dealing with spreadsheet data
- [`rapidfuzz`](https://rapidfuzz.github.io/RapidFuzz/) - for fuzzy matching
- [`openpyxl`](https://openpyxl.readthedocs.io/en/stable/) - for processing Excel files

This means that in a new environment you can simply install `heat_helper` and have a complete setup for processing and manipulating CSV or Excel files.

## Optional Dependencies
`heat_helper` has the following optional dependencies:

- [`pydantic`](https://docs.pydantic.dev/latest/) - for data validation. If installed, you gain access to [validation functions](validation.md).

To install `pydantic` use:

=== "pip"

    ```Bash
    pip install heat_helper[validation]
    ```

=== "uv"

    ```Bash
    uv add heat_helper[validation]
    ```

## Install from respository
If you have [git](https://git-scm.com/) installed on your system you can also install `heat_helper` directly from the GitHub repository:

=== "pip"

    ```Bash
    pip install git+https://github.com/hammezii/heat-helper.git
    ```

=== "uv"

    ```Bash
    uv add git+https://github.com/hammezii/heat-helper.git
    ```


