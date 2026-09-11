# Notice of Authorship and Ownership

## Work

**Proofline** — a statistical AI-generated-text detector developed by
TriGeoChiral Engineering.

## Authors

- David Zubick
- Jennifer Huff

Contact: trigeochiral@gmail.com

## Ownership

The Proofline detector — its feature extractor, tokenizer, encoder and
trained model parameters — is proprietary and confidential. It is not
published in this repository, is not distributed in the
`proofline-verify` package, and is available only under a separate
commercial agreement.

The verifier published here contains no detector. It reads a signed result
and checks it; it cannot produce one.

## What is published, and why

This repository publishes signed benchmark results, the public key they
verify against, and the tool that checks them. That is deliberate: a
detection claim that cannot be re-examined by the person relying on it is
not worth much, particularly where the result may affect a student, an
employee or a party to a dispute.

Anyone may verify these results, analyse the per-document scores they
contain, compare them against other detectors, and publish the outcome.
See `LICENSE` for the terms.

## Timestamping

`RAID.signed.json.ots` is an OpenTimestamps proof that commits the SHA-256
of the signed RAID payload to the Bitcoin blockchain, establishing that the
result existed in its published form at the time it was anchored. Verify it
with the reference client:

```bash
pip install opentimestamps-client
ots upgrade RAID.signed.json.ots
ots verify RAID.signed.json.ots -f RAID.signed.json
```

This timestamps the *result*. It is not, on its own, a claim of priority of
invention, and it is not a patent filing.

---

Copyright (c) 2026 David Zubick & Jennifer Huff (TriGeoChiral Engineering).
All rights not expressly granted in `LICENSE` are reserved.
