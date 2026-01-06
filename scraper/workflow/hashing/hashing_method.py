import hashlib

def safe_strip(value):
    if value is None:
        return ""
    return str(value).strip()

def normalize_keywords(raw_keywords):
    """Deduplicate, strip, join by comma"""
    if not raw_keywords:
        return ""
    if isinstance(raw_keywords, str):
        kw_list = [k.strip() for k in raw_keywords.split(",") if k.strip()]
    elif isinstance(raw_keywords, list):
        kw_list = [str(k).strip() for k in raw_keywords if str(k).strip()]
    else:
        return ""
    # remove duplicates while preserving order
    return ",".join(sorted(list(dict.fromkeys(kw_list))))

def normalize_contact(raw_contact):
    if not raw_contact or raw_contact.lower() == "n.a.":
        return ""
    return raw_contact.strip()


def compute_priority_hash(dataset):
    """Compute SHA256 hash of the 5 key fields"""
    key_fields = [
        dataset.get('title', ''),
        dataset.get('name', ''),
        dataset.get('abstract', ''),
        # dataset.get('contact', ''),
        dataset.get('keywords', '')
    ]
    combined = "||".join([str(f).strip() for f in key_fields])
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()


def normalize_then_hash(layer): 
        # Normalize
    layer["keywords"] = normalize_keywords(layer.get("keywords"))
    layer["contact"] = normalize_contact(layer.get("contact"))
    layer["title"] = safe_strip(layer.get("title"))
    layer["name"] = safe_strip(layer.get("name"))
    layer["abstract"] = safe_strip(layer.get("abstract"))

    # Compute priority hash
    hash_new = compute_priority_hash(layer)

    return hash_new
