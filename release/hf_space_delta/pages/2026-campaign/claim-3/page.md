# Claim 3 — VERIFIED

**Paper claim.** Bounded density permits a `K×K` uniform grid with discretization error `O(log(T)/K)` (Lemmas 5.1–5.2).

This check removes online learning entirely. It compares only dense and grid-restricted GBB comparator LPs on three analytic bounded-density rectangle mixtures for nested `K=5,9,17,33,65,129,257`.

- feasible two-action projection trials: `10,752`
- directed-projection violations: `0`
- independent SciPy HiGHS LP cross-checks: PASS
- uniform and separated-market gaps: exact zero
- correlated-four-rectangle maximum gap: `0.0004503038`; exact by `K=33`

The former total-regret proxy is not used.

## Evidence files

- [Contract](../../../evidence/2026/claim_3/claim_contract.json)
- [Source audit](../../../evidence/2026/claim_3/source_audit.md)
- [Method](../../../evidence/2026/claim_3/method.md)
- [Result](../../../evidence/2026/claim_3/result.json)
- [Raw grid rows](../../../evidence/2026/claim_3/raw_results.csv)
- [Primary verifier](../../../evidence/2026/claim_3/verifier_output.txt)
- [Independent LP checker](../../../evidence/2026/claim_3/independent_checker_output.txt)
- [Negative control](../../../evidence/2026/claim_3/negative_control_output.txt)

