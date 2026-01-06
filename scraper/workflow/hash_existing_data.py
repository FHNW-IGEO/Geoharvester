import json
from pathlib import Path
from datetime import datetime

import pandas as pd

# Use the same method as in preflight, to keep things in sync
from hashing.hashing_method import normalize_then_hash

PICKLE_PATH = Path("data/merged_data.pkl")
OUTPUT_PATH = Path("processed-hashes.json")


def load_dataframe():
    if not PICKLE_PATH.exists():
        raise FileNotFoundError(f"Pickle not found: {PICKLE_PATH}")
    return pd.read_pickle(PICKLE_PATH)


def row_to_hash_entry(row):
    provider = str(row.get("provider", "") or "").strip()
    name = str(row.get("name", "") or "").strip()

    dataset_id = f"{provider}::{name}"

    layer_for_hashing = {
        "title": row.get("title"),
        "name": name,
        "abstract": row.get("abstract"),
        "contact": row.get("contact"),
        "keywords": row.get("keywords"),
    }

    hash_processed = normalize_then_hash(layer_for_hashing)

    return dataset_id, {
        "hash": hash_processed,
        "provider": provider,
        "name": name,
    }


def main():
    df = load_dataframe()

    hashes = {}

    for _, row in df.iterrows():
        provider = str(row.get("provider") or "").strip()
        name = str(row.get("name") or "").strip()

        if not provider or not name:
            continue  # defensive: skip malformed rows

        dataset_id = f"{provider}:{name}"

        layer_for_hashing = {
            "title": row.get("title"),
            "name": name,
            "abstract": row.get("abstract"),
            "contact": row.get("contact"),
            "keywords": row.get("keywords"),
        }

        hashes[dataset_id] = normalize_then_hash(layer_for_hashing)

        OUTPUT_PATH.write_text(
            json.dumps(hashes, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        print(f"✔ Wrote {len(hashes)} processed hashes to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
