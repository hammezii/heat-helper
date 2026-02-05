# What is HEAT Helper?
[![python - >= 3.10](https://img.shields.io/badge/python->=_3.10-blue?logo=python&logoColor=white)](https://www.python.org/) [![License](https://img.shields.io/badge/License-GPL--3.0-green)](https://github.com/hammezii/heat-helper/blob/main/LICENSE) ![PyPI - Version](https://img.shields.io/pypi/v/heat_helper)

`heat-helper` is a Python utility library designed to streamline the cleaning and preparation of student data for use with the [Higher Education Access Tracker (HEAT)](https://heat.ac.uk).

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

## Built by
`heat_helper` was created by Hannah Merry at Higher Horizons Uni Connect and is free for anyone to use. It is open source, and you can find the code on [Github](https://github.com/hammezii/heat-helper).

This documentation was built with [material for mkdocs](https://squidfunk.github.io/mkdocs-material/) and [mkdocstrings](https://mkdocstrings.github.io/).
