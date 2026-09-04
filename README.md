# Truth-in-AI — Signed Proof-of-Work

> **TriGeoChiral Engineering — Providing Truth-In-AI, by NOT using it.**

This repository contains the cryptographically signed, Bitcoin-anchored
proof-of-work for the Truth-in-AI AI-generated-text detector.

The detector itself is a proprietary trade secret of David Zubick and
Jennifer Huff and is not distributed here. What you can do with this
repository is **independently verify** that the detector achieves the
results claimed below, without needing to trust TriGeoChiral Engineering.

## Headline

**Mean AUC 0.9302 across 30 attack × domain configurations of the
public RAID benchmark (Dugan et al. 2024, arXiv:2405.07940).**

| Domain | n | Mean AUC | Range |
|---|---:|---:|---|
| overall | 30 | **0.9302** | 0.876 – 1.0000 |

**Adversarial-paraphrase attack** (the config where every published
detector collapses):

| Detector | German paraphrase AUC |
|---|---:|
| GPTZero | 0.62 |
| Originality.ai | 0.71 |
| Binoculars | 0.76 |
| **Truth-in-AI** | **0.996** |

No neural inference. CPU-only. Sub-10-millisecond per document.

## Verify it yourself

```bash
pip install truth-in-ai-verify
truth-in-ai-verify --result RAID.signed.json --pubkey pubkey.pem
```

The verifier checks:
1. **Ed25519 signature** over the entire result payload
2. **Per-config AUCs** — each of the 30 configurations independently
   recomputed from stored per-document scores; any deviation fails.
3. **Bitcoin timestamp** of the signed result via OpenTimestamps.

## Priority anchor (Bitcoin)

`RAID.signed.json.ots` timestamps the signed benchmark result into the
Bitcoin blockchain via OpenTimestamps:

```bash
pip install opentimestamps-client
ots upgrade RAID.signed.json.ots
ots verify RAID.signed.json.ots
```

## Licensing

Proprietary. See `LICENSE`. Verification use only. For commercial
licensing, integration, or partnership inquiries: **trigeochiral@gmail.com**

---
*TriGeoChiral Engineering — Providing Truth-In-AI, by NOT using it.*
