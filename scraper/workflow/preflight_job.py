#!/usr/bin/env python3
import csv
import json
import argparse
from datetime import datetime
from owslib.wms import WebMapService
from owslib.wfs import WebFeatureService
from owslib.wmts import WebMapTileService
from urllib.parse import urlparse, parse_qs
from hashing.hashing_method import normalize_then_hash

def detect_service_type(url: str) -> str | None:
    """Detect OGC service type from URL query parameters"""
    qs = parse_qs(urlparse(url).query)
    service = qs.get("service") or qs.get("SERVICE")
    if not service:
        return None
    return service[0].upper()

def ping_and_parse_service(url, timeout=10):
    """
    Ping OGC service using a real GetCapabilities request.
    Reachable means: server responded to OWSLib handshake.
    """
    layers_data = []

    service_type = detect_service_type(url)
    if not service_type:
        return False, "SERVICE parameter missing", []

    try:
        # --- Reachability check
        if service_type == "WMS":
            svc = WebMapService(url, version="1.3.0", timeout=timeout)
        elif service_type == "WFS":
            svc = WebFeatureService(url, version="2.0.0", timeout=timeout)
        elif service_type == "WMTS":
            svc = WebMapTileService(url, timeout=timeout)
        else:
            return False, f"Unsupported service type: {service_type}", []

        reachable = True
        error = None

    except Exception as e:
        # Could not even complete GetCapabilities handshake
        return False, str(e), []
    
    # Contact comes from service, not from layer
    service_contact = getattr(svc, "provider", None)
    if service_contact:
        contact_info = getattr(service_contact, "contact", None)
        if contact_info:
            email = getattr(contact_info, "email", None)
            name = getattr(contact_info, "name", None)
            contact = email or name or ""
        else:
            contact = ""
    else:
        contact = ""

    # --- Layer parsing (best effort, should not fail reachability) ---
    try:
        if service_type == "WMS":
            for layer in svc.contents.values():
                layers_data.append({
                    "title": getattr(layer, "title", "") or "",
                    "name": getattr(layer, "name", "") or "",
                    "abstract": getattr(layer, "abstract", "") or "",
                    "contact": contact,
                    "keywords": getattr(layer, "keywords", "") or ""
                })

        elif service_type == "WFS":
            for name in svc.contents:
                layer = svc[name]
                layers_data.append({
                    "title": getattr(layer, "title", "") or "",
                    "name": getattr(layer, "name", "") or "",
                    "abstract": getattr(layer, "abstract", "") or "",
                    "contact": contact,
                    "keywords": getattr(layer, "keywords", "") or ""
                })

        elif service_type == "WMTS":
            for layer in svc.contents.values():
                layers_data.append({
                    "title": getattr(layer, "title", "") or "",
                    "name": getattr(layer, "id", "") or "",
                    "abstract": getattr(layer, "abstract", "") or "",
                    "contact": contact,
                    "keywords": ""
                })

    except Exception as e:
        # Parsing failed, but service is reachable
        error = f"Layer parsing warning: {e}"

    return reachable, error, layers_data

def main():
    parser = argparse.ArgumentParser(description="Preflight check for geoservices")
    parser.add_argument("--input", required=True, help="Path to sources.csv")
    parser.add_argument(
        "--out-diagnostics",
        default="preflight-diagnostics.jsonl",
        help="Output JSONL diagnostics file"
    )
    parser.add_argument(
        "--out-hashes",
        default="preflight-hashes.json",
        help="Output JSON file with priority hashes"
    )

    parser.add_argument(
        "--baseline-hashes",
        default=None,
        help="Optional previous preflight-hashes.json"
    )
    args = parser.parse_args()

    # Load baseline hashes if provided
    baseline_hashes = {}
    if args.baseline_hashes:
        try:
            with open(args.baseline_hashes, encoding="utf-8") as f:
                baseline_hashes = json.load(f)
        except FileNotFoundError:
            print(f"Baseline file {args.baseline_hashes} not found, assuming empty baseline")

    diagnostics = []
    hashes = {}

    with open(args.input, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            provider = (row.get("Description") or "").strip()
            url = (row.get("URL") or "").strip()

            reachable, error, layers = ping_and_parse_service(url)

            if not layers:
                layers = [{
                    "title": "",
                    "name": "",
                    "abstract": "",
                    "contact": "",
                    "keywords": ""
                }]

            for layer in layers:
                dataset_id = f"{provider}:{layer.get('name', '')}"
                hash_new = normalize_then_hash(layer)
                hashes[dataset_id] = hash_new

                needs_preprocessing = baseline_hashes.get(dataset_id) != hash_new

                # Append result for this layer
                diagnostics.append({
                    "provider": provider,
                    "layer_name": layer.get("name", ""),
                    "service_url": url,
                    "checked_at": datetime.utcnow().isoformat() + "Z",
                    "reachable": reachable,
                    "error": error,
                    "needs_preprocessing": needs_preprocessing,
                    "hash": hash_new
                })


    with open(args.out_diagnostics, "w", encoding="utf-8") as f:
        for row in diagnostics:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    with open(args.out_hashes, "w", encoding="utf-8") as f:
        json.dump(hashes, f, indent=2, ensure_ascii=False)

    print(f"Preflight finished: {len(diagnostics)} layers checked")
    print(f"Diagnostics: {args.out_diagnostics}")
    print(f"Hashes: {args.out_hashes}")  # ← CHANGED

if __name__ == "__main__":
    main()
