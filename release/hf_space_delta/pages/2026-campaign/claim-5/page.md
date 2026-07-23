# Claim 5 — VERIFIED

**Paper claim.** Algorithm 2 estimates all `K²` price-pair outcomes using `2K` exploration lines and exactly `2KN` rounds (Lemmas 8.1–8.2).

The actual exploration phase was run for 128 trials at each configuration:

| K | N | Rounds | Max observed error | Simultaneous bound |
|---:|---:|---:|---:|---:|
| 8 | 256 | 4,096 | 0.096119 | 0.182655 |
| 16 | 512 | 16,384 | 0.076172 | 0.139245 |
| 32 | 1,024 | 65,536 | 0.064421 | 0.105111 |

Every run updated all `K²` cells in exactly `2KN` rounds. There were zero simultaneous failures; the exact one-sided 95% failure-probability upper bound was `0.023132 < delta=0.05`. The identity `GFT=L+R+PRO` held to `1.11e-16`.

This is an estimation-accuracy experiment, not the arithmetic fact `2K<K²`.

## Evidence files

- [Contract](../../../evidence/2026/claim_5/claim_contract.json)
- [Source audit](../../../evidence/2026/claim_5/source_audit.md)
- [Method](../../../evidence/2026/claim_5/method.md)
- [Result](../../../evidence/2026/claim_5/result.json)
- [Raw trial rows](../../../evidence/2026/claim_5/raw_results.csv)
- [Primary verifier](../../../evidence/2026/claim_5/verifier_output.txt)
- [Independent checker](../../../evidence/2026/claim_5/independent_checker_output.txt)
- [Reversed-indicator control](../../../evidence/2026/claim_5/negative_control_output.txt)

