# transform_metadata_geocat.py
"""
Module: transform_metadata_geocat

This module provides tools for transforming and cleaning metadata CSV files exported from geocat.ch.

It includes the following features:
- Normalization of language codes (e.g., 'deu' -> 'de')
- Merging alternate-language columns (e.g., 'dataset_description_GE' into 'dataset_description_DE')
- ISO formatting of date fields
- Cleaning of placeholder values like 'N/A'
- Error logging via a shared logger

Typical usage:
    from transform_metadata_geocat import process_dataset_metadata, clean_csv_file
    process_dataset_metadata("geocat_dataset_metadata.csv")
    clean_csv_file("geocat_distribution_metadata.csv")

You can also run the module as a script to process and clean all expected geocat files:
    python transform_metadata_geocat.py
"""

import pandas as pd
import ast
from datetime import datetime
from geocat.error_logger import log_error, log_start_message

# Language code mappings
language_mapping = {
    "deu": "de",
    "ger": "de",
    "eng": "en",
    "fra": "fr",
    "fre": "fr",
    "ita": "it"
    # Extend with more mappings as needed
}

# Columns to merge from *_GE into *_DE
merge_instructions = [
    ("dataset_description_DE", "dataset_description_GE"),
    ("dataset_title_DE", "dataset_title_GE")
]

# Columns that contain date strings to be formatted
date_columns = ["dataset_issued"]

# Values considered "empty" and to be cleaned
values_to_remove = {"N/A", "[N/A]"}


def parse_language_column(lang_value):
    """Parses and normalizes a language code or list of codes, mapping them to standard short codes."""
    if isinstance(lang_value, str):
        try:
            lang_list = ast.literal_eval(lang_value) if lang_value.startswith("[") else [lang_value]
            return sorted([language_mapping.get(lang, lang) for lang in lang_list])
        except Exception as e:
            log_error("Failed to parse language column", exception=e)
            return lang_value
    return lang_value


def merge_columns(df, target_col, source_col):
    """Merges values from the source column into the target column and drops the source column."""
    try:
        if source_col in df.columns:
            df[target_col] = df[target_col].fillna(df[source_col])
            df.drop(columns=[source_col], inplace=True)
    except Exception as e:
        log_error(f"Failed to merge columns {source_col} into {target_col}", exception=e)


def transform_date(date_str):
    """
    Converts a date string to SQL TIMESTAMP format ('YYYY-MM-DD HH:MM:SS').
    Returns None if empty or invalid.
    """
    try:
        if pd.isna(date_str) or str(date_str).strip() == "":
            return None
        return datetime.fromisoformat(str(date_str)).strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None
    except Exception as e:
        log_error("Failed to transform date", exception=e)
        return None


def clean_value(value):
    """Cleans a cell value by removing 'N/A', parsing lists, and trimming whitespace."""
    try:
        if pd.isna(value) or str(value).strip() in values_to_remove:
            return ""
        parsed_value = ast.literal_eval(value)
        if isinstance(parsed_value, list):
            parsed_value = [item for item in parsed_value if str(item).strip() not in values_to_remove]
            return parsed_value if parsed_value else ""
    except (ValueError, SyntaxError):
        pass
    except Exception as e:
        log_error("Error cleaning value", exception=e)
    return value.strip()


def process_dataset_metadata(file_path):
    """Processes a dataset CSV file by parsing language codes, merging columns, and formatting dates.

    Args:
        file_path (str): Path to the dataset metadata CSV file.
    """
    try:
        df = pd.read_csv(file_path, dtype=str)
        
        # Rename dataset_title to dataset_title_UNKNOWN if it exists
        if "dataset_title" in df.columns:
            df["dataset_title_UNKNOWN"] = df.pop("dataset_title")

        # Rename dataset_description to dataset_description_UNKNOWN if it exists
        if "dataset_description" in df.columns:
            df["dataset_description_UNKNOWN"] = df.pop("dataset_description")

        # Apply language mapping if column exists
        if "dataset_language" in df.columns:
            df["dataset_language"] = df["dataset_language"].apply(parse_language_column)

        # Merge *_GE into *_DE columns
        for target_col, source_col in merge_instructions:
            merge_columns(df, target_col, source_col)

        # Format date columns
        for col in date_columns:
            if col in df.columns:
                df[col] = df[col].apply(transform_date)

        df.to_csv(file_path, index=False)
        print(f"Processed and saved: {file_path}")
        success_message = "Geocat metadata transformation completed successfully."
        log_error(success_message, level="info")
    except Exception as e:
        log_error(f"Failed to process dataset metadata file: {file_path}", exception=e)


def clean_csv_file(file_path):
    """Cleans a CSV file by applying value normalization to each cell.

    Args:
        file_path (str): Path to the CSV file to be cleaned.
    """
    try:
        df = pd.read_csv(file_path, dtype=str)
        df = df.map(clean_value)
        df.to_csv(file_path, index=False)
        print(f"Cleaned values in: {file_path}")
    except Exception as e:
        log_error(f"Failed to clean CSV file: {file_path}", exception=e)


def main():
    """Main function to process and clean all geocat metadata files."""
    dataset_file = "geocat_dataset_metadata.csv"
    other_csv_files = ["geocat_dataset_metadata.csv", "geocat_distribution_metadata.csv", "geocat_contact_point_metadata.csv"]

    print("Processing dataset metadata...")
    process_dataset_metadata(dataset_file)

    print("Cleaning all metadata CSV files...")
    for file in other_csv_files:
        clean_csv_file(file)

    success_message = "Geocat metadata transformation completed successfully."
    print(success_message)
    log_error(success_message, level="info")


if __name__ == "__main__":
    main()
