"""
Ed25519 signature verification for Proofline signed results.

Verify-only: this module intentionally does NOT include key-generation
or signing helpers. To create signed results, use TriGeoChiral internal
tooling.
"""
from __future__ import annotations
import json, hashlib

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives import serialization


def verify_signature(signed: dict, public_key_pem_path: str) -> bool:
    canonical = json.dumps(signed["payload"], sort_keys=True, separators=(",", ":")).encode()
    if hashlib.sha256(canonical).hexdigest() != signed["payload_sha256"]:
        return False
    if signed.get("signature_algo") != "ed25519":
        return False
    with open(public_key_pem_path, "rb") as f:
        pub = serialization.load_pem_public_key(f.read())
    try:
        pub.verify(bytes.fromhex(signed["signature"]), canonical)
        return True
    except Exception:
        return False
