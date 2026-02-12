# Getting Started
`heat_helper` is designed to be easy to use and to integrate with your python workflow, especially if you are already familiar with common data packages like `pandas`. 

## Importing heat_helper into your projects
Once installed, you can import `heat_helper`:

```Python
import heat_helper as hh
```

Then use any of the functions in the [usage documentation](names.md).

!!! Example

    ```Python
    import heat_helper as hh

    name = ' JANE    DoE '
    clean_name = hh.format_name(name)
    print(clean_name)

    # Output: Jane Doe
    ```

## Using cleaning functions
Many `heat_helper` cleaning functions can be used on a column in a DataFrame by using the `pandas` `.apply()` method.

!!! Example

    ```Python
    import heat_helper as hh
    import pandas as pd

    df = pd.read_csv('register.csv')

    # Create a new column containing the cleaned names
    df['Clean Names'] = df['Names'].apply(hh.format_name, errors='ignore')

    # Output
    #             Names     Clean Names
    #          JANE DOE        Jane Doe
    #     jane      doe        Jane Doe
    #  Sarah - Jane Doe  Sarah-Jane Doe
    #          jane DOE        Jane Doe
    #   Sarah- Jane Doe  Sarah-Jane Doe
    #        jane mcdoe      Jane McDoe
    #        jane O'Doe      Jane O'Doe
    ```

## Example: cleaning data and matching to heat
A simple scenario in which you might use `heat_helper` would be to clean activity registers and then match students to their HEAT records. This example assumes you have already loaded your CSV or Excel files as `df` (your register data) and `heat_df` (your HEAT student export).

!!! Example

    ```Python
    # You have collected the following register from an activity. 
    # Because you were on the run from a Demogorgon on the way back 
    # from the Upside Down, the data is a bit messy:

    #       Jane      Hopper    2000-01-01   AA1 1AA
    #       mike     Wheeler    2000-02-02   bb22bb
    #    Lucas.     Sinclair    2000-03-03   C33cc
    #    Robin 1     Buckley    1997-04-04   DD44DD
    #      steve  harrington    1997-05-05    E55EE
    #     dustin  HENDERSON     2000-06-06   F6 6FF

    # Clean the data
    df['First Name'] = df['First Name'].apply(hh.format_name)
                                        .apply(hh.remove_numbers)
                                        .apply(hh.remove_punctuation)

    df['Last Name'] = df['Last Name'].apply(hh.format_name)
                                    .apply(hh.remove_numbers)
                                    .apply(hh.remove_punctuation)
                                    
    df['Postcode'] = df['Postcode'].apply(hh.format_postcode)

    df['Date of Birth'] = pd.to_datetime(df['Date of Birth']).dt.normalize()

    print(df)

    # The data now looks like this:

    # First Name   Last Name Date of Birth Postcode
    #       Jane      Hopper    2000-01-01  AA1 1AA
    #       Mike     Wheeler    2000-02-02  BB2 2BB
    #      Lucas    Sinclair    2000-03-03   C3 3CC
    #      Robin     Buckley    1997-04-04  DD4 4DD
    #      Steve  Harrington    1997-05-05   E5 5EE
    #     Dustin   Henderson    2000-06-06   F6 6FF

    # Now you want to match the records to HEAT. 
    # You've been on crawls in the Upside Down before so
    # you know these students already have a record on 
    # HEAT. You look for exact matches:

    matched_df, unmatched_df = hh.perform_exact_match(
        df, 
        heat_df, 
        ['First Name', 'Last Name', 'Date of Birth', 'Postcode'],
        ['First Name', 'Last Name', 'Date of Birth', 'Postcode'],
        "Exact Match")

    print(matched_df)

    # This returns their HEAT IDs, which you can paste into your 
    # HEAT upload template to register them to the activity:

    # First Name   Last Name Date of Birth Postcode     Match Type HEAT: HEAT ID
    #       Jane         Doe    2000-01-01  AA1 1AA  Exact Match           #1
    #       Mike     Wheeler    2000-02-02  BB2 2BB  Exact Match           #2
    #      Lucas    Sinclair    2000-03-03   C3 3CC  Exact Match           #3
    #      Robin     Buckley    1997-04-04  DD4 4DD  Exact Match           #4
    #      Steve  Harrington    1997-05-05   E5 5EE  Exact Match           #5
    #     Dustin   Henderson    2000-06-06   F6 6FF  Exact Match           #6
    ```