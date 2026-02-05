# Duplicates
These functions help to find duplicates within your data.

## Find Duplicates
This function attempts to find duplicates within your data if given name, date of birth, and postcode. It first searches for exact matches and then looks for fuzzy name matches, using either date of birth and postcode or just date of birth, to limit the pool of potential matches. It returns a new column in your DataFrame called 'Potential Duplicates' which contains a list of ID numbers corresponding to the rows which are potential duplicates. If your data does not have a suitable column to use as the ID, one will be created by the function for you.

### Controlling for Similarity
There are three ways to control the similarity of the duplicate matching. The first way is to set a fuzzy matching threshold. By default this is 80, but you can reduce it. It must be a number between 1 and 100 and roughly equates to the percentage match you are willing to accept when fuzzy matching names. 

The second way is to choose whether to use only date of birth, or date of birth and postcode to limit the pool of potential matches. If you set `fuzzy_type` to 'strict' it will only return potential duplicates where both date of birth and postcode match. By default it is set to 'permissive', which only matches on date of birth before attempting name matches. 

Finally you can toggle `twin_protection` to True or False. By default this is set to True. This compares first names only and excludes any matches where the first name is less than 70% similar. This assumes that genuine duplicates with nicknames or typos in first names will be over the 70% threshold.

!!! failure "Warning"
    Twin protection is not foolproof and may still return some twins as potential duplicates or miss some students who are actual duplicates. In testing, turning this to True reduced the twins being returned as duplicates by roughly 75%.

=== "Example 1: No Twin Protection"

    ```Python
    import heat_helper as hh
    import pandas as pd

    # Example Data
    # Jane and Janie are duplicates 
    # (she has moved house and has a different postcode)
    # Sarah and Sam are twins
    #
    # First Name       Last Name Date of Birth Home Postcode
    #       Jane             Doe    2010-01-01       AA1 1AA
    #      James           Smith    2011-02-02       BB2 2AB
    #      Janie             Doe    2010-01-01       AB1 1AB
    #      Sarah  Robinson-Jones    2008-03-03       CC3 3CC
    #        Sam  Robinson-Jones    2008-03-03       CC3 3CC

    df = hh.find_duplicates(df,
                        ['First Name', 'Last Name'],
                        'Date of Birth',
                        'Home Postcode',
                        fuzzy_type='permissive',
                        threshold=80,
                        twin_protection=False
                        )
    
    # Results: Jane and Janie, and Sarah and Sam, have flagged as duplicates
    #                                                                Potential
    # First Name       Last Name Date of Birth Home Postcode   ID   Duplicates
    #        Sam  Robinson-Jones    2008-03-03       CC3 3CC   #5       #4, #5
    #      Sarah  Robinson-Jones    2008-03-03       CC3 3CC   #4       #4, #5
    #      Janie             Doe    2010-01-01       AB1 1AB   #3       #1, #3
    #       Jane             Doe    2010-01-01       AA1 1AA   #1       #1, #3
    #      James           Smith    2011-02-02       BB2 2AB   #2         None

    ```

=== "Example 2: Twin Protection"

    ```Python
    import heat_helper as hh
    import pandas as pd

    # Example Data
    # Jane and Janie are duplicates 
    # (she has moved house and has a different postcode)
    # Sarah and Sam are twins
    #
    # First Name       Last Name Date of Birth Home Postcode
    #       Jane             Doe    2010-01-01       AA1 1AA
    #      James           Smith    2011-02-02       BB2 2AB
    #      Janie             Doe    2010-01-01       AB1 1AB
    #      Sarah  Robinson-Jones    2008-03-03       CC3 3CC
    #        Sam  Robinson-Jones    2008-03-03       CC3 3CC

    df = hh.find_duplicates(df,
                        ['First Name', 'Last Name'],
                        'Date of Birth',
                        'Home Postcode',
                        fuzzy_type='permissive',
                        threshold=80,
                        twin_protection=True
                        )
    
    # Results: Jane and Janie have flagged as duplicates
    # Sarah and Sam have been excluded because twin_protection is True
    #                                                                Potential
    # First Name       Last Name Date of Birth Home Postcode   ID   Duplicates
    #      Janie             Doe    2010-01-01       AB1 1AB   #3       #1, #3
    #       Jane             Doe    2010-01-01       AA1 1AA   #1       #1, #3
    #        Sam  Robinson-Jones    2008-03-03       CC3 3CC   #5         None
    #      Sarah  Robinson-Jones    2008-03-03       CC3 3CC   #4         None
    #      James           Smith    2011-02-02       BB2 2AB   #2         None

    ```

=== "Example 3: Fuzzy Type 'Strict'"

    ```Python
    import heat_helper as hh
    import pandas as pd

    # Example Data
    # Jane and Janie are duplicates 
    # (she has moved house and has a different postcode)
    # Sarah and Sam are twins
    #
    # First Name       Last Name Date of Birth Home Postcode
    #       Jane             Doe    2010-01-01       AA1 1AA
    #      James           Smith    2011-02-02       BB2 2AB
    #      Janie             Doe    2010-01-01       AB1 1AB
    #      Sarah  Robinson-Jones    2008-03-03       CC3 3CC
    #        Sam  Robinson-Jones    2008-03-03       CC3 3CC

    df = hh.find_duplicates(df,
                        ['First Name', 'Last Name'],
                        'Date of Birth',
                        'Home Postcode',
                        fuzzy_type='strict',
                        threshold=80,
                        twin_protection=True
                        )
    
    # Results: No duplicates have been returned
    # Sarah and Sam have been excluded because twin_protection is True
    # Jane and Janie have been excluded because they have different postcodes
    #                                                                 Potential
    # First Name       Last Name Date of Birth Home Postcode    ID   Duplicates
    #        Sam  Robinson-Jones    2008-03-03       CC3 3CC    #5         None
    #      Sarah  Robinson-Jones    2008-03-03       CC3 3CC    #4         None
    #      Janie             Doe    2010-01-01       AB1 1AB    #3         None
    #      James           Smith    2011-02-02       BB2 2AB    #2         None
    #       Jane             Doe    2010-01-01       AA1 1AA    #1         None

    ```
