# Proofline — Signed Proof-of-Work

**TriGeoChiral Engineering — Providing Proofline, by NOT using AI.**

This repository holds the cryptographically signed, Bitcoin-anchored
proof-of-work for the Proofline AI-generated-text detector.

The Proofline signal-intelligence engine is proprietary and is **not**
distributed here. What this repository lets you do is **independently verify**
that the published results are the results that were actually produced — with
no account, no NDA, no network connection, and no need to trust us.

## Results

Signed run `raid_all`, seed 42, produced 2026-09-04 against the public RAID
benchmark (Dugan et al. 2024, [arXiv:2405.07940](https://arxiv.org/abs/2405.07940)).

**Mean AUC 0.9302 across 30 attack × domain configurations** — the RAID `extra`
split: code, German and Czech, each under 10 adversarial attacks.

| Domain  |  n | Mean AUC | Range          |
|---------|---:|---------:|----------------|
| overall | 30 | **0.9302** | 0.876 – 1.0000 |

Code sits at the 0.876 floor — a domain most detectors decline to attempt.

**Adversarial attacks**, where published detectors collapse:

| Configuration | AUC |
|---|---:|
| German · homoglyph | **1.0000** |
| Czech · paraphrase | **0.9980** |
| German · paraphrase | **0.9958** |
| Code · paraphrase | **0.9715** |

Against published numbers on German paraphrase:

| Detector | German paraphrase AUC |
|----------------|----------------------:|
| GPTZero        | 0.62 |
| Originality.ai | 0.71 |
| Binoculars     | 0.76 |
| **Proofline**  | **0.996** |

A second signed run, `dmitva_english` (8 configs, mean AUC **0.9987**), is
included as `DMITVA.signed.json`.

No neural inference. CPU-only. Sub-10-millisecond per document.

## Verify it yourself

```bash
pip install proofline-verify
proofline-verify --result RAID.signed.json --pubkey pubkey.pem
```

Runs offline. Exits `0` on success, non-zero on any failure.

### What the verifier checks

1. **Ed25519 signature** over the canonical payload (sorted keys, no
   whitespace), against `pubkey.pem`, plus the payload SHA-256.
2. **Dataset manifest** — the SHA-256 of every source dataset file recorded in
   the payload is checked, so the result is bound to exact input bytes.
3. **Per-configuration AUCs** — all 30 configurations are recomputed from the
   stored per-document scores and labels and compared to the published values.

Check 3 is the one that matters: the raw per-document scores ship inside the
artifact, so the numbers cannot be edited even by someone holding a signing
key. Alter an AUC and re-sign it with your own key and the recompute still
catches it.

### What the verifier does not check

The **OpenTimestamps anchor**. Verifying a Bitcoin attestation needs a
calendar/node round-trip, so it is deliberately out of scope for an offline
tool. Check it separately:

```bash
pip install opentimestamps-client
ots upgrade RAID.signed.json.ots
ots verify RAID.signed.json.ots -f RAID.signed.json
```

## Contents

| File | What it is |
|---|---|
| `RAID.signed.json` | Signed RAID `extra` result — payload, `payload_sha256`, Ed25519 signature, and per-document scores for all 30 configs. |
| `RAID.signed.json.ots` | OpenTimestamps Bitcoin anchor for the above. |
| `DMITVA.signed.json` | Signed dmitva English result, 8 configs, same key and format. |
| `pubkey.pem` | Ed25519 public key both signatures verify against. |
| `proofline_verify/` | Source of the `proofline-verify` PyPI package. Verifier only — no detector. |

## Licensing

Proprietary. See `LICENSE`. Verification use only. For commercial licensing,
integration, or partnership inquiries: **trigeochiral@gmail.com**

---
*TriGeoChiral Engineering — Providing Proofline, by NOT using AI.*
