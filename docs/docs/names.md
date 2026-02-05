# Names and Text
These functions are used to help you clean and format student names.

## Format Name
This function takes text (names) and cleans them. It carries out a number of common cleaning steps:

- changes to title case (with exceptions for names like McDonald and O'Reilly),
- removes any number of spaces either side of hyphens,
- cleans instances of more than one space and changes it to a single space,
- cleans leading or trailing whitespace.

!!! info
    You can pass the `errors` argument to control error behaviour. Default is 'raise' which will raise all errors and stop your script. 'ignore' will not raise an error and return the original value. 'coerce' will not raise an error and return None.

    To use the errors argument when passing to a pandas dataframe use: 
    `df['Clean Names'] = df['Names'].apply(hh.format_name, errors='ignore')`

=== "Clean one name"

    ```Python
    import heat_helper as hh

    # Example: clean one name
    name = ' JANE    DoE '
    clean_name = hh.format_name(name)
    print(clean_name)

    #Output: Jane Doe
    ```

=== "Clean a list of names"

    ```Python
    import heat_helper as hh

    messy_names = ["JANE DOE", 
                "jane      doe", 
                "jane DOE", 
                "Sarah - Jane Doe ", 
                " Sarah- Jane Doe", 
                "jane mcdoe", 
                "jane O'Doe"]

    clean_names = [hh.format_name(name) for name in messy_names]

    print(clean_names)

    # Output: 
    # ["Jane Doe", 
    # "Jane Doe", 
    # "Jane Doe", 
    # "Sarah-Jane Doe", 
    # "Sarah-Jane Doe", 
    # "Jane McDoe", 
    # "Jane O'Doe"]
    ```

=== "Clean a pandas DataFrame column"

    ```Python
    import heat_helper as hh
    import pandas as pd

    messy_names = {'Names' :[
        "JANE DOE",
        " jane      doe",
        "jane DOE",
        "Sarah - Jane Doe ",
        "Sarah- Jane Doe",
        "jane mcdoe",
        "jane O'Doe",
    ]}

    df = pd.DataFrame(data=messy_names)

    df['Clean Names'] = df['Names'].apply(hh.format_name)

    print(df.head(10))

    # Output
    #              Names     Clean Names
    #0          JANE DOE        Jane Doe
    #1     jane      doe        Jane Doe
    #3  Sarah - Jane Doe  Sarah-Jane Doe
    #2          jane DOE        Jane Doe
    #4   Sarah- Jane Doe  Sarah-Jane Doe
    #5        jane mcdoe      Jane McDoe
    #6        jane O'Doe      Jane O'Doe
    ```


## Find Numbers in Text
This function takes text and returns True/False if one or more numbers is present (0-9). This can be useful for checking if numbers appear in names, either due to data entry error or because numbers have been added to names to differentiate students with the same name. You can use this function to check if names contain numbers before you attempt to remove then. This can be useful if a student has had a letter replaced by a number (e.g. zero for the letter O), and removing the numbers would leave the letter O missing. By checking first, you can confirm that it is safe to remove numbers. 

!!! info
    You can pass the `errors` argument to control error behaviour. Default is 'raise' which will raise all errors and stop your script. 'ignore' will not raise an error and return the original value. 'coerce' will not raise an error and return None.
    
    You can use the optional `convert_to_string` argument to set whether data passed to this function is converted to a string before the function runs.

=== "Example with one name"

    ```Python
    import heat_helper as hh

    name_to_check = 'Jane Doe 23'

    is_numbers = hh.find_numbers_in_text(name_to_check)

    print(f"Are there numbers in '{name_to_check}'? Answer: {is_numbers}")

    #Output: Are there numbers in 'Jane Doe 23'? Answer: True
    ```

=== "Example with pandas DataFrame column"

    ```Python
    import heat_helper as hh
    import pandas as pd

    # Example Data
    #  First Name   Last Name
    #       Jane   Hopper 23
    #       mike     Wheeler
    #    Lucas.     Sinclair
    #    Robin 1     Buckley
    #      st3ve  harrington
    #     dustin  HENDERSON
    #      nancY    wheeler

    df['Numbers in First Name'] = df['First Name'].apply(hh.find_numbers_in_text)
    df['Numbers in Last Name'] = df['Last Name'].apply(hh.find_numbers_in_text)

    #Output: 
    #  First Name   Last Name  Numbers in First Name  Numbers in Last Name
    #       Jane   Hopper 23                  False                  True
    #       mike     Wheeler                  False                 False
    #    Lucas.     Sinclair                  False                 False
    #    Robin 1     Buckley                   True                 False
    #      st3ve  harrington                   True                 False
    #     dustin  HENDERSON                   False                 False
    #      nancY    wheeler                   False                 False
    ```


## Remove Numbers
This functions takes text and removes any numbers that are present (0-9). This can be useful for removing numbers from the end of names where you may have been provided data in the format 'Jane Doe 1', 'Jane Doe 2' to differentiate students with the same name. Typically, these numbers would not be added to records on the HEAT database, as other identifying information like date of birth or postcode can usually help you differentiate students in the database.

!!! warning
    If a number has been used in place of a letter, this function will remove the number but cannot replace it with the letter it should represent. 'St3ve' will become 'Stve'.
    The `find_numbers_in_text` function can help you identify rows with numbers in them by allowed you to filter on 'True' to check what will be removed.

The function will remove any number of numbers. Numbers do not have to be consecutive.

!!! info
    You can pass the `errors` argument to control error behaviour. Default is 'raise' which will raise all errors and stop your script. 'ignore' will not raise an error and return the original value. 'coerce' will not raise an error and return None.
    
    You can use the optional `convert_to_string` argument to set whether data passed to this function is converted to a string before the function runs.

=== "Example with one name"

    ```Python
    import heat_helper as hh

    name = 'Jane Doe 23'

    clean_name = hh.remove_numbers(name)

    print(f"Clean name is '{clean_name}'")

    #Output: Clean name is 'Jane Doe'
    ```

=== "Example with pandas DataFrame column"

    ```Python
    import heat_helper as hh
    import pandas as pd

    # Example Data
    #  First Name   Last Name
    #       Jane   Hopper 23
    #       mike     Wheeler
    #    Lucas.     Sinclair
    #    Robin 1     Buckley
    #      st3ve  harrington
    #     dustin  HENDERSON
    #      nancY    wheeler

    df['Clean First Name'] = df['First Name'].apply(hh.remove_numbers)
    df['Clean in Last Name'] = df['Last Name'].apply(hh.remove_numbers)

    # Output
    #  First Name   Last Name Clean First Name Clean in Last Name
    #       Jane   Hopper 23             Jane             Hopper
    #       mike     Wheeler             mike            Wheeler
    #    Lucas.     Sinclair          Lucas.            Sinclair
    #    Robin 1     Buckley            Robin            Buckley
    #      st3ve  harrington             stve         harrington
    #     dustin  HENDERSON            dustin         HENDERSON
    #      nancY    wheeler             nancY           wheeler
    ```

## Create Full Name
This function concatenates several strings into one string, typically for names. This is necessary if you want to carry out exact or fuzzy matching between names on a register and names in your HEAT Student export. You should create a full name column in both dataframes and use this for [matching](matching.md).

!!! tip
    Middle names are optional. The function will run if you only have a first and last name string or column. Middle name functionality is included in case you use this field in HEAT.

=== "Example with single strings"

    ```Python
    
    import heat_helper as hh

    first = 'Jane'
    middle = 'Mary'
    last = 'Doe'

    full = hh.create_full_name(first, last)
    print(full)

    #Output: Jane Doe

    full = hh.create_full_name(first, last, middle_name=middle)
    print(full)

    #Output: Jane Mary Doe
    ```

=== "Example with pandas DataFrame columns"

    ```Python

    import heat_helper as hh
    import pandas as pd

    name_dict = {'First': ['Jane', 'Sarah', 'Jo'], 
             'Middle' : ['Rose', 'Louise', ''], 
             'Last' : ['Doe', 'Bloggs', 'McDonald']}

    df = pd.DataFrame(name_dict)

    df['Full Name'] = hh.create_full_name(
        df['First'], 
        df['Last'], 
        middle_name=df['Middle'])

    print(df.head())

    #   First  Middle      Last            Full Name
    #0   Jane    Rose       Doe        Jane Rose Doe
    #1  Sarah  Louise    Bloggs  Sarah Louise Bloggs
    #2     Jo          McDonald          Jo McDonald
    ```

## Remove Diacritics
Attempts to remove diacritics (accented characters) from text and replace them with equivalent letters. Useful for normalising names before upload to HEAT or to improve exact and fuzzy matching responses.

!!! info
    You can pass the `errors` argument to control error behaviour. Default is 'raise' which will raise all errors and stop your script. 'ignore' will not raise an error and return the original value. 'coerce' will not raise an error and return None.

=== "Example with one name"

    ```Python

    import heat_helper as hh

    diacritic = 'Chloë'

    clean = hh.remove_diacritics(diacritic)

    print(f"{diacritic} has been replaced with {clean}")

    # Output: Chloë has been replaced with Chloe
    ```

=== "Example with pandas DataFrame column"

    ```Python

    import heat_helper as hh
    import pandas as pd

    #Example data:
    #  First Name
    #      Renée
    #        Zoë
    #   François
    #      Chloë
    #       Siân

    df['Clean First Name'] = df['First Name'].apply(hh.remove_diacritics)
    print(df)

    # Output:
    # First Name Clean First Name
    #      Renée            Renee
    #        Zoë              Zoe
    #   François         Francois
    #      Chloë            Chloe
    #       Siân             Sian
    ```

## Remove Punctuation
Attempts to remove punctuation except for hyphens and apostrophes from text. It initially replaces punctuation with spaces before replacing multiple spaces with one space, and trimming trailing and leading spaces. This means that if you have a name like `Jane...Doe` this function will clean it to `Jane Doe`. Useful for normalising/cleaning names before upload to HEAT or to improve exact and fuzzy matching responses.

!!! info
    You can pass the `errors` argument to control error behaviour. Default is 'raise' which will raise all errors and stop your script. 'ignore' will not raise an error and return the original value. 'coerce' will not raise an error and return None.

=== "Example with one name"

    ```Python

    import heat_helper as hh

    punctuation = 'Jane! Doe.'

    clean = hh.remove_punctuation(punctuation)

    print(f"{punctuation} has been replaced with {clean}")

    # Output: Jane! Doe. has been replaced with Jane Doe
    ```

=== "Example with pandas DataFrame column"

    ```Python

    import heat_helper as hh
    import pandas as pd

    #Example data:
    #           Name
    #      Jane! Doe
    #  Jane O'Reilly
    #     \Zoe Jones
    #  James...Smith
    #    Jane? Smith

    df['Clean First Name'] = df['Name'].apply(hh.remove_punctuation)
    print(df)

    #           Name Clean First Name
    #      Jane! Doe         Jane Doe
    #  Jane O'Reilly    Jane O'Reilly
    #     \Zoe Jones        Zoe Jones
    #  James...Smith      James Smith
    #    Jane? Smith       Jane Smith
    ```