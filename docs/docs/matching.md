# Matching
These functions are used to match student data to your HEAT records using the Student Export. They can be used to check if students in newly collected data already have records or to find Student IDs for registering students to activities within HEAT.

## Perform Exact Match
This function is used to exactly match student data to records in your HEAT Student Export. It uses the `pandas` `merge` function, which joins two DataFrames on common columns. You can use any number of columns to perform the join, but the number of columns passed to `left_join_cols` and `right_join_cols` must match. You can choose to return just the HEAT IDs from the HEAT export, or all columns in your HEAT Sudent Export using the `verify` argument. 

!!! Tip
    If you want to return all columns from your Student Export you may wish to drop some columns from the DataFrame before you use this function, as the resulting DataFrame may have a higher number of columns. For example, you might only wish to include columns needed to verify the match, or ones which you might want to check for updates if you're using this function on new data you want to upload to HEAT.

This function returns two DataFrames: one containing your matches, and one containing remaining student data which was not matched in its original format. This can be used for matching again, for example by using this function again with less strict criteria, or by using any other matching functions. The DataFrame containing your matches includes a column called 'Match Type' populated with whatever text you passed to `match_desc`. This can be useful if you join results of multiple matching functions together to one DataFrame to verify later: it helps you identify which matches were returned by which functions.

!!! Note
    The function assumes the column in the HEAT export with the IDs in is called 'Student HEAT ID'. If for any reason your column is not called this, you should set the name by passing a value to the optional `heat_id_col` argument. See [API documentation](matching-doc.md#heat_helper.matching.perform_exact_match).

=== "Example with pandas DataFrames"

    ```Python
    import heat_helper as hh
    from datetime import date
    import pandas as pd

    print(f"------ NEW DATA")
    print(new_data)
    print(f"------ HEAT DATA")
    print(heat)

    print(f"------ STARTING MATCH")
    matched, unmatched = hh.perform_exact_match(
        new_data,
        heat,
        ['Full Name', 'Date of Birth', 'Postcode'],
        ['Student Full Name', 'Student Date of Birth', 'Student Postcode'],
        'Exact match',
        student_heat_id_col='ID'
    )

    print(f"------ MATCHED DATA")
    print(matched)
    print(f"------ UNMATCHED DATA")
    print(unmatched)

    # Output
    #------ NEW DATA
    #      Full Name Date of Birth Postcode
    #0      Jane Doe    2008-09-02  AA1 1AA
    #1  Thomas Smith    2008-12-25  CC3 3CC
    #2    Mike Jones    2009-07-25  BB2 2BB
    #3   Sarah Brown    2008-11-13  DD4 4DD
    #
    #------ HEAT DATA
    #          ID Student Full Name Student Date of Birth Student Postcode  
    #0  #00000001          Jane Doe            2008-09-02          AA1 1AA
    #1  #00000002     Michael Jones            2009-07-25          BB2 2BB
    #2  #00000003      Thomas Smith            2008-12-25          CC3 3CC
    #3  #00000004       Sarah Brown            2008-11-13          DD4 4DD
    #4  #00000005          Jane Doe            2008-09-02          AA1 1AA
    #
    #------ STARTING MATCH
    #   Attempting match: Exact match:
    #     ...3 students found in HEAT data
    #     ...1 students left to find.
    #     WARNING: 1 extra record(s) created. Some student matched to multiple 
    #       HEAT records. Check HEAT data for duplicates.
    #
    #------ MATCHED DATA
    #      Full Name Date of Birth Postcode         ID   Match Type
    #0      Jane Doe    2008-09-02  AA1 1AA  #00000001  Exact match
    #1      Jane Doe    2008-09-02  AA1 1AA  #00000005  Exact match
    #2  Thomas Smith    2008-12-25  CC3 3CC  #00000003  Exact match
    #3   Sarah Brown    2008-11-13  DD4 4DD  #00000004  Exact match
    #
    #------ UNMATCHED DATA
    #    Full Name Date of Birth Postcode
    #0  Mike Jones    2009-07-25  BB2 2BB
    ```

## Perform Fuzzy Match
This function uses fuzzy matching on student names to find students in your HEAT Student Export. In order to improve the likelihood of matches, the function uses any number of columns to filter the pool of possible matches, and then returns the best match from this pool. It only returns one match (the best match) per student in your new DataFrame.

!!! Tip
    Unlike the exact match function above, this function returns all columns from the HEAT Student Export as it assumes you will need to verify the matches. This means the resulting DataFrame may have a high number of columns. You might wish to drop some columns from your HEAT Student Export before using this function. For example, you might only wish to include columns needed to verify the match, or ones which you might want to check for updates if you're using this function on new data you want to upload to HEAT.

You can control the strictness of the match with the `threshold` argument. This defaults to 80, but you may want to experiment with different values depending on how many columns you are using to control the match pool. If you are only looking for name fuzzy matches where Date of Birth and Postcode matches, you could lower the threshold to 70, as there will be a limited pool of potential matches, for example.

!!! Warning
    Before using this function you must create a column in both DataFrames which contains the students' full names. You can use the [create full name](names.md#create-full-name) function to do this.

This function returns two DataFrames: one containing your matches, and one containing remaining student data which was not matched in its original format. This can be used for matching again, for example by using this function again with less strict criteria, or by using any other matching function.

The matches DataFrame includes a column called Fuzzy Score which tells you the percentage match between the names. Higher means the names are more similar. 100 means the names match exactly. It also includes a column called 'Match Type' populated with whatever text you passed to `match_desc`. This can be useful if you join results of multiple matching functions together to one DataFrame to verify later: it helps you identify which matches were returned by which functions.

!!! Warning
    This function uses iterative processing and may be slow for datasets with >10,000 rows. Consider testing with a sample first, or removing exact matches using `perform_exact_match` before you attempt fuzzy matching.

=== "Example with pandas DataFrame"

    ```Python
    import heat_helper as hh
    from datetime import date
    import pandas as pd

    print(f"------ NEW DATA")
    print(new_data)
    print(f"------ HEAT DATA")
    print(heat)

    print(f"------ STARTING MATCH")
    matched, unmatched = hh.perform_fuzzy_match(
        new_data,
        heat,
        ['Date of Birth', 'Postcode'],
        ['Student Date of Birth', 'Student Postcode'],
        'Full Name',
        'Student Full Name',
        'Fuzzy Name DOB+Postcode match',
        threshold=70,
    )

    print(f"------ MATCHED DATA")
    print(matched)
    print(f"------ UNMATCHED DATA")
    print(unmatched)

    # Output
    #------ NEW DATA
    #            Full Name Date of Birth Postcode
    #0            Jane Doe    2008-09-02  AA1 1AA
    #1          Mike Jones    2009-07-25  BB2 2BB
    #2        Thomas Smith    2008-12-25  CC3 3CC
    #3         Sarah Brown    2008-11-13  DD4 4DD
    #4  Christopher Bloggs    2010-12-30  EE5 5EE
    #
    #------ HEAT DATA
    #        ID     Student Full Name Student Date of Birth  Student Postcode
    #0  #00000001          Jane Doe            2008-09-02          AA1 1AA
    #1  #00000002     Michael Jones            2009-07-25          BB2 2BB
    #2  #00000003      Thomas Smith            2008-12-25          CC3 3CC
    #3  #00000004       Sarah Brown            2008-11-13          DD4 4DD
    #4  #00000005          Jane Doe            2008-09-02          AA1 1AA
    #5  #00000006  Sarah Jane Brown            2008-11-13          DD4 4DD
    #
    #------ STARTING MATCH
    #Attempting fuzzy match where ['Date of Birth', 'Postcode'] match HEAT data.
    #    ...4 students found in HEAT data.
    #    ...1 students left to find.
    #
    #------ MATCHED DATA
    #      Full Name Date of Birth Postcode  ... Fuzzy Score  Match Type
    #0      Jane Doe    2008-09-02  AA1 1AA  ...      100.00  Fuzzy Name DOB+Postcode match
    #1  Thomas Smith    2008-12-25  CC3 3CC  ...      100.00  Fuzzy Name DOB+Postcode match
    #2   Sarah Brown    2008-11-13  DD4 4DD  ...      100.00  Fuzzy Name DOB+Postcode match
    #3    Mike Jones    2009-07-25  BB2 2BB  ...       78.26  Fuzzy Name DOB+Postcode match
    #
    #------ UNMATCHED DATA
    #            Full Name Date of Birth Postcode
    #4  Christopher Bloggs    2010-12-30  EE5 5EE
    ```

## Perform School Age Range Fuzzy Match
This function fuzzy matches student names to your HEAT Export by grouping potential matches by school and year group. It is particularly useful if you do not have a student date of birth but you do know which year group they are in. The function uses year group to create a date of birth range to search within from the student's school.

!!! Tip
    You can either use School Name or School ID to group students by school, but you should ensure that the data you are trying to match to your HEAT Student Export contains school names or IDs exactly as they appear on HEAT, or the function will not work.

You can control the strictness of the match with the `threshold` argument. This defaults to 80, but you may want to experiment with different values depending on how strict you want the fuzzy match to be.

!!! Warning
    Before using this function you must create a column in both DataFrames which contains the students' full names. You can use the [create full name](names.md#create-full-name) function to do this.

This function returns two DataFrames: one containing your matches, and one containing remaining student data which was not matched in its original format. This can be used for matching again, for example by using this function again with less strict criteria, or by using any other matching function.

!!! Warning
    This function uses iterative processing and may be slow for datasets with >10,000 rows. Consider testing with a sample first, or removing exact matches using `perform_exact_match` before you attempt fuzzy matching.

The matches DataFrame includes a column called Fuzzy Score which tells you the percentage match between the names. Higher means the names are more similar. 100 means the names match exactly. It also includes a column called 'Match Type' populated with whatever text you passed to `match_desc`. This can be useful if you join results of multiple matching functions together to one DataFrame to verify later: it helps you identify which matches were returned by which functions.

!!! Note
    The function assumes the column in the HEAT export with the IDs in is called 'Student HEAT ID'. If for any reason your column is not called this, you should set the name by passing a value to the `heat_id_col` argument. See [API documentation](matching-doc.md#heat_helper.matching.perform_school_age_range_fuzzy_match).

=== "Example with pandas DataFrame"

    ```Python
    import heat_helper as hh
    import pandas as pd

    matched_df, unmatched_df = hh.perform_school_age_range_fuzzy_match(
    new,
    heat,
    'School',
    'Student School',
    'Full Name',
    'Student Full Name',
    'Year Group',
    'Student Date of Birth',
    'DOB In Range for YG',
    heat_id_col = 'ID'
    )

    #---- NEW DATA
    #           Full Name Postcode    School Year Group
    #            Jane Doe  AA1 1AA  School A    Year 12
    #          Mike Jones  BB2 2BB  School A    Year 12
    #        Thomas Smith  CC3 3CC  School A    Year 12
    #         Sarah Brown  DD4 4DD  School B    Year 12
    #  Christopher Bloggs  EE5 5EE  School B    Year 10
    #
    #---- HEAT DATA
    #           ID         Full Name Date of Birth Postcode    School
    #  #00000001         Janie Doe    2008-09-02  AA1 1AA  School A
    #  #00000002     Michael Jones    2009-07-25  BB2 2BB  School A
    #  #00000003      Thomas Smith    2008-12-25  CC3 3CC  School A
    #  #00000004       Sarah Brown    2008-11-13  DD4 4DD  School B
    #  #00000005          Jane Doe    2008-09-02  AA1 1AA  School B
    #  #00000006  Sarah Jane Brown    2008-11-13  DD4 4DD  School A
    #
    #---- MATCHED DATA
    #  Full Name Postcode    School Year Group   HEAT: ID HEAT: Full Name HEAT: Date of Birth HEAT: Postcode HEAT: School  Fuzzy Score           Match Type
    #  Thomas Smith  CC3 3CC  School A    Year 12  #00000003    Thomas Smith          2008-12-25        CC3 3CC     School A       100.00  DOB In Range for YG
    #   Sarah Brown  DD4 4DD  School B    Year 12  #00000004     Sarah Brown          2008-11-13        DD4 4DD     School B       100.00  DOB In Range for YG
    #      Jane Doe  AA1 1AA  School A    Year 12  #00000001       Janie Doe          2008-09-02        AA1 1AA     School A        94.12  DOB In Range for YG
    #
    #---- UNMATCHED DATA
    #           Full Name Postcode    School Year Group
    #          Mike Jones  BB2 2BB  School A    Year 12
    #  Christopher Bloggs  EE5 5EE  School B    Year 10
    ```
