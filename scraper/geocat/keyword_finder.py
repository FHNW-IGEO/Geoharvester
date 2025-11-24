import os
import pickle
import sys, types
import pandas as pd
import pickle

from tqdm import tqdm
from geocat.error_logger import log_error


# -------------------------------------------------------------------
# PICKLE DATABASE HELPERS
# -------------------------------------------------------------------

def load_pickle_db(base_dir: str, pkl_file: str) -> dict:
    """Load pickle DB into memory with backward compatibility for old pandas pickles."""


    # ------------------------------------------------------------------
    # Compatibility shim for old pandas (<2.0) pickles
    # ------------------------------------------------------------------
    # Some old pickles refer to:  pandas.core.indexes.numeric.Int64Index
    # but pandas 2.x removed this module path.
    try:
        # Only install shim if needed
        if "pandas.core.indexes.numeric" not in sys.modules:
            fake_mod = types.ModuleType("pandas.core.indexes.numeric")

            # Recreate Int64Index class so pandas 2.x can unpickle it
            class Int64Index(pd.Index):
                pass

            fake_mod.Int64Index = Int64Index
            sys.modules["pandas.core.indexes.numeric"] = fake_mod
    except Exception:
        pass

    # ------------------------------------------------------------------
    # Normal loading
    # ------------------------------------------------------------------
    db_path = os.path.join(base_dir, f"{pkl_file}.pkl")
    print(f"Loading pickle DB from {db_path}")

    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Pickle DB not found: {db_path}")

    with open(db_path, "rb") as f:
        return pickle.load(f)


def save_pickle_db(base_dir: str, pkl_file: str, data: dict) -> None:
    """Save updated pickle DB back to disk."""
    db_path = os.path.join(base_dir, f"{pkl_file}.pkl")
    with open(db_path, "wb") as f:
        pickle.dump(data, f)
    log_error(f"Saved updated pickle DB to {db_path}", "info")

# -------------------------------------------------------------------
# PREPROCESSING DATAFRAMES
# -------------------------------------------------------------------


def build_geocat_joined_dataframe(df_geocat: dict) -> pd.DataFrame:
    """
    Build the combined GeoHarvester-style DataFrame from the geocat dictionary.

    Parameters
    ----------
    df_geocat : dict
        Dictionary containing the tables 'dataset', 'distribution', and 'contact_point'.

    Returns
    -------
    pd.DataFrame
        Joined DataFrame with selected and renamed columns.
    """

    # Extract tables
    m = df_geocat["dataset"]
    d = df_geocat["distribution"]
    c = df_geocat["contact_point"]

    # Perform the joins
    database_4M = (
        m.merge(c, on="dataset_identifier", how="left", suffixes=("", "_c"))
         .merge(d, on="dataset_identifier", how="left", suffixes=("", "_d"))
    )

    # Rename overlapping origin/xml_filename columns
    database_4M = database_4M.rename(columns={
        "origin_c": "contact_origin",
        "xml_filename_c": "contact_xml_filename",
        "origin_d": "distribution_origin",
        "xml_filename_d": "distribution_xml_filename"
    })

    # Target columns
    columns = list(m.columns) + [
        "contact_type", "contact_email", "contact_name",
        "contact_origin", "contact_xml_filename",
        "distribution_format", "distribution_access_url",
        "distribution_download_url",
        "distribution_format_name", "distribution_format_type",
        "distribution_license", "distribution_rights",
        "distribution_language", "distribution_id",
        "distribution_origin", "distribution_xml_filename",
        "distribution_description_de", "distribution_description_fr",
        "distribution_description_it", "distribution_description_en",
        "distribution_description_rm"
    ]

    # Only keep columns that exist
    existing_columns = [col for col in columns if col in database_4M.columns]
    database_4M = database_4M[existing_columns]

    return database_4M

def split_by_keywordlist(df_geoharvester: pd.DataFrame, term: str = "wms_ows_keywordlist"):
    """
    Split a GeoHarvester DataFrame into two parts:
    1. Rows whose 'keywords' column contains the term.
    2. Rows whose 'keywords' column does NOT contain the term.

    Returns
    -------
    matches_df : pd.DataFrame
        Rows where the keyword column contains the term.
    non_matches_df : pd.DataFrame
        Rows where the keyword column does NOT contain the term.
    """

    # Ensure string column
    keywords = df_geoharvester["keywords"].astype(str)

    # Mask for term
    mask = keywords.str.contains(term, case=False, na=False)

    # Two opposite subsets
    matches_df = df_geoharvester[mask].copy()
    non_matches_df = df_geoharvester[~mask].copy()

    return matches_df, non_matches_df


# - ------------------------------------------------------------------
# Matching keywords from geocat to geoharvester datasets
# -------------------------------------------------------------------

def fill_missing_geocat_keywords(df_geoharvester_keywords_missing: pd.DataFrame,
                                 database_4M: pd.DataFrame,
                                 dev_limit: int = None) -> pd.DataFrame:
    """
    Match GeoHarvester rows without keywords against database_4M URLs
    and fill geocat_keyword_* fields based on name–URL matching.
    """

    df = df_geoharvester_keywords_missing.copy()

    urls = database_4M["distribution_access_url"].astype(str)
    names = df["name"].astype(str)

    if dev_limit is not None:
        urls = urls.iloc[:dev_limit]

    df["geocat_keyword_de"] = None
    df["geocat_keyword_fr"] = None
    df["geocat_keyword_it"] = None
    df["geocat_keyword_en"] = None

    for url_index, url in tqdm(urls.items(), total=len(urls), desc="Scanning URLs"):
        for name_index, name in names.items():

            if name.strip() and name in url:
                df.at[name_index, "geocat_keyword_de"] = database_4M.at[url_index, "dataset_keyword_de"]
                df.at[name_index, "geocat_keyword_fr"] = database_4M.at[url_index, "dataset_keyword_fr"]
                df.at[name_index, "geocat_keyword_it"] = database_4M.at[url_index, "dataset_keyword_it"]
                df.at[name_index, "geocat_keyword_en"] = database_4M.at[url_index, "dataset_keyword_en"]

    return df

#
# Merge datasets back together
#

def combine_missing_and_existing(df_missing_filled: pd.DataFrame,
                                 df_geoharvester_keywords_not_missing: pd.DataFrame) -> pd.DataFrame:
    """
    Concatenate filled-missing rows with rows that already have keywords.
    """

    full_with_keywords = pd.concat(
        [df_missing_filled, df_geoharvester_keywords_not_missing],
        ignore_index=True
    )

    return full_with_keywords


# -------------------------------------------------------------------
# MAIN KEYWORD FINDER LOGIC
# -------------------------------------------------------------------

def keyword_finder(base_dir_geocat,base_dir_geoharvester, pkl_geocat_data_name, pkl_geoharvester_data_name, pkl_geoharvester_data_name_with_geocat_keywords):
    # Load pickle DBs
    df_geocat = load_pickle_db(base_dir_geocat, pkl_geocat_data_name)
    df_geoharvester = load_pickle_db(base_dir_geoharvester, pkl_geoharvester_data_name)

    # Build joined DataFrame for geocat
    df_geocat = build_geocat_joined_dataframe(df_geocat)

    # Split geoharvester datasets by presence of keywords
    df_geoharvester_keywords_missing, df_geoharvester_keywords_not_missing = split_by_keywordlist(df_geoharvester)

    # Fill missing geocat keywords based on name–URL matching
    df_missing_filled = fill_missing_geocat_keywords(df_geoharvester_keywords_missing,df_geocat,dev_limit=None)

    # Combine back the two parts
    full_df = combine_missing_and_existing(df_missing_filled,df_geoharvester_keywords_not_missing)

    # Save updated pickle DB
    save_pickle_db(base_dir_geoharvester,pkl_geoharvester_data_name_with_geocat_keywords, full_df)

    
    return 