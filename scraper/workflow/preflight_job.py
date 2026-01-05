#!/usr/bin/env python3

import csv
import json
import time
import argparse
import hashlib
import os
from datetime import datetime
from urllib.parse import urlparse, urlunparse

import requests
import redis
from lxml import etree


# ----------------------------
# Configuration
# ----------------------------

DEFAULT_TIMEOUT = 10
USER_AGENT = "geoservice-preflight/1.0"


# ----------------------------
# Helpers
# ----------------------------

def normalize_service_url(url: str) -> str:
    """
    Strip query params and normalize scheme/host.
    """
    p = urlparse(url)
    return urlunparse((
        p.scheme.lower(),
        p.netloc.lower(),
        p.path,
        "", "", ""
    ))


def normalize_keywords(keyword_str: str):
    """
    From comma-separated string → sorted, deduplicated, lowercase list.
    """
    if not keyword_str:
        return []

    parts = [k.strip().lower() for k in keyword_str.split(",") if k.strip()]
    return sorted(set(parts))


def normalize_contact(contact: str | None):
    if not contact or contact.strip().lower() in ("n.a.", ""):
        return None
    return " ".join(contact.split())


def canonical_priority_json(
    provider: str,
    service_url: str,
    layer_name: str,
    title: str,
    abstract: str,
    contact: str | None,
    keywords: list[str],
):
    """
    Build canonical JSON object used for hashing.
    """
    return {
        "provider": provider.strip(),
        "service_url": normalize_service_url(service_url),
        "layer_name": layer_name.strip(),
        "title": (title or "").strip(),
        "abstract": (abstract or "").strip(),
        "contact": normalize_contact(contact),
        "keywords": keywords,
    }


def hash_priority_payload(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def now_utc():
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


# ----------------------------
# XML parsing (WMS/WFS/WMTS)
# ----------------------------

def detect_service_type(root):
    tag = etree.QName(root.tag).localname.lower()
    if "wms" in tag:
        return "WMS"
    if "wfs" in tag:
        return "WFS"
    if "wmts" in tag:
        return "WMTS"
    return "UNKNOWN"


def find_layers_wms(root):
    ns = root.nsmap
    layers = root.findall(".//{*}Layer[{*}Name]")
    for layer in layers:
        yield {
            "name": layer.findtext("{*}Name"),
            "title": layer.findtext("{*}Title"),
            "abstract": layer.findtext("{*}Abstract"),
            "keywords": ",".join(
                [k.text for k in layer.findall(".//{*}Keyword") if k.text]
            ),
            "contact": None,  # WMS usually service-level; handled outside
        }


def find_layers_wfs(root):
    for ft in root.findall(".//{*}FeatureType"):
        yield {
            "name": ft.findtext("{*}Name"),
            "title": ft.findtext("{*}Title"),
            "abstract": ft.findtext("{*}Abstract"),
            "keywords": ",".join(
                [k.text for k in ft.findall(".//{*}Keyword") if k.text]
            ),
            "contact": None,
        }


def find_layers_wmts(root):
    for layer in root.findall(".//{*}Layer"):
        yield {
            "name": layer.findtext("{*}Identifier"),
            "title": layer.findtext("{*}Title"),
            "abstract": layer.findtext("{*}Abstract"),
            "keywords": ",".join(
                [k.text for k in layer.findall(".//{*}Keyword") if k.text]
            ),
            "contact": None,
        }


# ----------------------------
# Main logic
# ----------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    redis_client = redis.Redis(
        host=os.environ["REDIS_HOST"],
        port=int(os.environ.get("REDIS_PORT", 6379)),
        password=os.environ["REDIS_PASSWORD"],
        decode_responses=True,
    )

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    with open(args.input, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    with open(args.out, "w", encoding="utf-8") as out:
        for row in rows:
            provider = row["Description"].strip()
            url = row["URL"].strip()

            base_result = {
                "provider": provider,
                "service_url": normalize_service_url(url),
                "checked_at": now_utc(),
            }

            try:
                t0 = time.time()
                resp = session.get(url, timeout=args.timeout)
                elapsed_ms = int((time.time() - t0) * 1000)

                if resp.status_code >= 400:
                    raise RuntimeError(f"HTTP {resp.status_code}")

                root = etree.fromstring(resp.content)
                service_type = detect_service_type(root)

                if service_type == "WMS":
                    layers = list(find_layers_wms(root))
                elif service_type == "WFS":
                    layers = list(find_layers_wfs(root))
                elif service_type == "WMTS":
                    layers = list(find_layers_wmts(root))
                else:
                    raise RuntimeError("Unsupported service type")

                for layer in layers:
                    if not layer["name"]:
                        continue

                    keywords = normalize_keywords(layer.get("keywords"))
                    payload = canonical_priority_json(
                        provider=provider,
                        service_url=url,
                        layer_name=layer["name"],
                        title=layer.get("title"),
                        abstract=layer.get("abstract"),
                        contact=layer.get("contact"),
                        keywords=keywords,
                    )

                    priority_hash = hash_priority_payload(payload)

                    redis_key = (
                        f"preflight:priority_hash:"
                        f"{provider}:"
                        f"{hashlib.sha1(payload['service_url'].encode()).hexdigest()}:"
                        f"{layer['name']}"
                    )

                    previous_hash = redis_client.get(redis_key)
                    changed = previous_hash != priority_hash

                    if changed:
                        redis_client.set(redis_key, priority_hash)

                    result = {
                        **base_result,
                        "layer_name": layer["name"],
                        "service_type": service_type,
                        "reachable": True,
                        "response_time_ms": elapsed_ms,
                        "priority_changed": changed,
                    }

                    out.write(json.dumps(result, ensure_ascii=False) + "\n")

            except Exception as e:
                error_result = {
                    **base_result,
                    "reachable": False,
                    "error": str(e),
                }
                out.write(json.dumps(error_result, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
