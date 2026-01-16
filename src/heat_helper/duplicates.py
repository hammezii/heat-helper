import pandas as pd
from rapidfuzz import fuzz, process

from heat_helper.exceptions import ColumnDoesNotExistError


def find_duplicates(
    df: pd.DataFrame,
    name_col: str | list[str],
    date_of_birth_col: str,
    postcode_col: str,
    id_col: str = None,
    threshold: int = 80,
    fuzzy_type: str = "permissive",
    twin_protection: bool = True,
) -> pd.DataFrame:
    """Attempts to find duplicate records within one DataFrame. 
    The function looks for exact matches on any columns passed to name_col, date_of_birth_col and postcode_col, 
    and then attempts to fuzzy match names using either date_of_birth_col or date_of_birth_col and postcode_col 
    to create blocks of potential matches. Strictness of duplicate matching can be controlled using threshold 
    (% match for fuzzy name matching), fuzzy type (permission or strict) which pools potential duplicates for matching by
    using either date of birth or date of birth and postcode, and setting twin_protection to True/False. Twin Protection isolates
    first names in potential matches to filter out people with totally different first names. This is not totally failsafe and may
    still return some twins as potential duplicates.

    Args:
        df (pd.DataFrame): The DataFrame contain records to check for duplicates.
        name_col (str | list[str]): The column or list of columns contain names. Pass a list in the order the columns should be joined to create a full name e.g. ['First Name', 'Middle Name', 'Last Name'].
        date_of_birth_col (str): The column containing date of birth.
        postcode_col (str): The column containing postcode.
        id_col (str, optional): If there is already a column in your DataFrame which contains some kind of ID number, set it here. Otherwise, one will be created. Defaults to None.
        threshold (int, optional): The threshold for fuzzy matching. The percentage match of the name. Defaults to 80.
        fuzzy_type (str, optional): Controls whether date_of_birth_col or date_of_birth_col and postcode_col are used to create blocks for fuzzy matching. 'permissive' uses only date_of_birth_col, so will find duplicates with different postcodes. 'strict' uses both columns, so will only return potential duplicates where both date of birth and postcode match. Defaults to "permissive".
        twin_protection (bool, optional): If True, this filters out suspected twins with less similar first names (<65% match) from returned potential duplicates. Defaults to True.

    Raises:
        TypeError: Raised if df is not a DataFrame.
        ValueError: Raised if threshold is not a value between 0 and 100 or if fuzzy_type is not 'strict' or 'permissive'.
        ColumnDoesNotExistError: Raised if any of the columns passed as args are not in df.

    Returns:
        A DataFrame with a column called 'Potential Duplicates' which contains a list of IDs for any potential duplicates found by the function.
    """
    # Error Handling
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"{df} is not a DataFrame")

    if not (0 <= threshold <= 100):
        raise ValueError("Threshold must be an integer between 0 and 100")

    if fuzzy_type not in ["strict", "permissive"]:
        raise ValueError("fuzzy_type must be 'strict' or 'permissive'")
    
    # Check cols exist
    if isinstance(name_col, str):
        if name_col not in df.columns:
            raise ColumnDoesNotExistError(f"'{name_col}' not found in {df} columns")
    else:
        for name in name_col:
            if name not in df.columns:
                raise ColumnDoesNotExistError(f"'{name_col}' not found in {df} columns")
    
    if date_of_birth_col not in df.columns:
            raise ColumnDoesNotExistError(f"'{date_of_birth_col}' not found in {df} columns")
    
    if postcode_col not in df.columns:
            raise ColumnDoesNotExistError(f"'{postcode_col}' not found in {df} columns")

    new_df = df.copy()

    # Set up col list depending on if name_col is a list or single str
    if isinstance(name_col, list):
        new_df["_match_name"] = (
            new_df[name_col].fillna("").astype(str).agg(" ".join, axis=1)
        )
        col_list = name_col + [date_of_birth_col, postcode_col]
    else:
        col_list = [name_col, date_of_birth_col, postcode_col]
        new_df["_match_name"] = new_df[name_col]

    # String Column Cleaning
    for col in col_list:
        if new_df[col].dtype == "object":
            new_df[col] = (
                df[col].str.strip().replace(r"\s+", " ", regex=True).fillna("")
            )

    # Set up ID column if not passed to function
    if id_col is None:
        new_df["Duplicate ID"] = "#" + (pd.Series(range(len(new_df))) + 1).astype(str)
        id_col = "Duplicate ID"

    print("Searching for duplicates...")

    # 1. Exact Matches
    def _format_duplicate_list(group_series):
        # If there is more than one item in the group, it's a duplicate
        if len(group_series) > 1:
            return ", ".join(sorted(group_series))
        return ""
    
    new_df["Potential Duplicates"] = (
        new_df.groupby(col_list)[id_col].transform(_format_duplicate_list).fillna("")
    )

    # 2. Fuzzy Matching
    # We use a custom Union-Find structure to track clusters.
    # parent[x] = y means "x belongs to the same cluster as y"
    parent = {}

    def find_root(i):
        # Recursively find the root representative of ID i
        if parent.setdefault(i, i) != i:
            parent[i] = find_root(parent[i])  # Path compression
        return parent[i]

    def union(i, j):
        # Merge the sets containing i and j
        root_i = find_root(i)
        root_j = find_root(j)
        if root_i != root_j:
            parent[root_i] = root_j

    # A. Register Exact Matches into Union-Find
    # If we already found #1 and #2 are exact matches, union them now.
    has_dupe = new_df[new_df["Potential Duplicates"] != ""]
    for row_ids in has_dupe["Potential Duplicates"]:
        ids_in_group = row_ids.split(", ")
        first_id = ids_in_group[0]
        for other_id in ids_in_group[1:]:
            union(first_id, other_id)

    # B. Run Fuzzy Matching
    if fuzzy_type == "strict":
        blocks = new_df.groupby([date_of_birth_col, postcode_col])
    else:
        blocks = new_df.groupby(date_of_birth_col)

    for _, block_df in blocks:
        if len(block_df) < 2:
            continue

        names = block_df["_match_name"].tolist()
        ids = block_df[id_col].tolist()

        # Calculate similarity matrix
        score_matrix = process.cdist(names, names, scorer=fuzz.token_sort_ratio)

        # Iterate upper triangle to avoid duplicate checks
        for i in range(len(score_matrix)):
            for j in range(i + 1, len(score_matrix)):
                if score_matrix[i][j] >= threshold:
                    if twin_protection:
                        # Split name on first space. 0 = Name before first space
                        name_1 = names[i].split(" ")[0]
                        name_2 = names[j].split(" ")[0]

                        # Compare ONLY the first names
                        first_name_score = fuzz.ratio(name_1, name_2)

                        # If the full strings match, but the first names are clearly different,
                        # assume they are twins (or siblings) and SKIP the union.
                        if (
                            first_name_score < 70
                        ):
                            continue

                    # If fuzzy match found, Union the two IDs
                    union(ids[i], ids[j])

    # --- 5. Final Reconciliation ---
    # Now we simply group all IDs by their "Root Parent"
    # This automatically handles the A->B->C chaining
    clusters = {}
    for i in new_df[id_col]:
        root = find_root(i)
        if root not in clusters:
            clusters[root] = []
        clusters[root].append(i)

    # Convert clusters to string format: "#1, #2, #3"
    # We only care about clusters with size > 1
    id_to_string_map = {}
    for root, members in clusters.items():
        if len(members) > 1:
            member_str = ", ".join(sorted(members))
            for member in members:
                id_to_string_map[member] = member_str

    # Apply the map
    new_df['Potential Duplicates'] = new_df[id_col].map(id_to_string_map).fillna("")

    # Final clean up
    if "_match_name" in new_df.columns:
        new_df.drop(columns=["_match_name"], inplace=True)

    new_df['Potential Duplicates'] = new_df['Potential Duplicates'].replace(
        r"^\s*$", None, regex=True
    )

    new_df = new_df.sort_values(['Potential Duplicates', id_col], ascending=False)

    dupe_count = len(new_df) - new_df['Potential Duplicates'].isna().sum()
    print(f"{dupe_count} records are potential duplicates.")

    return new_df
