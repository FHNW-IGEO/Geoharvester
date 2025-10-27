import os
import pickle
import pandas as pd
import langid
from tqdm import tqdm
from geocat.error_logger import log_error

langid.set_languages(['en', 'fr', 'de', 'it'])


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
# LANGUAGE CORRECTION LOGIC (unchanged)
# -------------------------------------------------------------------

def process_language_status(df, prefixes, table_set_type):
    EMPTY_VALUES = {"", "nan", "none", "null"}

    def is_empty(val):
        return pd.isna(val) or str(val).strip().lower() in EMPTY_VALUES

    for lang in prefixes:
        title_col = f"{table_set_type.lower()}_title_{lang.lower()}"
        keyword_col = f"{table_set_type.lower()}_keyword_{lang.lower()}"
        desc_col = f"{table_set_type.lower()}_description_{lang.lower()}"
        status_col = f"language_status_{lang.lower()}"

        def check_status(row):
            title_val = row.get(title_col)
            keyword_val = row.get(keyword_col)
            desc_val = row.get(desc_col)
            if all(is_empty(val) for val in [title_val, keyword_val, desc_val]):
                return "no_data"
            if all(is_empty(val) for val in [title_val, desc_val]) and not is_empty(keyword_val):
                return "only_keywords"
            return None

        df[status_col] = df.apply(check_status, axis=1)
    return df


def detect_preferred_language(text, language_prefixes):
    language_prefixes = [lang.lower() for lang in language_prefixes]
    try:
        lang, prob = langid.classify(str(text))
        if lang in language_prefixes:
            return lang, round(prob, 3)
        else:
            return ['not_found'], 0.0
    except Exception:
        return ['not_found'], 0.0


def evaluate_text_lengths(df, language_prefixes, min_length_lang_detect, table_set_type):
    for lang in language_prefixes:
        lang = lang.lower()
        title_col = f"{table_set_type.lower()}_title_{lang}"
        desc_col = f"{table_set_type.lower()}_description_{lang}"
        flag_col = f"text_length_flag_{lang}"
        status_col = f"language_status_{lang}"

        def assess_length(row):
            title = str(row[title_col]) if pd.notna(row[title_col]) else ""
            desc = str(row[desc_col]) if pd.notna(row[desc_col]) else ""
            title_long = len(title.strip()) > min_length_lang_detect
            desc_long = len(desc.strip()) > min_length_lang_detect
            if title_long and desc_long:
                return "title_and_description_long"
            elif desc_long:
                return "description_long"
            elif title_long:
                return "title_long"
            else:
                return "neither_long"

        df[flag_col] = df.apply(assess_length, axis=1)

        def validate_language(row):
            if row[flag_col] == "neither_long":
                return row.get(status_col, None)
            text_parts = []
            if row[flag_col] in ["title_and_description_long", "title_long"]:
                text_parts.append(str(row[title_col]))
            if row[flag_col] in ["title_and_description_long", "description_long"]:
                text_parts.append(str(row[desc_col]))
            combined_text = " ".join(text_parts)
            detected_lang, detected_prob = detect_preferred_language(combined_text, language_prefixes)
            if detected_lang == lang:
                return "correct"
            else:
                return f"incorrect_new_{detected_lang}"

        df[status_col] = df.apply(validate_language, axis=1)
    return df


def relocate_incorrect_text(df, language_prefixes, table_set_type):
    for lang in language_prefixes:
        lang = lang.lower()
        status_col = f"language_status_{lang.lower()}"
        title_col = f"{table_set_type.lower()}_title_{lang.lower()}"
        desc_col = f"{table_set_type.lower()}_description_{lang.lower()}"
        for idx, row in df.iterrows():
            status = row[status_col]
            if status and status.startswith("incorrect_new_"):
                target_lang = status.replace("incorrect_new_", "")
                new_title_col = f"{table_set_type.lower()}_title_{target_lang}"
                new_desc_col = f"{table_set_type.lower()}_description_{target_lang}"
                if pd.isna(row.get(new_title_col)) or not str(row.get(new_title_col)).strip():
                    df.at[idx, new_title_col] = row[title_col]
                    df.at[idx, new_desc_col] = row[desc_col]
                df.at[idx, title_col] = None
                df.at[idx, desc_col] = None
    return df


def add_language_quality(df):
    df["language_quality"] = None
    return df


def set_language_quality(df, language_prefixes):
    def determine_quality(row):
        current_quality = row.get("language_quality", None)
        if current_quality == "identical_description":
            return current_quality
        for lang in language_prefixes:
            status = row.get(f"language_status_{lang.lower()}", "")
            if status and status.startswith("incorrect"):
                return "incorrect"
        return "correct"
    df["language_quality"] = df.apply(determine_quality, axis=1)
    return df


def check_identical_descriptions(df, prefixes, table_set_type):
    desc_cols = [f"{table_set_type.lower()}_description_{lang.lower()}" for lang in prefixes]
    def has_identical_descriptions(row):
        descriptions = [str(row[col]).strip().lower() for col in desc_cols if pd.notnull(row[col]) and str(row[col]).strip()]
        seen = {}
        for desc in descriptions:
            if desc in seen:
                return True
            seen[desc] = True
        return False
    df["language_quality"] = df.apply(
        lambda row: "identical_description" if has_identical_descriptions(row) else row.get("language_quality", None),
        axis=1
    )
    return df


# -------------------------------------------------------------------
# MAIN LANGUAGE CORRECTION ENTRYPOINT (for pickle DB)
# -------------------------------------------------------------------

def language_correction(base_dir, db_name, table_name, language_prefixes, base_columns, table_set_type, min_length_lang_detect):
    print(f"Loading pickle DB: {db_name}")
    db = load_pickle_db(base_dir, db_name)

    if table_name not in db:
        print(f"Table '{table_name}' not found in pickle DB.")
        return None

    df = db[table_name]
    if df.empty:
        print("No data found in the selected table.")
        return None

    # Run the processing steps
    steps = [
        ("Language processing step 1: Process language status", lambda df: process_language_status(df, language_prefixes, table_set_type)),
        ("Language processing step 2: Add language quality", add_language_quality),
        ("Language processing step 3: Check identical descriptions", lambda df: check_identical_descriptions(df, language_prefixes, table_set_type)),
        ("Language processing step 4: Evaluate text lengths and detect language", lambda df: evaluate_text_lengths(df, language_prefixes, min_length_lang_detect, table_set_type)),
        ("Language processing step 5: Relocate incorrect texts", lambda df: relocate_incorrect_text(df, language_prefixes, table_set_type)),
        ("Language processing step 6: Set overall language quality", lambda df: set_language_quality(df, language_prefixes))
    ]

    for label, func in tqdm(steps, desc="Processing transformations"):
        print(f"→ {label}")
        df = func(df)

    # Save updated table back to pickle DB
    db[table_name] = df
    save_pickle_db(base_dir, db_name, db)

    print(f"✅ Language correction complete for table '{table_name}'.")
    return df
