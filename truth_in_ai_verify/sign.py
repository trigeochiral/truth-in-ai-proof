"""
Ed25519 signing for TREVS results.
Uses cryptography package if available; falls back to a plain SHA-256
digest with a warning otherwise (so tests can run in constrained envs).
"""
from __future__ import annotations
import json, hashlib, os
from pathlib import Path

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PrivateKey, Ed25519PublicKey,
    )
    from cryptography.hazmat.primitives import serialization
    _HAS_ED25519 = True
except ImportError:
    _HAS_ED25519 = False


def gen_keypair(out_dir: str = None) -> tuple[str, str]:
    if not _HAS_ED25519:
        raise RuntimeError("install `cryptography` for Ed25519 support")
    priv = Ed25519PrivateKey.generate()
    pub  = priv.public_key()
    priv_bytes = priv.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption())
    pub_bytes  = pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        with open(f"{out_dir}/privkey.pem", "wb") as f: f.write(priv_bytes)
        with open(f"{out_dir}/pubkey.pem",  "wb") as f: f.write(pub_bytes)
        return f"{out_dir}/privkey.pem", f"{out_dir}/pubkey.pem"
    return priv_bytes.decode(), pub_bytes.decode()


def sign_result(result: dict, private_key_pem_path: str) -> dict:
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    digest = hashlib.sha256(canonical).hexdigest()
    if not _HAS_ED25519:
        return {"payload": result, "signature_algo": "sha256-only",
                "payload_sha256": digest,
                "warning": "cryptography package unavailable; result carries a plain SHA-256 digest only. Install cryptography for Ed25519 signing."}
    with open(private_key_pem_path, "rb") as f:
        priv = serialization.load_pem_private_key(f.read(), password=None)
    sig = priv.sign(canonical).hex()
    return {"payload": result, "signature_algo": "ed25519",
            "payload_sha256": digest, "signature": sig}


def verify_signature(signed: dict, public_key_pem_path: str) -> bool:
    canonical = json.dumps(signed["payload"], sort_keys=True, separators=(",", ":")).encode()
    if hashlib.sha256(canonical).hexdigest() != signed["payload_sha256"]:
        return False
    if signed.get("signature_algo") != "ed25519":
        return False   # unsigned or fallback-only
    with open(public_key_pem_path, "rb") as f:
        pub = serialization.load_pem_public_key(f.read())
    try:
        pub.verify(bytes.fromhex(signed["signature"]), canonical)
        return True
    except Exception:
        return False
