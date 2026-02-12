# File Processing
These functions help you manipulate files.

## Get Excel Filepaths in Folder
This function will get a list of Excel files in a specified folder. This can be useful if you want to get data from multiple files at once and join these into one DataFrame. For example, if you have 10 separate activity registers from outreach activities and want to combine them into one DataFrame to allow you to match the students to your HEAT records. 

This function returns a list of filepaths, or an empty list if there are no files in the folder.

=== "Example: simple usage"

    ```Python
    import heat_helper as hh

    folder_path = r"C:\path\to\registers"

    files = hh.get_excel_filepaths_in_folder(folder_path)

    print(files)

    # Output
    # ["C:\path\to\registers\file1.xslx", 
    # "C:\path\to\registers\file2.xslx", 
    # "C:\path\to\registers\file3.xslx"]
    ```

=== "Example: get register files to create master register"

    ```Python
    import heat_helper as hh

    folder_path = r"C:\path\to\registers"

    files = hh.get_excel_filepaths_in_folder(folder_path)

    # Initialise empty loop to add the registers to
    # so you can join them together efficiently with pd.concat
    register_files = []
    for file in files:
        reg = pd.read_excel(file, sheet_name="register")
        register_files.append(reg)

    # Join all files into one master DataFrame
    master_reg = pd.concat(register_files)
    
    ```

## Convert Columns to Snake Case
This functions converts the column headers or titles in your DataFrame to snake case (e.g. 'First Name' -> 'first_name'). This can be useful to help tidy data and normalise your headings by removing extra spaces, making them all lowercase, and by removing punctuation and special characters, or to make it easier to pass data to `pydantic` validation models. 

```Python
print(f"DataFrame columns names: {df.columns}")

# DataFrame columns names: Index(['First Name', 'Last Name', 'Date of Birth (dd/mm/yyyy)', 'Postcode'], dtype='object')

df = hh.convert_col_snake_case(df)

print(f"DataFrame columns names after conversion: {df.columns}")

# DataFrame columns names after conversion: Index(['first_name', 'last_name', 'date_of_birth_ddmmyyyy', 'postcode'], dtype='object')

```