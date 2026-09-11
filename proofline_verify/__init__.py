"""proofline-verify — third-party verification of Proofline signed benchmark results.

Verify any Proofline signed artifact:
    proofline-verify --result RAID.signed.json --pubkey pubkey.pem

Checks the Ed25519 signature, the frozen dataset manifest hashes, and
recomputes every per-configuration AUC from the stored per-document scores.
"""
__version__ = "2.0.0"
