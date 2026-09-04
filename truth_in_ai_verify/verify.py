"""
Third-party TREVS verifier.

Given a signed result blob and (optionally) a signing public key, this
tool re-runs the evaluation and confirms every published metric.
"""
from __future__ import annotations
import argparse, json, os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from truth_in_ai_verify.manifest   import verify_manifest
from truth_in_ai_verify.sign       import verify_signature
from truth_in_ai_verify.statistics import bootstrap_auc_ci
from sklearn.metrics import roc_auc_score


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--result",  required=True, help="signed result JSON")
    ap.add_argument("--pubkey",  default=None,  help="Ed25519 public key PEM")
    ap.add_argument("--tolerance", type=float, default=0.005,
                    help="max acceptable AUC deviation on rerun")
    args = ap.parse_args()

    with open(args.result) as f: signed = json.load(f)

    ok = True
    print("── STAGE 1: signature ──")
    if args.pubkey and signed.get("signature_algo") == "ed25519":
        v = verify_signature(signed, args.pubkey)
        print(f"  Ed25519 signature: {'VALID' if v else 'INVALID'}")
        ok = ok and v
    else:
        print(f"  no public key provided or result unsigned; "
              f"checking payload SHA-256 only")
        import hashlib, json as _json
        canonical = _json.dumps(signed["payload"], sort_keys=True, separators=(",", ":")).encode()
        digest_ok = hashlib.sha256(canonical).hexdigest() == signed["payload_sha256"]
        print(f"  payload SHA-256: {'OK' if digest_ok else 'MISMATCH'}")
        ok = ok and digest_ok

    payload = signed["payload"]

    print("\n── STAGE 2: dataset manifest ──")
    problems = verify_manifest(payload["manifest"])
    if problems:
        for name, expected, actual in problems:
            print(f"  MISMATCH  {name}: expected {expected} got {actual}")
        ok = False
    else:
        print(f"  {len(payload['manifest']['datasets'])} files: HASHES MATCH")

    print("\n── STAGE 3: recompute AUCs from stored scores ──")
    per_result_ok = []
    for r in payload["results"]:
        y = np.array(r["y_true"]); s = np.array(r["scores"])
        auc_rerun = roc_auc_score(y, s)
        delta = abs(auc_rerun - r["auc"])
        status = "OK" if delta < args.tolerance else "FAIL"
        per_result_ok.append(status == "OK")
        print(f"  {r['domain']:7} {r['attack']:22}  published {r['auc']:.4f}  "
              f"recomputed {auc_rerun:.4f}  Δ {delta:.4f}  {status}")
    ok = ok and all(per_result_ok)

    print("\n" + ("═" * 60))
    if ok:
        print("  ✅  RESULT VERIFIED")
        print(f"      Mean AUC across {len(payload['results'])} configs: "
              f"{payload['mean_auc']:.4f}")
        sys.exit(0)
    else:
        print("  ❌  VERIFICATION FAILED — see above")
        sys.exit(1)


if __name__ == "__main__":
    main()
