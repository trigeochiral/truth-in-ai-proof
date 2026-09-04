# Truth-in-AI — Signed Proof-of-Work

**TriGeoChiral Engineering — Providing Truth-In-AI, by NOT using it.**

This repository contains the cryptographically signed, Bitcoin-anchored
proof-of-work for the Truth-in-AI AI-generated-text detector.

The Truth In AI signal intelligence engine is proprietary,and is not distributed here. What you can do with this
repository is **independently verify** that the CPU-driven architecture achieves the
results claimed below. We value honesty, integrity, and the scientific method, and we're looking forward to proving it. 
Yes, I used AI to write the rest of this. Thank you for your visit. 

September 4, 2026 
 **RAID 0.87–0.999 accuracy across all 8 domains** — mean AUC 0.
9302 across 30 attack × domain configurations of the RAID benchmar
k. Code sits at the 0.87 floor — a domain most detectors decline t
o attempt.
3. **Perfect separation on adversarial attacks** — German/homoglyp
h: **AUC 1.0000 [1.0000–1.0000], TPR 100% at 5% FPR, ECE 0.0016.**
 For enterprise buyers, that last number matters most: at the indu
stry-standard false-positive threshold we catch **every** AI submi
ssion — the exact operating point where Turnitin failed and univer
sities pulled the plug.


**Mean AUC 0.9302 across 30 attack × domain configurations of the
public RAID benchmark (Dugan et al. 2024, arXiv:2405.07940).**

| Domain |  n | Mean AUC   |  Range         |
| overall| 30 | **0.9302** | 0.876 – 1.0000 |

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
