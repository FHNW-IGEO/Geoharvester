import json
from pathlib import Path
from datetime import datetime

import pandas as pd

# Use the same method as in preflight, to keep things in sync
from hashing.hashing_method import normalize_then_hash

PICKLE_PATH = Path("data/merged_data.pkl")
OUTPUT_PATH = Path("processed-hashes.json")
DUPLICATES_PATH = Path("duplicates.json") 


def load_dataframe():
    if not PICKLE_PATH.exists():
        raise FileNotFoundError(f"Pickle not found: {PICKLE_PATH}")
    return pd.read_pickle(PICKLE_PATH)


def main():
    df = load_dataframe()

    hashes = {} # used for output
    duplicates_info = [] # stores info about duplicates
    seen_hashes = {} # keeps track of processed hashes

    for _, row in df.iterrows():
        provider = str(row.get("provider") or "").strip()
        name = str(row.get("name") or "").strip()

        if not provider or not name:
            continue  # defensive: skip malformed rows

        dataset_id = f"{provider}:{name}"

        if dataset_id in hashes:
            print(f"⚠️ Duplicate dataset_id: {dataset_id} (will overwrite previous entry)")
            duplicates_info.append({
                "type": "duplicate_dataset_id",
                "dataset_id": dataset_id
            })

        layer_for_hashing = {
            "title": row.get("title"),
            "name": name,
            "abstract": row.get("abstract"),
            "contact": row.get("contact"),
            "keywords": row.get("keywords"),
        }

        hash_value = normalize_then_hash(layer_for_hashing)
        hashes[dataset_id] = hash_value

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

        OUTPUT_PATH.write_text(
            json.dumps(hashes, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    print(f"✔ Wrote {len(hashes)} processed hashes to {OUTPUT_PATH}")

    if duplicates_info:
        DUPLICATES_PATH.write_text(
            json.dumps(duplicates_info, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"⚠️ Found {len(duplicates_info)} duplicates, written to {DUPLICATES_PATH}")



if __name__ == "__main__":
    main()
