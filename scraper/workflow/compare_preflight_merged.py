# Decision making based on preflight and hashes of existing data.

import json
from pathlib import Path
import pandas as pd


MERGED_DATA_PKL = Path("data/merged_data.pkl") # From Git
PREFLIGHT_HASHES = Path("../artifacts/preflight-hashes.json") # From preflight
OUTPUT = Path("datasets_to_process.json")

def main():

    if not MERGED_DATA_PKL.exists():
        raise FileNotFoundError("merged_data.pkl not found")
    if not PREFLIGHT_HASHES.exists():
        raise FileNotFoundError("preflight-hashes.json not found")


    df = pd.read_pickle(MERGED_DATA_PKL)
    print(f"Loaded {len(df)} rows from merged_data.pkl")

    with open(PREFLIGHT_HASHES, encoding="utf-8") as f:
        preflight_hashes = json.load(f)
    print(f"Loaded {len(preflight_hashes)} preflight hashes")


    datasets_to_process = []

    for _, row in df.iterrows():
        provider = str(row.get("provider") or "").strip()
        name = str(row.get("name") or "").strip()
        service_url = str(row.get("service_url") or "").strip()
        dataset_id = f"{provider}:{name}"

        # Read the existing hash from merged_data.pkl
        current_hash = row.get("hash")
        if current_hash is None:
            # Defensive: no hash in pkl
            print(f"⚠️ Missing hash for {dataset_id}, flagging for processing")
            datasets_to_process.append({
                "dataset_id": dataset_id,
                "preflight_hash": None,
                "current_hash": None,
                "service_url": service_url
            })
            continue

        # Compare to preflight hash
        preflight_hash = preflight_hashes.get(dataset_id)
        needs_processing = preflight_hash != current_hash

        if needs_processing:
            datasets_to_process.append({
                "dataset_id": dataset_id,
                "preflight_hash": preflight_hash,
                "current_hash": current_hash,
                "service_url": service_url
            })

    # Write output JSON for downstream pipeline
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(datasets_to_process, f, indent=2, ensure_ascii=False)

    print(f"✅ Datasets flagged for processing: {len(datasets_to_process)}")
    print(f"Output written to {OUTPUT}")


if __name__ == "__main__":
    main()