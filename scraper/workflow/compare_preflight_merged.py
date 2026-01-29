# Decision making based on preflight and hashes of existing data.

import json
from pathlib import Path

PREFLIGHT_HASHES = Path("artifacts/preflight-hashes.json") # From preflight
MERGED_DATA_PKL = Path("../data/merged_data.pkl") # From Git
OUTPUT = Path("datasets_to_process.json")

def main():
    if not PREFLIGHT_HASHES.exists():
        raise FileNotFoundError("preflight-hashes.json not found")

    if not MERGED_DATA_PKL.exists():
        raise FileNotFoundError("processed-hashes.json not found")

    # Load full JSON objects (NOT jsonl)
    # preflight = json.loads(PREFLIGHT_HASHES.read_text(encoding="utf-8"))
    # processed = json.loads(PROCESSED_HASHES.read_text(encoding="utf-8"))

    # to_process = {}

    # for dataset_id, hash_new in preflight.items():
    #     hash_old = processed.get(dataset_id)

    #     if hash_old is None:
    #         to_process[dataset_id] = "new"
    #     elif hash_old != hash_new:
    #         to_process[dataset_id] = "updated"

    # OUTPUT.write_text(
    #     json.dumps(to_process, indent=2, ensure_ascii=False),
    #     encoding="utf-8",
    # )

    # print(f"Datasets to process: {len(to_process)}")


if __name__ == "__main__":
    main()