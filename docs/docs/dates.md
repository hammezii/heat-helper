# Dates
These functions are designed for use on dates (usually dates of birth).

## Reverse Dates
This function can be used to 'reverse' the day and month in a date. This can be useful if Excel has incorrectly formatted a date and it has been read incorrectly by pandas. If the function would create a date which doesn't exist, the original date is returned. 

If `errors` are ignored for this function, original date is returned.

!!! warning "Data Type Warning"
    This function only works on dates - pandas DataFrame columns must be converted to datetime with `pd.to_datetime()` before being passed to this function.

=== "Example with single date"

    ```Python

    import heat_helper as hh

    date_to_reverse = date(2025, 1, 2)

    print(f"Original date: {date_to_reverse}")

    check = hh.reverse_date(date_to_reverse)

    print(f"Reversed date: {check}")

    #Output: 
    #Original date: 2025-01-02
    #Reversed date: 2025-02-01
    ```


=== "Example with pandas DataFrame"

    ```Python

    import heat_helper as hh

    dates = {'Dates' : [
        '2025-01-02', 
        '2025-10-31', 
        '2025-11-03', 
        '2025-08-09', 
        '', 
        None]}

    df = pd.DataFrame(dates)

    df['Dates'] = pd.to_datetime(df['Dates'])

    print(df.head(10))

    df['Reversed'] = df['Dates'].apply(hh.reverse_date)

    print(df.head(10))

    #Output: 
    #       Dates   Reversed
    #0 2025-01-02 2025-02-01
    #1 2025-10-31 2025-10-31
    #2 2025-11-03 2025-03-11
    #3 2025-08-09 2025-09-08
    #4        NaT        NaT
    #5        NaT        NaT
    ```

## Calculate Date of Birth Range from Year Group
This function calculates the date of birth range for a given year group. It returns a tuple of the start of the date of birth range (1st September (calculated year)) and the end of the date of birth range (31st August (calculated year)). It can calculate a date of birth range for any year group between Reception and Year 13. 

!!! Warning "Error Warning"
    This function cannot calculate date of birth ranges for FE Levels. It will raise `FELevelError` error if FE Levels are entered, or `InvalidYearGroupError` if a Year Group is outside of the expected range (0-13). If `errors` are ignored, a tuple of None, None is returned. You can set `error` behaviour using the errors argument.


=== "Example with list of dates"

    ```Python
    import heat_helper as hh

    start_date, end_date = hh.calculate_dob_range_from_year_group('Year 8')

    print(f
        "Students in Year 8 have dates of birth between {start_date} and {end_date}"
        )

    # Output:
    # Students in Year 8 have dates of birth between 2012-09-01 and 2013-08-31
    ```

=== "Example with pandas DataFrame"

    ```Python
    import heat_helper as hh
    import pandas as pd
    from datetime import date

    # Create example DataFrame
    df_dict = {'Year Group' : ['Year 7', 8, 'Y9', 'year 10', 11, 'Year 12', 
                                'YEAR13', None, 'FE Level 3', 'Year 15']}
    df = pd.DataFrame.from_dict(df_dict)
    df['Year Group'] = df['Year Group'].astype(str)

    # Apply function
    df['DOB Start'], df['DOB End'] = hh.calculate_dob_range_from_year_group(
        df['Year Group'], errors='ignore')
    print(df)

    #Output:
    #   Year Group   DOB Start     DOB End
    #      Year 7  2013-09-01  2014-08-31
    #           8  2012-09-01  2013-08-31
    #          Y9  2011-09-01  2012-08-31
    #     year 10  2010-09-01  2011-08-31
    #          11  2009-09-01  2010-08-31
    #     Year 12  2008-09-01  2009-08-31
    #      YEAR13  2007-09-01  2008-08-31
    #        None        None        None
    #  FE Level 3        None        None
    #     Year 15        None        None

    ```
