# Validation
These functions are used with the optional `pydantic` dependency to validate your data and generate error reports.

!!! Info
    To install `heat_helper` with the optional `pydantic` dependency use:

    ```Bash

    pip install heat_helper[validation]

    ```

## Create Error Report
This function allows you to validate a DataFrame against a `pydantic` [Model](https://docs.pydantic.dev/latest/concepts/models/) and returns the DataFrame with information about the number and type of errors found per row. It will return any 'extra' data passed to the Model (usually columns in the DataFrame which do not correspond to a field in the Model and so are not validated) in the DataFrame, but obviously these columns won't have been validated. Pydantic by default usually removes any extra data passed to a Model, so this behaviour is different to the standard but has been included as it is less destructive. 

=== "Example: Activity Register"

    ```Python
    import heat_helper as hh 
    import pandas as pd 
    from pydantic import BaseModel, Field
    from datetime import date
    from typing import Literal

    # DEFINE YOUR PYDANTIC VALIDATION MODEL. 
    # This is a Validation Model for activity registers.
    class Register(BaseModel):
        first_name: str
        last_name: str
        date_of_birth: date = Field(le=date(2014,8,31))
        postcode: str = Field(min_length=6, max_length=8)
        year_group: Literal['Year 7', 'Year 8', 'Year 9', 
                            'Year 10', 'Year 11', 
                            'Year 12', 'Year 13']
        school: str
        attended: Literal['Y', 'N']

    # LOAD DATA AND CREATE ERROR REPORT
    register = pd.read_csv('register.csv')

    error_report = create_error_report(register, Register, 'register')

    print(error_report.head(15))  

    # RETURNED DATAFRAME - VALIDATION COLUMNS 
    # (Note: original data ommitted but would also be returned.)
    #
    # Validated 14 rows in register. 4 rows have 4 total errors.
    #    val_error_count                                  val_error_details validation_status
    #0                 0                                               None             Valid
    #1                 0                                               None           Invalid
    #2                 1      'date_of_birth': Input should be a valid date           Invalid
    #4                 0                                               None             Valid
    #3                 0                                               None             Valid
    #5                 1  'postcode': String should have at least 6 char...           Invalid
    #6                 1           'school': Input should be a valid string           Invalid
    #7                 0                                               None             Valid
    #8                 0                                               None             Valid
    #9                 0                                               None             Valid
    #10                0                                               None             Valid
    #11                0                                               None             Valid
    #12                1         'postcode': Input should be a valid string           Invalid

    ```
