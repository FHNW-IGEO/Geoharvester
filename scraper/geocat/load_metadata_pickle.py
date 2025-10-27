import os
import pickle
import pandas as pd
from geocat.error_logger import log_error


# -------------------------------------------------------------------
# CONFIG HELPERS
# -------------------------------------------------------------------

def get_db_path(db_name: str, base_dir: str) -> str:
    """Return full path to the pickle DB file."""
    return os.path.join(base_dir, f"{db_name}.pkl")


# -------------------------------------------------------------------
# DATABASE UTILITIES
# -------------------------------------------------------------------

def database_exists(db_name: str, base_dir: str) -> bool:
    """Check if the pickle DB file exists."""
    return os.path.exists(get_db_path(db_name, base_dir))


def create_database(db_name: str, base_dir: str) -> None:
    """Create an empty pickle DB file."""
    db_path = get_db_path(db_name, base_dir)
    os.makedirs(base_dir, exist_ok=True)
    with open(db_path, "wb") as f:
        pickle.dump({}, f)
    log_error(f"Created new pickle DB at {db_path}", "info")


def reset_database(db_name: str, base_dir: str) -> None:
    """Recreate (overwrite) the pickle DB file each time."""
    create_database(db_name, base_dir)
    log_error(f"Reset pickle DB '{db_name}'", "info")


def load_database(db_name: str, base_dir: str) -> dict:
    """Load pickle DB from disk."""
    db_path = get_db_path(db_name, base_dir)
    if not os.path.exists(db_path):
        log_error(f"Pickle DB '{db_name}' not found. Creating new.", "warning")
        create_database(db_name, base_dir)
    with open(db_path, "rb") as f:
        return pickle.load(f)


def save_database(db_name: str, base_dir: str, data: dict) -> None:
    """Save pickle DB to disk."""
    db_path = get_db_path(db_name, base_dir)
    with open(db_path, "wb") as f:
        pickle.dump(data, f)
    log_error(f"Saved pickle DB to {db_path}", "info")


# -------------------------------------------------------------------
# LOAD METADATA
# -------------------------------------------------------------------

def load_metadata(files: list[str], base_dir: str, db_name: str) -> None:
    """
    Load the specified metadata CSV files into a pickle DB.
    Overwrites existing data every time.
    """
    db_data = {}

    try:
        # Map each file to the correct table name
        for f in files:
            file_name = os.path.basename(f).lower()
            if "dataset" in file_name:
                db_data["dataset"] = pd.read_csv(f)
            elif "distribution" in file_name:
                db_data["distribution"] = pd.read_csv(f)
            elif "contact_point" in file_name:
                db_data["contact_point"] = pd.read_csv(f)
            else:
                log_error(f"Unrecognized file type: {f}", "warning")

        # Save DB
        save_database(db_name, base_dir, db_data)
        log_error(f"Metadata successfully loaded into pickle DB '{db_name}'", "info")

    except Exception as e:
        log_error("Failed to load CSV data into pickle DB", "error", exception=e)
