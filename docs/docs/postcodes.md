# Postcodes
These functions are designed to be run on postodes.

## Format Postode
This function takes a postcode, attempts to clean and format it in accordance to UK standards, and validate that it is a valid postcode form. The validation logic matches formats: A9 9AA, A99 9AA, AA9 9AA, AA99 9AA, A9A 9AA, AA9A 9AA. Postcodes will be returned with all uppercase letters, and a space between the outward and inward part.

Errors will be raised if postcode is not a valid string (text) or if the format does not conform to the UK standard. You can ignore errors with `errors='ignore'` which will return the original postcode. You can also 'coerce' errors which will attempt to turn postcode into a string. If this still fails and raises an error, None will be returned.

!!! failure "Warning"
    This function does not validate that a UK postcode _exists_, only that it conforms to the expected format.

=== "Example with list of postcodes"

    ```Python
    import heat_helper as hh

    postcode_messy = ['aa11aa', 'w1a7nn', 'ST1 1AA', 'ST1', 'st5   5BG']

    clean_postcodes = [hh.format_postcode(postcode, errors='ignore') for 
                        postcode in postcode_messy]

    print(clean_postcodes)

    #Output: ['AA1 1AA', 'W1A 7NN', 'ST1 1AA', 'ST1', 'ST5 5BG']
    ```

=== "Example on pandas dataframe"

    ```Python
    import heat_helper as hh
    import pandas as pd

    postcode_messy = ['aa11aa', 'w1a7nn', 'ST1 1AA', 'ST1', 'st5   5BG']

    postcode_dict = {'Postcodes' : postcode_messy}

    postcode_df = pd.DataFrame(postcode_dict)

    postcode_df['Clean Postcodes'] = postcode_df['Postcodes'].apply(
        hh.format_postcode, errors='coerce'
        )

    print(postcode_df.head(5))

    #Output:
    #   Postcodes Clean Postcodes
    #0     aa11aa         AA1 1AA
    #2    ST1 1AA         ST1 1AA
    #1     w1a7nn         W1A 7NN
    #3        ST1            None
    #4  st5   5BG         ST5 5BG
    ```
