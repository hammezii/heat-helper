# Updates
These functions are used to check if updates are required when matching data of new students to existing HEAT records. They return only the data that is different from your HEAT records, which can be copied to HEAT upload templates to bulk update records.

## Get Updates
This function compares two DataFrame columns and returns a value if `new_col` is different to `heat_col`. This can help you identify where new data is different to existing HEAT records and therefore needs updating. It returns a new column which only contains data that needs to be updated - so it can be copied to the HEAT import template.

!!! Note
    This function copies the original DataFrame in memory and does not modify your original DataFrame in place.

For example, if you have collected new student data and matched this to your existing HEAT records and discover that some students already have records, you can use this function to check if the new data is different to the current records. If there are differences, the new data will be returned in the return column so that you can easily identify changes.

!!! Tip
    If used on string columns, it will attempt to 'normalise' nulls by filling them with blank strings and then turning them to None. This should mean that no null values are returned as 'new' data.

=== "Example"

    ```Python
    import heat_helper as hh
    import pandas as pd

    # Example Data: we want to check if any postcodes in NEW Postcode 
    # are different to the existing HEAT Postcodes
    #
    #       NEW Full Name NEW Postcode HEAT Postcode
    #            Jane Doe      BB1 1AB       AA1 1AA
    #          Mike Jones      BB2 2BB       BB2 2BB
    #        Thomas Smith                    CC3 3CC
    #         Sarah Brown      DD4 4DD       DD4 4DD
    #  Christopher Bloggs      AA1 1AA          None

    df['Updated Postcodes'] = hh.get_updates(
    df,
    'NEW Postcode',
    'HEAT Postcode'
    )

    # Result: Jane Doe's postcode needs updating, as does Christopher's 
    # (which was blank on HEAT)
    #
    #       NEW Full Name NEW Postcode HEAT Postcode Updated Context
    #            Jane Doe      BB1 1AB       AA1 1AA         BB1 1AB
    #          Mike Jones      BB2 2BB       BB2 2BB            None
    #        Thomas Smith         None       CC3 3CC            None
    #         Sarah Brown      DD4 4DD       DD4 4DD            None
    #  Christopher Bloggs      AA1 1AA          None         AA1 1AA

    ```

=== "Example: running on multiple cols at once"

    ```Python
    import heat_helper as hh
    import pandas as pd

    personal_columns_to_update = [
    "First Name",
    "Middle Name",
    "Last Name",
    "Date of Birth",
    "Home Postcode",
    "Last known Institution HEAT ID",
    "Last known Institution Name",
    "Individual Data Collection Date",
    "Individual Data Collection Privacy Form",
    "Phase Adjustment",
    ]

    # Update person cols if new data is different to old
    for col in personal_columns_to_update:
        heat_col = f"HEAT: {col}"
        update_col = f"Update: {col}"
        df[update_col] = hh.get_updates(df, col, heat_col)

    # This would create a new column for each column in personal_columns_to_update 
    # containing only data that needs updating

    ```

## Get Contextual Updates
This function compares two DataFrame columns and returns a value if `new_col` is different to `heat_col` and if the values in `new_col` are not in `bad_values`. This can help you identify where new data is different to existing HEAT records and therefore needs updating, but will not override 'good' data with values like 'Not available' 'Unknown' or 'Information Refused'. It returns a new column which only contains data that needs to be updated - so it can be copied to the HEAT import template.

For example, if you have collected new student data and matched this to your existing HEAT records and discover that some students already have records, you can use this function to check if the new data is different to the current records. If there are differences, the new data will be returned in the return column so that you can easily identify changes.

!!! Note
    This function copies the original DataFrame in memory and does not modify your original DataFrame in place.

The best use case for this function is on the contextual data columns in the HEAT Student Export, as you can pass all 'bad' values as a list, tuple, set or any other Iterable and avoid them overwriting older data.

!!! Tip
    If used on string columns, it will attempt to 'normalise' nulls by filling them with blank strings and then turning them to None. This should mean that no null values are returned as 'new' data.

=== "Example"

    ```Python
    import heat_helper as hh
    import pandas as pd

    # Example Data: we want to check if any values in NEW Context 
    # are different to the existing HEAT Context, but we don't want
    # values like 'Not available' or 'Information Refused' to overwrite 
    # 'good' values like 'Yes' and 'No'.
    #
    #       NEW Full Name          NEW Context HEAT Context
    #            Jane Doe        Not available          Yes
    #          Mike Jones  Information Refused           No
    #        Thomas Smith                  Yes           No
    #         Sarah Brown                                No
    #  Christopher Bloggs                  Yes          Yes

    df['Updated Context'] = hh.get_contextual_updates(
    df,
    'NEW Context',
    'HEAT Context',
    bad_values = ['Not available', 'Information Refused']
    )

    # Result: only Thomas Smith's Context needs updating
    #
    #       NEW Full Name          NEW Context HEAT Context Updated Context
    #            Jane Doe        Not available          Yes            None
    #          Mike Jones  Information Refused           No            None
    #        Thomas Smith                  Yes           No             Yes
    #         Sarah Brown                 None           No            None
    #  Christopher Bloggs                  Yes          Yes            None

    ```

=== "Example: running on multiple cols at once"

    ```Python
    import heat_helper as hh
    import pandas as pd

    # Define the "bad" values we do not want to be overridden 
    # by good values (lose no data via updates)
    BAD_VALUES = (
    "Not available",
    "Information refused",
    "Not available (999)",
    "Unknown",
    "Not known (997)",
    "Prefer not to say (998)",
    "Prefer not to say",
    )

    contextual_columns_to_update = [
    "Sex",
    "First Generation HE",
    "Disability",
    "Ethnicity",
    "Refugee / Asylum Seeker",
    "Care Leaver",
    "Estranged",
    "Service Children",
    "Young Carer",
    ]

    # Update contextual only if new data is different AND 'good'
    for col in contextual_columns_to_update:
        left_col = col
        heat_col = f"HEAT: {col}"
        update_col = f"Update: {col}"

        # Create all cols in the list
        df[update_col] = hh.get_contextual_updates(df, 
                                left_col, heat_col, BAD_VALUES)

    # This would create a new column for each column in 
    # contextual_columns_to_update containing only data that needs 
    # updating

    ```