import os
import pickle
import pandas as pd
import langid
from tqdm import tqdm
from geocat.error_logger import log_error

# -------------------------------------------------------------------
# PICKLE DATABASE HELPERS
# -------------------------------------------------------------------

def load_pickle_db(base_dir: str, db_name: str) -> dict:
    """Load pickle DB into memory."""
    db_path = os.path.join(base_dir, f"{db_name}.pkl")
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Pickle DB not found: {db_path}")
    with open(db_path, "rb") as f:
        return pickle.load(f)


def save_pickle_db(base_dir: str, db_name: str, data: dict) -> None:
    """Save updated pickle DB back to disk."""
    db_path = os.path.join(base_dir, f"{db_name}.pkl")
    with open(db_path, "wb") as f:
        pickle.dump(data, f)
    log_error(f"Saved updated pickle DB to {db_path}", "info")


# -------------------------------------------------------------------


key