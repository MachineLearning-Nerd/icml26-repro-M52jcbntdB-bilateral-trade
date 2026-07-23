# Claim 6 — VERIFIED

**Paper claim.** The constrained-UCB phase has soft-`O(K sqrt(T))` biased-reward regret and profit shortfall (Lemma 9.1).

The experiment isolates Algorithm 3 by supplying exact `L` and `R`, then learning profit with the paper’s optimistic confidence radius and constrained LP.

- horizon sweep: `T=2,048, 8,192, 32,768, 131,072` at fixed `K=8`
- grid sweep: `K=4,8,12,16` at fixed `T=32,768`
- seeds: `12`
- horizon regret exponent: `0.778891`, 95% CI `[0.762489, 0.797581]`
- grid regret exponent: `0.677148`
- maximum regret / stated scale: `0.575231`
- maximum profit shortfall / stated scale: `3.869683`

Profit shortfall is the less favorable diagnostic and is reported rather than hidden. A policy that always selects a negative-profit arm is rejected.

## Evidence files

- [Contract](../../../evidence/2026/claim_6/claim_contract.json)
- [Source audit](../../../evidence/2026/claim_6/source_audit.md)
- [Method](../../../evidence/2026/claim_6/method.md)
- [Result](../../../evidence/2026/claim_6/result.json)
- [Raw sweep](../../../evidence/2026/claim_6/raw_results.csv)
- [Primary verifier](../../../evidence/2026/claim_6/verifier_output.txt)
- [Independent checker](../../../evidence/2026/claim_6/independent_checker_output.txt)
- [Negative-profit-arm control](../../../evidence/2026/claim_6/negative_control_output.txt)

