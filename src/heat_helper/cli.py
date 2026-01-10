import click
import pandas as pd
import os
import re
from datetime import datetime
from importlib import metadata

# This retrieves the version from the installed package metadata
try:
    __version__ = metadata.version("heat-helper")
except metadata.PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0-dev"  # pragma: no cover


@click.group()
@click.version_option(version=__version__, help="Show the version and exit.")
def main():
    """Heat Helper: Utility for cleaning data for specific database systems."""
    pass


@main.command()
def version():
    """Display the current version of heat_helper."""
    click.echo(f"heat-helper version {__version__}")


@main.command()
@click.argument("file_name", type=click.Path(exists=True))
def describe(file_name):
    """Shows detailed information about a CSV or Excel file.

    This includes file metadata, column naming compliance,
    missing values, and data quality warnings (like whitespace)."""
    try:
        # 1. FILE SYSTEM METADATA
        extension = os.path.splitext(file_name)[1].lower()
        stats = os.stat(file_name)
        last_modified = datetime.fromtimestamp(stats.st_mtime).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        file_size_mb = stats.st_size / (1024 * 1024)

        # 2. LOAD DATA & GET RAW HEADERS
        # We handle loading differently based on extension
        if extension == ".csv":
            with open(file_name, "r", encoding="utf-8", errors="ignore") as f:
                first_line = f.readline().strip()
                raw_headers = [h.strip() for h in first_line.split(",")]
            df = pd.read_csv(file_name)
        elif extension in [".xlsx", ".xls"]:
            # For Excel, we read just the first row for headers to stay consistent
            header_df = pd.read_excel(file_name, nrows=0)
            raw_headers = list(header_df.columns)
            df = pd.read_excel(file_name)
        else:
            click.secho(f"Unsupported file format: {extension}", fg="red")
            return

        click.secho(
            f"\n>>> FILE SUMMARY: {os.path.basename(file_name)}", fg="cyan", bold=True
        )
        click.echo(f"File Type:       {extension}")
        click.echo(f"Last Updated:    {last_modified}")
        click.echo(f"Physical Size:   {file_size_mb:.2f} MB")

        mem_usage = df.memory_usage(deep=True).sum() / 1024**2
        click.echo(f"Memory Footprint: {mem_usage:.2f} MB")
        click.echo(f"Total Columns:    {len(df.columns)}")
        click.echo(f"Total Rows:       {len(df)}")

        # 4. COLUMN NAME CHECKS
        click.secho("\n>>> COLUMN NAME CHECKS", fg="yellow")

        # Check for duplicates using the RAW headers we read earlier
        if len(raw_headers) != len(set(raw_headers)):
            seen = set()
            dupes = [h for h in raw_headers if h in seen or seen.add(h)]
            click.secho(
                f"⚠ CRITICAL: Duplicate headers in raw file: {', '.join(dupes)}",
                fg="red",
                bold=True,
            )
        else:
            click.secho("✓ All column names are unique.", fg="green")

        # 2. Check for "Dirty" names (Brackets, Spaces, Special Chars)
        invalid_char_pattern = re.compile(r"[^a-zA-Z0-9_]")

        dirty_columns = [c for c in raw_headers if invalid_char_pattern.search(c)]

        if dirty_columns:
            if (len(dirty_columns)) > 1:
                name_text = "names"
            else:
                name_text = "name"
            click.secho(
                f"⚠ Warning: {len(dirty_columns)} column {name_text} contain spaces, brackets, or special chars.",
                fg="red",
            )
            click.secho(f"  Suggest cleaning: {', '.join(dirty_columns)}", fg="red")
        else:
            click.secho(
                "✓ Column names are clean (Alphanumeric/Underscores only).", fg="green"
            )

        # 5. DATA QUALITY CHECKS
        click.secho("\n>>> DATA QUALITY SUMMARY", fg="yellow")
        # Added 'Whitespace' to the header
        header = f"{'Column Name':<20} | {'Dtype':<12} | {'Missing':<10} | {'Duplicates':<12} | {'Whitespace':<12} | {'Contains Numbers'}"
        click.echo(header)
        click.echo("-" * len(header))

        for col in df.columns:
            dtype = str(df[col].dtype)
            missing = df[col].isnull().sum()
            dupes_count = df[col].duplicated().sum()

            # Determine Whitespace Warning status
            if df[col].dtype == "object":
                # Check if any non-null cell has leading or trailing space
                has_space = df[col].str.contains(r"^\s|\s$", na=False).any()
                ws_warning = "Yes" if has_space else "No"
                contains_num = df[col].str.contains(r"[0-9]", na=False).any()
                num_warning = "Yes" if contains_num else "No"
            else:
                ws_warning = "N/A"
                num_warning = "N/A"

            # Print the row with the new column
            click.echo(
                f"{col[:20]:<20} | {dtype:<12} | {missing:<10} | {dupes_count:<12} | {ws_warning:<12} | {num_warning}"
            )

    except Exception as e:
        click.secho(f"Error reading file: {e}", fg="red")


if __name__ == "__main__":
    main()  # pragma: no cover
