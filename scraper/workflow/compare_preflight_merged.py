# Decision making based on preflight and hashes of existing data.

import json
from pathlib import Path
import pandas as pd


MERGED_DATA_PKL = Path("data/merged_data.pkl") # From Git
PREFLIGHT_HASHES = Path("../artifacts/preflight-hashes.json") # From preflight - only hash
PREFLIGHT_DIAGNOSTICS = Path("../artifacts/preflight-diagnostics.jsonl") # From preflight - data
OUTPUT = Path("datasets_to_process.json")

def main():

    if not MERGED_DATA_PKL.exists():
        raise FileNotFoundError("merged_data.pkl not found")
    if not PREFLIGHT_HASHES.exists():
        raise FileNotFoundError("preflight-hashes.json not found")
    if not PREFLIGHT_DIAGNOSTICS.exists():
        raise FileNotFoundError("preflight-diagnostics.jsonl not found")


    df = pd.read_pickle(MERGED_DATA_PKL)
    print(f"Loaded {len(df)} rows from merged_data.pkl")

    with open(PREFLIGHT_HASHES, encoding="utf-8") as f:
        preflight_hashes = json.load(f)
    print(f"Loaded {len(preflight_hashes)} preflight hashes")



    diagnostics_by_id = {}
    with open(PREFLIGHT_DIAGNOSTICS, encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            dataset_id = f"{row['provider']}:{row['layer_name']}"
            diagnostics_by_id[dataset_id] = row

    print(f"Loaded {len(diagnostics_by_id)} preflight diagnostics records")


    merged_hashes = {
        f"{str(r.get('provider')).strip()}:{str(r.get('name')).strip()}": r.get("hash")
        for _, r in df.iterrows()
    }

    datasets_to_process = []

    for dataset_id, preflight_hash in preflight_hashes.items():

        diag = diagnostics_by_id.get(dataset_id)
        if not diag:
            # Should never happen, but be defensive
            print(f"⚠️ Missing diagnostics for {dataset_id}, skipping")
            continue

        current_hash = merged_hashes.get(dataset_id)

        needs_processing = (
            current_hash is None or preflight_hash != current_hash
        )

        if not needs_processing:
            continue

        datasets_to_process.append({
            "dataset_id": dataset_id,
            "provider": diag["provider"],
            "layer_name": diag["layer_name"],
            "service_url": diag["service_url"],
            "service_type": diag["service_type"],
            "preflight_hash": preflight_hash,
            "current_hash": current_hash
        })

        # for _, row in df.iterrows():
        #     provider = str(row.get("provider") or "").strip()
        #     name = str(row.get("name") or "").strip()
        #     dataset_id = f"{provider}:{name}"

        #     # Read the existing hash from merged_data.pkl
        #     current_hash = row.get("hash")
        #     if current_hash is None:
        #         needs_processing = True
            
        #     else:
        #         # Compare to preflight hash
        #         preflight_hash = preflight_hashes.get(dataset_id)
        #         needs_processing = preflight_hash != current_hash

        #     if not needs_processing:
        #         continue

        #     diag = diagnostics_by_id.get(dataset_id)
        #     if not diag:
        #         raise KeyError(f"No diagnostics entry for {dataset_id}")

        #     datasets_to_process.append({
        #         "dataset_id": dataset_id,
        #         "provider": provider,
        #         "layer_name": name,
        #         "service_url": diag["service_url"],
        #         "service_type": diag["service_type"],
        #         "preflight_hash": preflight_hashes.get(dataset_id),
        #         "current_hash": current_hash
        #   })

        # Write output JSON for downstream pipeline
        with open(OUTPUT, "w", encoding="utf-8") as f:
            json.dump(datasets_to_process, f, indent=2, ensure_ascii=False)

        print(f"✅ Datasets flagged for processing: {len(datasets_to_process)}")
        print(f"Output written to {OUTPUT}")


if __name__ == "__main__":
    main()