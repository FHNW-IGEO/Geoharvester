import pandas as pd
from typing import List
import os
from geocat.error_logger import log_error


# ----------------------------------------------------------
# Column definitions
# ----------------------------------------------------------

DATASET_COLUMNS = [
    "dataset_identifier", "origin", "xml_filename", "dataset_language",
    "dataset_title_de", "dataset_keyword_de", "dataset_description_de",
    "dataset_title_unknown", "dataset_keyword_unknown", "dataset_description_unknown",
    "dataset_title_en", "dataset_keyword_en", "dataset_description_en",
    "dataset_keyword_fr", "dataset_title_fr", "dataset_description_fr",
    "dataset_title_it", "dataset_keyword_it", "dataset_description_it",
    "dataset_title_rm", "dataset_keyword_rm", "dataset_description_rm",
    "dataset_publisher_name", "dataset_publisher_url",
    "dataset_spatial", "dataset_theme", "dataset_issued",
    "dataset_is_mobility", "dataset_location_id", "dataset_location",
    "dataset_location_district", "dataset_location_canton", "dataset_location_country",
    "dataset_language_status_de", "dataset_language_status_en",
    "dataset_language_status_fr", "dataset_language_status_it",
    "dataset_language_status_unknown", "dataset_language_quality",
    "dataset_description_length_de", "dataset_description_length_en",
    "dataset_description_length_fr", "dataset_description_length_it",
    "dataset_description_length_rm", "dataset_distribution_format_count",
    "dataset_keyword_count_de", "dataset_keyword_count_en",
    "dataset_keyword_count_fr", "dataset_keyword_count_it",
    "dataset_keyword_count_rm", "dataset_cluster_id"
]


DISTRIBUTION_COLUMNS = [
    "dataset_identifier", "distribution_format", "distribution_access_url",
    "origin", "xml_filename", "distribution_title_de", "distribution_description_de",
    "distribution_title_unknown", "distribution_description_unknown",
    "distribution_title_en", "distribution_description_en",
    "distribution_title_fr", "distribution_description_fr",
    "distribution_title_it", "distribution_description_it",
    "distribution_title_rm", "distribution_description_rm",
    "distribution_media_type", "distribution_language", "distribution_download_url",
    "distribution_coverage", "distribution_temporal_resolution", "distribution_documentation",
    "distribution_id", "distribution_issued_date", "distribution_modified_date",
    "distribution_license", "distribution_rights", "distribution_byte_size",
    "distribution_language_status_de", "distribution_language_status_en",
    "distribution_language_status_fr", "distribution_language_status_it",
    "distribution_language_status_unknown", "distribution_language_quality",
    "distribution_description_length_de", "distribution_description_length_en",
    "distribution_description_length_fr", "distribution_description_length_it",
    "distribution_description_length_rm", "distribution_format_name",
    "distribution_format_type", "distribution_format_cluster",
    "distribution_format_geodata", "distribution_access_url_status_code",
    "distribution_download_url_status_code"
]


CONTACT_POINT_COLUMNS = [
    "dataset_identifier", "contact_type", "contact_email",
    "contact_name", "origin", "xml_filename"
]



# ----------------------------------------------------------
# Apply schema to one CSV file
# ----------------------------------------------------------

def apply_schema(input_file: str, output_file: str, required_columns: List[str]) -> None:
    """Ensure the CSV matches the required schema (columns + order)."""
    try:
        df = pd.read_csv(input_file)
        df.columns = [col.lower() for col in df.columns]

        # Add missing columns
        for col in required_columns:
            if col not in df.columns:
                df[col] = ""

        # Keep only required columns and order them correctly
        df = df[required_columns]

        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        df.to_csv(output_file, index=False)
        log_error(f"Schema applied to {os.path.basename(input_file)}", level="info")
    except Exception as e:
        log_error(f"Failed to apply schema to '{input_file}'", level="error", exception=e)


# ----------------------------------------------------------
# Schema application functions
# ----------------------------------------------------------

def apply_dataset_schema(file_path: str, output_dir: str) -> None:
    output_file = os.path.join(output_dir, "geocat_dataset_metadata.csv")
    apply_schema(file_path, output_file, DATASET_COLUMNS)

def apply_distribution_schema(file_path: str, output_dir: str) -> None:
    output_file = os.path.join(output_dir, "geocat_distribution_metadata.csv")
    apply_schema(file_path, output_file, DISTRIBUTION_COLUMNS)

def apply_contact_point_schema(file_path: str, output_dir: str) -> None:
    output_file = os.path.join(output_dir, "geocat_contact_point_metadata.csv")
    apply_schema(file_path, output_file, CONTACT_POINT_COLUMNS)


# ----------------------------------------------------------
# Apply all schemas
# ----------------------------------------------------------

def apply_schemas(files: List[str], output_dir: str):
    """Apply the correct DB schema to each metadata CSV file."""
    log_error("Start applying schemas", level="info")

    try:
        dataset_file = next(f for f in files if "dataset_metadata" in f)
        apply_dataset_schema(dataset_file, output_dir)
    except Exception as e:
        log_error("Failed to process dataset file", level="error", exception=e)

    try:
        distribution_file = next(f for f in files if "distribution_metadata" in f)
        apply_distribution_schema(distribution_file, output_dir)
    except Exception as e:
        log_error("Failed to process distribution file", level="error", exception=e)

    try:
        contact_file = next(f for f in files if "contact_point_metadata" in f)
        apply_contact_point_schema(contact_file, output_dir)
    except Exception as e:
        log_error("Failed to process contact point file", level="error", exception=e)
