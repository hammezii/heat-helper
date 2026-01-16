# HEAT Helper

[![python - >= 3.10](https://img.shields.io/badge/python->=_3.10-blue?logo=python&logoColor=white)](https://www.python.org/) [![License](https://img.shields.io/badge/License-GPL--3.0-blue)](#license) 

`heat_helper` is a Python utility library designed to streamline the cleaning and preparation of student data for use with the [Higher Education Access Tracker (HEAT)](https://heat.ac.uk). It's available on PyPI here: [https://pypi.org/project/heat_helper/](https://pypi.org/project/heat_helper/)

Preparing CSV or Excel files for HEAT often involves repetitive tasks like cleaning and formatting of names, year groups, and postcodes. This package automates these common data-cleaning tasks to ensure your imports are valid and consistent. It also provides functions to help you match students to your existing HEAT records and get their IDs to support you in reducing duplicate records uploaded to the database and with registering students to activities.

## Features
`heat_helper` provides functions to support many common tasks:

- **Text Cleaning**: simple functions to normalise names (including removing numbers, converting diacritics to plain text, removing punctuation except for hyphens and apostrophes, cleaning extra white spaces, and casing), postcodes, and year groups.
- **Working with Dates**: reverse day/month in a date, calculate a year group from date of birth, or calculate a date of birth range from year group
- **Student Matching**: exact and fuzzy match students from external sources (e.g. registers) to your HEAT Students export to get their ID numbers for activity linking.
- **Data Validation**: check dates of birth are in the right age range for a given year group, or check postcodes are in a UK format.
- **Bulk processing**: get lists of Excel files in folders so you can process lots of files at once.
- **Duplicates**: find potential duplicates in a dataset based on name, date of birth and postcode.
- **Compatibility**: built for use with `pandas` for handling your data.

## What can I use heat_helper for?
Common use cases for `heat_helper` include:

- Cleaning new data to be uploaded to the HEAT database
- Checking if 'new' students already have records in HEAT
- Matching students from your activities to their records on HEAT, so you can use their IDs to bulk register student records to activity records within HEAT

## Installation
You can install `heat_helper` from PyPI or directly from this repository. I recommend [uv](https://docs.astral.sh/uv/) for easy package management.

### with pip
You can install `heat_helper` with `pip` by typing the following into your terminal:

```Bash
pip install heat_helper
```
or from this repo:

```Bash
pip install git+https://github.com/hammezii/heat-helper.git
```

### with uv
If have already initialised a project with uv, you can add `heat_helper` as a dependency:

```Bash
uv add heat_helper
```
or from this repo:

```Bash
uv add git+https://github.com/hammezii/heat-helper.git
```

## Dependencies
`heat_helper` has the following dependencies which will also be installed:

- [`pandas`](https://pandas.pydata.org/) - for DataFrames and dealing with spreadsheet data
- [`rapidfuzz`](https://rapidfuzz.github.io/RapidFuzz/) - for fuzzy matching
- [`openpyxl`](https://openpyxl.readthedocs.io/en/stable/) - for processing Excel files

This means that in a new environment you can simply install `heat_helper` and have a complete setup for processing and manipulating CSV or Excel files.

## Documentation
You can access the documentation **[here](https://hammezii.github.io/heat-helper/)**.

The documentation is a work in progress and will be updated with more examples of how to use `heat_helper`.

## Contributing
You are welcome to contribute to `heat_helper`. Please either submit an issue or a pull request. 
