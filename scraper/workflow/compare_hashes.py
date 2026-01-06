# Decision making based on preflight and hashes of existing data.

import json
from pathlib import Path

# PREFLIGHT_HASHES = Path("preflight-hashes.jsonl") # From the preflight #TODO
PREFLIGHT_HASHES = Path("temp_preflight-hashes.json") # From existing data
# PROCESSED_HASHES = Path("processed-hashes.json") # From existing data #TODO - Read from repo!
PROCESSED_HASHES = Path("data/temp_processed-hashes.json") # From existing data
OUTPUT = Path("datasets_to_process.json")


def load_preflight():
    results = {}
    with PREFLIGHT_HASHES.open("r", encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            if not row.get("reachable"):
                continue

            dataset_id = f"{row['provider']}:{row['layer_name']}"
            results[dataset_id] = row.get("hash_new")
    return results


def main():
    preflight = load_preflight()
    processed = json.loads(PROCESSED_HASHES.read_text(encoding="utf-8"))

    to_process = {}

    for dataset_id, hash_new in preflight.items():
        hash_old = processed.get(dataset_id)

        if hash_old is None:
            to_process[dataset_id] = "new"
        elif hash_old != hash_new:
            to_process[dataset_id] = "updated"

    OUTPUT.write_text(
        json.dumps(to_process, indent=2),
        encoding="utf-8"
    )

    print(f"Datasets to process: {len(to_process)}")


if __name__ == "__main__":
    main()
