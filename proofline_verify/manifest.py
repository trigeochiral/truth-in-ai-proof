"""
Dataset manifest verification.

Verify-only: this module re-hashes files against a signed manifest and
reports mismatches. It intentionally does NOT include manifest-creation
helpers. To create signed manifests, use TriGeoChiral internal tooling.
"""
from __future__ import annotations
import hashlib, os


def sha256_file(path: str, chunk: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for buf in iter(lambda: f.read(chunk), b""):
            h.update(buf)
    return h.hexdigest()


def verify_manifest(manifest: dict) -> list:
    """Re-hash every file; return list of (name, expected_sha, actual_sha)
    for entries that DON'T match."""
    problems = []
    for name, entry in manifest["datasets"].items():
        path = entry["path"]
        if not os.path.exists(path):
            problems.append((name, entry["sha256"], "MISSING"))
            continue
        actual = sha256_file(path)
        if actual != entry["sha256"]:
            problems.append((name, entry["sha256"], actual))
    if "model" in manifest and os.path.exists(manifest["model"]["path"]):
        if sha256_file(manifest["model"]["path"]) != manifest["model"]["sha256"]:
            problems.append(("model", manifest["model"]["sha256"],
                             sha256_file(manifest["model"]["path"])))
    return problems
