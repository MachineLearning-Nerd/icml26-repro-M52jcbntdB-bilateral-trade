# Claim 1 — BLOCKED

**Paper claim.** Under bounded density, Algorithm 1 is GBB and has soft-`O(T^(3/4))` regret (Theorem 4.1).

## Observed evidence

The direct three-phase implementation used `K=round(T^(1/4))`, `N=round(T^(1/2))`, `beta=0.18*T^(3/4)`, four horizons from `16,384` through `1,048,576`, and 12 deterministic seeds.

| T | Mean regret |
|---:|---:|
| 16,384 | 782.888 |
| 65,536 | 3,144.332 |
| 262,144 | 12,065.627 |
| 1,048,576 | 48,580.150 |

Fitted exponent: `0.9903165`; 95% seed-bootstrap CI: `[0.9872549, 0.9935171]`. Profit-Max did not stop, so exploration and constrained UCB never ran.

This finite result blocks empirical verification but does **not** falsify an asymptotic theorem.

## Source-level blockers

1. Appendix F explicitly assumes `tau_2 < T` and does not prove the complementary Profit-Max-nontermination case.
2. Appendix C promises omitted Section 7 proofs but contains only Lemma 7.1; the proof of Lemma 7.2 is absent.
3. Lemmas 8.2 and 9.1 each state a `1-delta` event, while Theorem 4.1 also states `1-delta`; Algorithm 1 does not specify a confidence split.

The Appendix-F exponent algebra itself recomputes to `3/4`, but algebra alone is not promoted to a VERIFIED verdict.

## Evidence files

- [Contract](../../../evidence/2026/claim_1/claim_contract.json)
- [Source audit](../../../evidence/2026/claim_1/source_audit.md)
- [Method](../../../evidence/2026/claim_1/method.md)
- [Result](../../../evidence/2026/claim_1/result.json)
- [Raw term table](../../../evidence/2026/claim_1/raw_results.csv)
- [Primary verifier](../../../evidence/2026/claim_1/verifier_output.txt)
- [Independent checker](../../../evidence/2026/claim_1/independent_checker_output.txt)
- [Negative control](../../../evidence/2026/claim_1/negative_control_output.txt)

