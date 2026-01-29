import json
from pathlib import Path
from datetime import datetime

import pandas as pd

# Use the same method as in preflight, to keep things in sync
from hashing.hashing_method import normalize_then_hash

PICKLE_PATH = Path("../data/elia_merged_data.pkl")
OUTPUT_PICKLE_PATH = Path("../data/enhanced_merged_data.pkl")
DUPLICATES_PATH = Path("duplicates.json") 


def load_dataframe():
    if not PICKLE_PATH.exists():
        raise FileNotFoundError(f"Pickle not found: {PICKLE_PATH}")
    return pd.read_pickle(PICKLE_PATH)


def main():
    df = load_dataframe()

    duplicates_info = [] # stores info about duplicates
    seen_hashes = {} # keeps track of processed hashes
    seen_dataset_ids = set()

    hashes = []

    for idx, row in df.iterrows():
        provider = str(row.get("provider") or "").strip()
        name = str(row.get("name") or "").strip()

        if not provider or not name:
            hashes.append(None)
            continue

        dataset_id = f"{provider}:{name}"

        if dataset_id in hashes:
            print(f"⚠️ Duplicate dataset_id: {dataset_id} (will overwrite previous entry)")
            duplicates_info.append({
                "type": "duplicate_dataset_id",
                "dataset_id": dataset_id,
                "row_index": idx
            })
        else:
            seen_dataset_ids.add(dataset_id)

        layer_for_hashing = {
            "title": row.get("title"),
            "name": name,
            "abstract": row.get("abstract"),
            "contact": row.get("contact"),
            "keywords": row.get("keywords"),
        }

        hash_value = normalize_then_hash(layer_for_hashing)
        hashes.append(hash_value)

        # Check for duplicates
        if hash_value in seen_hashes:
            print(f"⚠️ Duplicate content: {dataset_id} has same hash as {seen_hashes[hash_value]}")
            duplicates_info.append({
                "type": "duplicate_content",
                "dataset_id": dataset_id,
                "original_dataset_id": seen_hashes[hash_value]
            })
        else:
            seen_hashes[hash_value] = dataset_id

    df["hash"] = hashes

    # Persist updated snapshot
    df.to_pickle(OUTPUT_PICKLE_PATH)
    print(f"✔ Backfilled hash into {OUTPUT_PICKLE_PATH}")
    print(f"✔ Rows processed: {len(df)}")

    if duplicates_info:
        DUPLICATES_PATH.write_text(
            json.dumps(duplicates_info, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"⚠️ Found {len(duplicates_info)} duplicates, written to {DUPLICATES_PATH}")


if __name__ == "__main__":
    main()
