import hashlib


def document_hash(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def stable_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()[:10].upper()
    return f"{prefix}_{digest}"