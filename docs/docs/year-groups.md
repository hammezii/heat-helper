# Year Groups
These functions are for use with year groups.

## Clean Year Group
This function is designed to standardise the way that year groups appear in your data. Year Groups (1-13) are formatted to: 'Year i' or 'Reception'. It will also raise an error if a year group is not within the range 0 (Reception) to 13. 

!!! Warning "Error Warning"
    This function cannot clean FE Levels. It will raise `FELevelError` error if FE Levels are entered, or `InvalidYearGroupError` if a Year Group is outside of the expected range (0-13) is entered. If `errors` are ignored, the original value is returned. You can set `error` behaviour using the errors argument.

=== "Example on list"

    ``` Python
    import heat_helper as hh

    year_group_messy = ['Year 10', 'Y9', 10, 'year 11', 'reception', 'year r']

    clean_year_groups = [hh.clean_year_group(yg, errors='ignore') 
                            for yg in year_group_messy]

    print(clean_year_groups)

    # Output: ['Year 10', 'Year 9', 'Year 10', 'Year 11', 'Reception', 'Reception']
    ```

=== "Example on pandas DataFrame"

    ```Python
    import heat_helper as hh
    import pandas as pd

    year_group_messy = ['Year 10', 'Y9', 10, 'year 11', 'reception', 'year r']

    yg_dict = {'Year Group' : year_group_messy}

    yg_df = pd.DataFrame(yg_dict)

    yg_df['Clean YG'] = yg_df['Year Group'].apply(hh.clean_year_group)

    print(yg_df.head(6))

    # Output
    #  Year Group   Clean YG
    #0    Year 10    Year 10
    #1         Y9     Year 9
    #2         10    Year 10
    #3    year 11    Year 11
    #4  reception  Reception
    #5     year r  Reception
    ```

## Calculate Year Group from Date
This function calculates which year group a date of birth falls into. Useful for checking students are in the year group you have been told (e.g. by the student or by the school), and then calculating a Phase Adjustment value if necessary. Year group is calculated for the current academic year. This can be overridden using the `start_year` argument to calculate which year group students would have been in in previous academic years. See [API documentation](year-groups-doc.md#heat_helper.yeargroup.calculate_year_group_from_date). 

Year groups are returned in the format 'Year i' except for Reception which is returned as 'Reception'. If errors are ignored for this funtion, None is returned.

!!! failure "Warning"
    Calculating a year group from a date of birth is not always correct - some students may not be in the 'correct' year group for their date of birth for a variety of reasons. This might particularly be the case at post-16 level or for students with dates of birth in August, who sometimes start school the following year.

This function will only return Reception to Year 13. If a student is too young for school, 'Student too young for school' will be returned. If a student is too old for school, an `InvalidYearGroupError` will be returned, unless errors are ignored.

=== "Example with single date"

    ```Python
    import heat_helper as hh
    from datetime import date

    date_yg = date(2011, 1, 2)

    year_group = hh.calculate_year_group_from_date(date_yg)

    print(f"Date: {date_yg} is in {year_group}")

    # Output:
    # Date: 2011-01-02 is in Year 10
    ```

=== "Example on pandas DataFrame"

    ```Python
    import heat_helper as hh
    import pandas as pd
    from datetime import date

    date_dict = {'Date of birth' : 
        [date(2013, 9, 1), 
        date(2013, 7, 25), 
        date(2014, 2, 20), 
        date(2010, 9, 1)]}

    date_df = pd.DataFrame(date_dict)

    date_df['Year Group'] = date_df['Date of birth']
        .apply(hh.calculate_year_group_from_date)

    print(date_df)

    # Output:
    #  Date of birth Year Group
    #0    2013-09-01     Year 7
    #1    2013-07-25     Year 8
    #2    2014-02-20     Year 7
    #3    2010-09-01    Year 10
    ```

