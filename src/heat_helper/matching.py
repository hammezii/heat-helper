import pandas as pd
from rapidfuzz import process, fuzz

from heat_helper.exceptions import ColumnDoesNotExistError, FuzzyMatchIndexError, FilterColumnMismatchError

def perform_exact_match(
    unmatched_df: pd.DataFrame,
    heat_df: pd.DataFrame,
    left_join_cols: list[str],
    right_join_cols: list[str],
    match_type_desc: str,
    verify: bool = False,
    student_heat_id_col: str = 'Student HEAT ID'
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Performs an exact match on specified columns between new data and your HEAT Student export and returns the HEAT Student ID if a match is found.
    This function returns two DataFrames: one containing the matches and one containing unmatched students, for passing to another matching function. 
    This is useful to create a matching waterfall where you move through different levels of strictness.
    
    
    Args:
        unmatched_df: The DataFrame containing the students you want to search for.
        heat_df: The DataFrame containing your HEAT Student Export.
        left_join_cols: Columns in new_df you want to match on.
        right_join_cols: Columns in heat_df you want to match on.
        match_type_desc: A description of the match; added to a 'Match Type' col in the returned matched DataFrame. Should be descriptive to help you verify matches later, especially if joining multiple returns of this function and exporting to a .csv or Excel file.
        verify (optional): Defaults to False. Controls whether to return all columns from heat_df to the matched DataFrame for verifying of matches. Useful if you are performing a less exact match and you want to verify the returned students. Also useful if you are using this function or perform_fuzzy_match function and want to join results together (column structure will be the same).
        student_heat_id_col (optional): Defaults to 'Student HEAT ID'. Use this if the column in your HEAT Export with the Student ID in is not called 'Student HEAT ID'.

    Raises:
        TypeError: Raised if new_df or heat_df are not pandas DataFrames.
        ColumnDoesNotExistError: Raised if a column you are trying to use for matching does not exist in either new_df or heat_df.

    Returns:
        Two DataFrames: first DataFrame is matched data, second is remaining data for onward matching.
    """
    
    # Checks before function starts
    if not isinstance(unmatched_df, pd.DataFrame) or not isinstance(heat_df, pd.DataFrame):
        raise TypeError("new_df and heat_df must be pandas DataFrames.")
    # Check cols exist
    for col in left_join_cols:
        if col not in unmatched_df.columns:
            raise ColumnDoesNotExistError(f"'{col}' not found in new_df")
    for col in right_join_cols:
        if col not in heat_df.columns:
            raise ColumnDoesNotExistError(f"'{col}' not found in heat_df")
    if student_heat_id_col not in heat_df.columns:
        raise ColumnDoesNotExistError(f"Specified ID column '{student_heat_id_col}' not found in heat_df.")
    
    # For performance, heat_df should just be columns required for match + heat ID
    heat_cols = list(right_join_cols)
    heat_cols_list = heat_cols + [student_heat_id_col]
    heat_df_slim = heat_df[heat_cols_list]

    # Initial slim merge using only data req. for match
    joined_df = pd.merge(
        unmatched_df,
        heat_df_slim,
        left_on=left_join_cols,
        right_on=right_join_cols,
        how="left",
        suffixes=("", "_match"),
    )

    # Separate matches and non-matches
    final_matched = joined_df.dropna(subset=[student_heat_id_col]).copy().reset_index(drop=True)
    final_matched["Match Type"] = match_type_desc

    unmatched = joined_df[joined_df[student_heat_id_col].isnull()].copy().reset_index(drop=True)
    unmatched = unmatched[unmatched_df.columns]

    # Reporting to terminal
    total_new = len(unmatched_df)
    total_unmatched = len(unmatched)
    students_matched_count = total_new - total_unmatched
    has_duplicates = len(final_matched) > students_matched_count
    print(f"   Attempting match: {match_type_desc}:")
    print(f"     ...{students_matched_count} students found in HEAT data")
    print(f"     ...{len(unmatched)} students left to find.")
    if has_duplicates:
        diff = len(final_matched) - students_matched_count
        print(f"     WARNING: {diff} extra record(s) created. Some student matched to multiple HEAT records. Check HEAT data for duplicates.")

    if verify:
        rename_dict = {col : f"HEAT: {col}" for col in heat_df.columns if col != student_heat_id_col}
        heat_df_verif = heat_df.rename(columns=rename_dict)
        final_matched_check = pd.merge(final_matched, heat_df_verif, how='left', on=student_heat_id_col)
        return final_matched_check, unmatched
    else:
        cols_list = unmatched_df.columns
        cols_list = list(cols_list)
        cols_list.extend([student_heat_id_col, "Match Type"])
        final_matched = final_matched[cols_list]
        return final_matched, unmatched



def perform_fuzzy_match(
    unmatched_df: pd.DataFrame,
    heat_df: pd.DataFrame,
    left_filter_cols: list[str],
    right_filter_cols: list[str],
    left_name_col: str,
    right_name_col: str,
    match_desc: str,
    threshold: int = 80
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """This function allows you to fuzzy match names of students in an external dataset to your HEAT Student Export to retrieve HEAT Student IDs. 
    You can control the potential pool of fuzzy matches by specifying filter columns in both DataFrames e.g. only look for fuzzy matches where Date of Birth matches. 

    Args:
        unmatched_df (pd.DataFrame): The DataFrame of students you want to fuzzy match.
        heat_df (pd.DataFrame): The DataFrame containing your HEAT Student Export.
        left_filter_cols: Filter columns in unmatched_df. By specifying a column here it will be used to control the pool of possible fuzzy matches. For example, by setting Date of birth and postcode here, it will only fuzzy match 'Jo Smith' to 'Joanne Smith' if both records have the same date of birth and postcode.
        right_filter_cols: Corresponding filter columns in heat_df. Must match those set in left_filter_cols.
        left_name_col: Column which contains the name information (to be matched) in unmatched_df.
        right_name_col: Column which contains the name information in heat_df. 
        match_desc: A description of the match; added to a 'Match Type' col in the returned matched DataFrame. Should be descriptive to help you verify matches later, especially if joining multiple returns of this function and exporting to a .csv or Excel file.
        threshold (optional): The acceptable percentage match for fuzzy matching. Higher is stricter and matches will be more similar. Defaults to 80.

    Raises:
        TypeError: Raised if unmatched_df or heat_df are not pandas DataFrames.
        ColumnDoesNotExistError: Raised if columns specified as filters or name columns do not exist in their DataFrames.
        FilterColumnMismatchError: Raised if unequal number of columns specified in left and right filters.
        FuzzyMatchIndexError: Raised when unmatched_df does not have a unique index and cannot be used for matching.

    Returns:
        Two DataFrames: first DataFrame is matched data, second is remaining data for onward matching.
    """
    # Type checking and error handling:
    if not isinstance(unmatched_df, pd.DataFrame) or not isinstance(heat_df, pd.DataFrame):
        raise TypeError("unmatched_df and heat_df must be pandas DataFrames.")
    # Check cols exist
    for col in left_filter_cols:
        if col not in unmatched_df.columns:
            raise ColumnDoesNotExistError(f"'{col}' not found in unmatched_df")
    for col in right_filter_cols:
        if col not in heat_df.columns:
            raise ColumnDoesNotExistError(f"'{col}' not found in heat_df")
    if left_name_col not in unmatched_df.columns:
            raise ColumnDoesNotExistError(f"'{left_name_col}' not found in unmatched_df")
    if right_name_col not in heat_df.columns:
            raise ColumnDoesNotExistError(f"'{right_name_col}' not found in heat_df")
    # Check filter cols are same length
    if len(left_filter_cols) != len(right_filter_cols):
        raise FilterColumnMismatchError("left_filter_cols and right_filter_cols must have the same length for mapping.")
    # Check unmatched has a unique index
    if not unmatched_df.index.is_unique:
        raise FuzzyMatchIndexError(f"unmatched_df")

    # Warning about column collisions
    collision_cols = [c for c in unmatched_df.columns if c.endswith("_HEAT")]
    
    if collision_cols:
        print(f"WARNING: The input unmatched_df contains columns that already end in '_HEAT': {collision_cols}. These will be renamed to 'HEAT: ...' in the final output and may be indistinguishable from actual data retrieved from the HEAT database.")

    print(f"Attempting fuzzy match where {left_filter_cols} match HEAT data.")
    # 1. Create the blocks: Group heat_df by the filter columns
    # We create a dictionary where keys are the filter values and values are indices
    grouped_heat = heat_df.groupby(right_filter_cols).groups
    
    matched_results = []
    
    # 2. Iterate through the unmatched data
    for idx, row in unmatched_df.iterrows():
        # Create a key from the current row's filter columns
        # Handle potential NaNs by converting to a tuple
        search_key = tuple(row[left_filter_cols])
        
        # 3. Quick Lookup: Does this block exist in the Heat data?
        if search_key in grouped_heat:
            # Get the indices of the rows in the Heat data that match this block
            potential_match_indices = grouped_heat[search_key]
            potential_matches = heat_df.loc[potential_match_indices]
            
            # 4. Fuzzy Match only within this specific block
            choices = potential_matches[right_name_col].to_dict() # {index: name}
            
            best_match = process.extractOne(
                query=row[left_name_col],
                choices=choices,
                scorer=fuzz.token_sort_ratio,
                score_cutoff=threshold
            )
            
            if best_match:
                name, score, heat_idx = best_match
                # Reconstruct the row
                res = pd.concat([row, heat_df.loc[heat_idx].add_suffix("_HEAT")])
                res['Fuzzy Score'] = round(score, 2)
                res['Match Type'] = match_desc
                matched_results.append(res)

    # Create matches df and rename cols to match output of exact_match if verify = True
    final_matches = pd.DataFrame(matched_results)
    if not final_matches.empty:
        heat_cols = [c for c in final_matches.columns if c.endswith("_HEAT")]
        mapping = {col: f"HEAT: {col.removesuffix('_HEAT')}" for col in heat_cols}
        final_matches.rename(columns=mapping, inplace=True)
        final_matches.sort_values(
            by="Fuzzy Score",
            ascending=False,
            inplace=True,
            ignore_index=True,
        )
        print(f"     ...{len(final_matches)} students found in HEAT data.")
    else:
        print("     ...0 students found in HEAT data.")
    # Identify who is still missing
    matched_indices = [res.name for res in matched_results] if matched_results else []
    remaining_unmatched = unmatched_df.drop(matched_indices)
    print(f"     ...{len(remaining_unmatched)} students left to find.")
    return final_matches, remaining_unmatched