import pandas as pd
from rapidfuzz import process, fuzz

from heat_helper.exceptions import (
    ColumnDoesNotExistError,
    FuzzyMatchIndexError,
    FilterColumnMismatchError,
)
from heat_helper.dates import calculate_dob_range_from_year_group
from heat_helper.core import CURRENT_ACADEMIC_YEAR_START, STUDENT_HEAT_ID


def perform_exact_match(
    unmatched_df: pd.DataFrame,
    heat_df: pd.DataFrame,
    left_join_cols: list[str],
    right_join_cols: list[str],
    match_desc: str,
    verify: bool = False,
    heat_id_col: str = STUDENT_HEAT_ID,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Performs an exact match on specified columns between new data and your HEAT Student export and returns the HEAT Student ID if a match is found.
    This function returns two DataFrames: one containing the matches and one containing unmatched students, for passing to another matching function.
    This is useful to create a matching waterfall where you move through different levels of strictness.


    Args:
        unmatched_df: The DataFrame containing the students you want to search for.
        heat_df: The DataFrame containing your HEAT Student Export.
        left_join_cols: Columns in new_df you want to match on.
        right_join_cols: Columns in heat_df you want to match on.
        match_desc: A description of the match; added to a 'Match Type' col in the returned matched DataFrame. Should be descriptive to help you verify matches later, especially if joining multiple returns of this function and exporting to a .csv or Excel file.
        verify (optional): Defaults to False. Controls whether to return all columns from heat_df to the matched DataFrame for verifying of matches. Useful if you are performing a less exact match and you want to verify the returned students. Also useful if you are using this function or perform_fuzzy_match function and want to join results together (column structure will be the same).
        heat_id_col (optional): Defaults to 'Student HEAT ID'. Use this if the column in your HEAT Export with the Student ID in is not called 'Student HEAT ID'.

    Raises:
        TypeError: Raised if new_df or heat_df are not pandas DataFrames.
        ColumnDoesNotExistError: Raised if a column you are trying to use for matching does not exist in either new_df or heat_df.

    Returns:
        Two DataFrames: first DataFrame is matched data, second is remaining data for onward matching.
    """

    # Checks before function starts
    if not isinstance(unmatched_df, pd.DataFrame) or not isinstance(
        heat_df, pd.DataFrame
    ):
        raise TypeError("new_df and heat_df must be pandas DataFrames.")
    # Check cols exist
    for col in left_join_cols:
        if col not in unmatched_df.columns:
            raise ColumnDoesNotExistError(f"'{col}' not found in new_df")
    for col in right_join_cols:
        if col not in heat_df.columns:
            raise ColumnDoesNotExistError(f"'{col}' not found in heat_df")
    if heat_id_col not in heat_df.columns:
        raise ColumnDoesNotExistError(
            f"Specified ID column '{heat_id_col}' not found in heat_df."
        )

    if unmatched_df.empty:
        print(
            f"WARNING: skipping match type: {match_desc} - no students left to match."
        )
        return pd.DataFrame(), unmatched_df
    else:
        # For performance, heat_df should just be columns required for match + heat ID
        heat_cols = list(right_join_cols)
        heat_cols_list = heat_cols + [heat_id_col]
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
        final_matched = (
            joined_df.dropna(subset=[heat_id_col]).copy().reset_index(drop=True)
        )
        final_matched["Match Type"] = match_desc

        unmatched = (
            joined_df[joined_df[heat_id_col].isnull()].copy().reset_index(drop=True)
        )
        unmatched = unmatched[unmatched_df.columns]

        # Reporting to terminal
        total_new = len(unmatched_df)
        total_unmatched = len(unmatched)
        students_matched_count = total_new - total_unmatched
        has_duplicates = len(final_matched) > students_matched_count
        print(f"   Attempting to match {total_new} students. Match type: {match_desc}.")
        print(f"     ...{students_matched_count} students found in HEAT data")
        print(f"     ...{len(unmatched)} students left to find.")
        if has_duplicates:
            diff = len(final_matched) - students_matched_count
            print(
                f"     WARNING: {diff} extra record(s) created. Some student matched to multiple HEAT records. Check HEAT data for duplicates."
            )

        if verify:
            rename_dict = {
                col: f"HEAT: {col}" for col in heat_df.columns if col != heat_id_col
            }
            heat_df_verif = heat_df.rename(columns=rename_dict)
            final_matched_check = pd.merge(
                final_matched, heat_df_verif, how="left", on=heat_id_col
            )
            final_matched_check = final_matched_check.rename(
                columns={heat_id_col: f"HEAT: {heat_id_col}"}
            )
            return final_matched_check, unmatched
        else:
            cols_list = unmatched_df.columns
            cols_list = list(cols_list)
            cols_list.extend(["Match Type", heat_id_col])
            final_matched = final_matched[cols_list]
            final_matched = final_matched.rename(
                columns={heat_id_col: f"HEAT: {heat_id_col}"}
            )
            return final_matched, unmatched


def perform_fuzzy_match(
    unmatched_df: pd.DataFrame,
    heat_df: pd.DataFrame,
    left_filter_cols: list[str],
    right_filter_cols: list[str],
    left_name_col: str,
    right_name_col: str,
    match_desc: str,
    threshold: int = 80,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """This function allows you to fuzzy match names of students in an external dataset to your HEAT Student Export to retrieve HEAT Student IDs.
    You can control the potential pool of fuzzy matches by specifying filter columns in both DataFrames e.g. only look for fuzzy matches where Date of Birth and Postcode matches.

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
    if not isinstance(unmatched_df, pd.DataFrame) or not isinstance(
        heat_df, pd.DataFrame
    ):
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
        raise FilterColumnMismatchError(
            "left_filter_cols and right_filter_cols must have the same length for mapping."
        )
    # Check unmatched has a unique index
    if not unmatched_df.index.is_unique:
        raise FuzzyMatchIndexError("unmatched_df")

    # Warning about column collisions
    collision_cols = [c for c in unmatched_df.columns if c.endswith("_HEAT")]

    if collision_cols:
        print(
            f"WARNING: The input unmatched_df contains columns that already end in '_HEAT': {collision_cols}. These will be renamed to 'HEAT: ...' in the final output and may be indistinguishable from actual data retrieved from the HEAT database."
        )

    if unmatched_df.empty:
        print(
            f"WARNING: skipping match type: {match_desc} - no students left to match."
        )
        return pd.DataFrame(), unmatched_df
    else:
        print(
            f"     Attempting to match {len(unmatched_df)} students. Fuzzy match type: {match_desc}."
        )

        # Create copies in case slice passed to function
        unmatched_df = unmatched_df.copy()
        heat_df = heat_df.copy()

        # create heat_df blocks for faster matching
        grouped_heat = heat_df.groupby(right_filter_cols).groups

        matched_results = []

        # Go through each row in unmatched data
        for idx, row in unmatched_df.iterrows():
            search_values = row[left_filter_cols].tolist()
            search_key = (
                tuple(search_values) if len(search_values) > 1 else search_values[0]
            )

            # Does this block exist in the Heat data?
            if search_key in grouped_heat:
                # Get the indices of the rows in the Heat data that match this block
                potential_match_indices = grouped_heat[search_key]
                potential_matches = heat_df.loc[potential_match_indices]

                # Fuzzy Match only within this specific block
                choices = potential_matches[right_name_col].to_dict()  # {index: name}

                best_match = process.extractOne(
                    query=row[left_name_col],
                    choices=choices,
                    scorer=fuzz.token_sort_ratio,
                    score_cutoff=threshold,
                )

                if best_match:
                    name, score, heat_idx = best_match
                    # Reconstruct the row
                    res = pd.concat([row, heat_df.loc[heat_idx].add_suffix("_HEAT")])
                    res["Fuzzy Score"] = round(score, 2)
                    res["Match Type"] = match_desc
                    res["__SOURCE_INDEX__"] = idx
                    matched_results.append(res)

        # final_matches processing
        final_matches = pd.DataFrame(matched_results)
        if not final_matches.empty:
            final_matches.sort_values(
                by="Fuzzy Score", ascending=False, inplace=True, ignore_index=True
            )

            # Rename HEAT columns
            heat_cols = [c for c in final_matches.columns if c.endswith("_HEAT")]
            mapping = {col: f"HEAT: {col.removesuffix('_HEAT')}" for col in heat_cols}
            final_matches.rename(columns=mapping, inplace=True)

            # Sort out indices for dropping
            matched_indices = final_matches["__SOURCE_INDEX__"].tolist()
            final_matches.drop(columns=["__SOURCE_INDEX__"], inplace=True)

            print(f"     ...{len(final_matches)} students found in HEAT data.")
        else:
            matched_indices = []
            print("     ...0 students found in HEAT data.")

        # Identify who is still missing
        remaining_unmatched = unmatched_df.drop(matched_indices)
        print(f"     ...{len(remaining_unmatched)} students left to find.")
        return final_matches, remaining_unmatched


def perform_school_age_range_fuzzy_match(
    unmatched_df: pd.DataFrame,
    heat_df: pd.DataFrame,
    unmatched_school_col: str,
    heat_school_col: str,
    unmatched_name_col: str,
    heat_name_col: str,
    unmatched_year_group_col: str,
    heat_dob_col: str,
    match_desc: str,
    heat_id_col: str = STUDENT_HEAT_ID,
    academic_year_start: int = CURRENT_ACADEMIC_YEAR_START,
    threshold: int = 80,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """This function attempts to fuzzy match the names of students to your HEAT data.
    To control the pool of fuzzy matches, data is first matched on school name, and then uses year group to only return students with a date of birth in range for that year group.
    Useful if you do not know a student's date of birth, but you do know which school they attend and their year group.
    Returns one dataframe of matches and one dataframe of remaining unmatched data.

    Args:
        unmatched_df: DataFrame containing student records you wish to fuzzy match to HEAT records.
        heat_df: DataFrame containing HEAT Student Export.
        unmatched_school_col: Column which contains School name in unmatched_df.
        heat_school_col: Column which contains school name in heat_df.
        unmatched_name_col: Column which contains Student name in unmatched_df.
        heat_name_col: Column which contains Student name in heat_df.
        unmatched_year_group_col: Column in unmatched_df which contains year group for age range calculation.
        heat_dob_col: Column in heat_df which contains Student Date of Birth.
        match_desc: A description of the match; added to a 'Match Type' col in the returned matched DataFrame. Should be descriptive to help you verify matches later, especially if joining multiple returns of this function and exporting to a .csv or Excel file.
        heat_id_col (optional): Column in heat_df which contains HEAT Student ID. Defaults to 'Student HEAT ID'.
        academic_year_start (optional): . Defaults to start of current academic year (calculated by package).
        threshold (optional): The acceptable percentage match for fuzzy matching. Higher is stricter and matches will be more similar. Defaults to 80.

    Raises:
        TypeError: Raised if unmatched_df or heat_df are not pandas DataFrames or if heat_dob_col is not in pandas Datetime format (will try to convert first.)
        ColumnDoesNotExistError: Raised if any specified column does not exist in its dataframe.
        FuzzyMatchIndexError: Raised if unmatched_df does not have unique index.

    Returns:
        Two DataFrames: first DataFrame is matched data, second is remaining data for onward matching.
    """
    # Type checking and error handling:
    if not isinstance(unmatched_df, pd.DataFrame) or not isinstance(
        heat_df, pd.DataFrame
    ):
        raise TypeError("unmatched_df and heat_df must be pandas DataFrames.")
    if not pd.api.types.is_datetime64_any_dtype(heat_df[heat_dob_col]):
        try:
            heat_df[heat_dob_col] = pd.to_datetime(heat_df[heat_dob_col]).dt.normalize()
            print(f"Note: Converted '{heat_dob_col}' to datetime format automatically.")
        except Exception:
            raise TypeError(
                f"'{heat_dob_col}' is not datetime and could not be converted."
            )
    # Check cols exist
    for col in [unmatched_school_col, unmatched_name_col, unmatched_year_group_col]:
        if col not in unmatched_df.columns:
            raise ColumnDoesNotExistError(f"'{col}' not found in unmatched_df")
    for col in [heat_name_col, heat_school_col, heat_dob_col]:
        if col not in heat_df.columns:
            raise ColumnDoesNotExistError(f"'{col}' not found in heat_df")

    # Check unmatched has a unique index
    if not unmatched_df.index.is_unique:
        raise FuzzyMatchIndexError("unmatched_df")

    # Copy originals in case df slice passed to this function; tidy up school names to improve matching
    unmatched_df = unmatched_df.copy()
    heat_df = heat_df.copy()

    heat_df[heat_school_col] = (
        heat_df[heat_school_col]
        .astype(str)
        .str.title()
        .str.strip()
        .replace(r"\s+", " ", regex=True)
    )
    unmatched_df[unmatched_school_col] = (
        unmatched_df[unmatched_school_col]
        .astype(str)
        .str.title()
        .str.strip()
        .replace(r"\s+", " ", regex=True)
    )

    # Create blocks on school in heat_df for quicker matching
    grouped_heat = heat_df.groupby(heat_school_col).groups

    matched_results = []

    # Go through each unmatched row
    for idx, row in unmatched_df.iterrows():
        school_key = row[unmatched_school_col]
        year_group = row[unmatched_year_group_col]

        # Calculate the DOB range for this specific student's year group
        try:
            dob_range = calculate_dob_range_from_year_group(
                year_group, academic_year_start
            )
        except Exception:
            continue

        if not dob_range or school_key not in grouped_heat:
            continue

        start_date, end_date = dob_range

        # Filter the School Block by Age
        # Get only the HEAT records for this school
        potential_matches = heat_df.loc[grouped_heat[school_key]]

        # Further narrow down by Date of Birth (Age Match)
        age_mask = (potential_matches[heat_dob_col].dt.date >= start_date) & (
            potential_matches[heat_dob_col].dt.date <= end_date
        )
        final_potentials = potential_matches[age_mask]

        if not final_potentials.empty:
            # Fuzzy Match names within the filtered school/age block
            choices = final_potentials[heat_name_col].to_dict()

            best_match = process.extractOne(
                query=row[unmatched_name_col],
                choices=choices,
                scorer=fuzz.token_sort_ratio,
                score_cutoff=threshold,
            )

            if best_match:
                name, score, heat_idx = best_match
                # Reconstruct row
                res = pd.concat([row, heat_df.loc[heat_idx].add_suffix("_HEAT")])
                res["Fuzzy Score"] = round(score, 2)
                res["Match Type"] = match_desc
                res["__SOURCE_INDEX__"] = idx
                matched_results.append(res)

    # Sorting, renaming and tidying
    final_matches = pd.DataFrame(matched_results)

    if not final_matches.empty:
        final_matches.sort_values(
            by="Fuzzy Score", ascending=False, inplace=True, ignore_index=True
        )

        heat_student_id_col = f"{heat_id_col}_HEAT"

        initial_count = len(final_matches)
        final_matches = final_matches.drop_duplicates(
            subset=[heat_student_id_col], keep="first"
        )
        conflicts_removed = initial_count - len(final_matches)

        if conflicts_removed > 0:
            print(
                f"     ...Removed {conflicts_removed} duplicate HEAT ID assignments (kept highest scores)."
            )

        # Rename HEAT columns
        heat_cols = [c for c in final_matches.columns if c.endswith("_HEAT")]
        mapping = {col: f"HEAT: {col.removesuffix('_HEAT')}" for col in heat_cols}
        final_matches.rename(columns=mapping, inplace=True)

        # Sort out indices for dropping
        matched_indices = final_matches["__SOURCE_INDEX__"].tolist()
        final_matches.drop(columns=["__SOURCE_INDEX__"], inplace=True)

        print(f"     ...{len(final_matches)} school/age fuzzy matches found.")
    else:
        matched_indices = []
        print("     ...0 matches found.")

    remaining_unmatched = unmatched_df.drop(matched_indices)

    return final_matches, remaining_unmatched
