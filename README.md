# HEAT Helper

[![python - >= 3.13](https://img.shields.io/badge/python->=_3.13-blue?logo=python&logoColor=white)](https://www.python.org/) [![License](https://img.shields.io/badge/License-GPL--3.0-blue)](#license) 

`heat-helper` is a Python utility library designed to streamline the cleaning and preparation of student data for use with the [Higher Education Access Tracker (HEAT)](https://heat.ac.uk).

Preparing CSV or Excel files for HEAT often involves repetitive tasks like cleaning and formatting of names, year groups, and postcodes. This package automates these common data-cleaning tasks to ensure your imports are valid and consistent. It also provides functions to help you match students to your existing HEAT records and get their IDs to support you in reducing duplicate records uploaded to the database and with registering students to activities.

## Features
`heat_helper` provides functions to support many common tasks:

- Cleaning and normalising student names including removing numbers, converting diacritics, cleaning extra whitespaces, and casing.
- Date related functions including reversing day/month, calculating a year group from date of birth, and calculating a date of birth range from year group
- Year group normalisation and cleaning to a standard format 'Year X'
- Postcode normalisation and format validation
- Student matching from one dataset to your HEAT data, including exact matches on multiple columns (e.g. name, date of birth, and postcode), fuzzy name matching where other variables match (i.e. where date of birth and postcode match).

Common use cases for `heat_helper` include:

- Cleaning new data to be uploaded to the HEAT database
- Checking if 'new' students already have records in HEAT
- Bulk matching students from your activities to their records on HEAT, so you can use their IDs to bulk register student records to activity records within HEAT

## Installation
You can install `heat_helper` from GitHub. I recommend [uv](https://docs.astral.sh/uv/) for easy package management.

### with pip
You can install `heat_helper` with `pip` by typing the following into your terminal:

```Bash
pip install git+https://github.com/hammezii/heat-helper.git
```

### with uv
If have already initialised a project with uv, you can add `heat_helper` as a dependency:

```Bash
uv add git+https://github.com/hammezii/heat-helper.git
```

## Dependencies
`heat_helper` assumes that if you're using python to process your HEAT data you probably already have common data packages like `pandas` installed. The following are required:

- pandas >= 2.3.3

## Documentation
You can access the documentation here: []().

The doumentation is frequently updated with more examples of how to use heat_helper.

## Contributing
You are welcome to contribute to `heat_helper`. Please either submit an issue or a pull request. 