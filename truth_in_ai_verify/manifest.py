"""
Dataset + model provenance registry.

Every benchmark run resolves a config against this registry and refuses
to run if any file's SHA-256 doesn't match what was recorded when the
manifest was signed.
"""
from __future__ import annotations
import hashlib, json, os, sys, time
from pathlib import Path


def sha256_file(path: str, chunk: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for buf in iter(lambda: f.read(chunk), b""):
            h.update(buf)
    return h.hexdigest()


def make_manifest(dataset_files: dict, model_file: str = None,
                  seed: int = 42, extra: dict = None) -> dict:
    """dataset_files: {name: absolute_path}. Returns a manifest dict."""
    entries = {}
    for name, path in dataset_files.items():
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        entries[name] = {
            "path": path,
            "sha256": sha256_file(path),
            "size_bytes": os.path.getsize(path),
        }
    m = {
        "trevs_version": "1.0.0",
        "created_ts": int(time.time()),
        "created_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "seed": seed,
        "datasets": entries,
        "python_version": sys.version.split()[0],
        "platform": sys.platform,
    }
    if model_file and os.path.exists(model_file):
        m["model"] = {"path": model_file, "sha256": sha256_file(model_file),
                      "size_bytes": os.path.getsize(model_file)}
    if extra:
        m["extra"] = extra
    return m


def verify_manifest(manifest: dict) -> list:
    """Re-hash every file; return list of (name, expected_sha, actual_sha)
    for entries that DON'T match."""
    problems = []
    for name, entry in manifest["datasets"].items():
        path = entry["path"]
        if not os.path.exists(path):
            problems.append((name, entry["sha256"], "MISSING")); continue
        actual = sha256_file(path)
        if actual != entry["sha256"]:
            problems.append((name, entry["sha256"], actual))
    if "model" in manifest and os.path.exists(manifest["model"]["path"]):
        if sha256_file(manifest["model"]["path"]) != manifest["model"]["sha256"]:
            problems.append(("model", manifest["model"]["sha256"],
                             sha256_file(manifest["model"]["path"])))
    return problems


if __name__ == "__main__":
    # CLI: build a manifest for a caller-supplied set of dataset files.
    # NO filesystem paths are hard-coded in this file -- every path must
    # be provided by the caller via --dataset NAME PATH.
    import argparse
    ap = argparse.ArgumentParser(description="Build a signed-manifest input.")
    ap.add_argument("--dataset", nargs=2, action="append",
                    metavar=("NAME", "PATH"), required=True,
                    help="Register a dataset file. Repeat for multiple.")
    ap.add_argument("--model", metavar="PATH", default=None,
                    help="Optional model file to include in the manifest.")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    print(json.dumps(
        make_manifest(dict(args.dataset), model_file=args.model, seed=args.seed),
        indent=2))
