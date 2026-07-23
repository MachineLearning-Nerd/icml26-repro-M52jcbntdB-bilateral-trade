# Claim 4 — VERIFIED

**Paper claim.** Conditional on collecting budget `beta`, Profit-Max regret is soft-`O(beta + T/K + sqrt(KT))` (Lemmas 7.1–7.2).

The actual Exp3 Profit-Max phase was run at `T=2,048, 8,192, 32,768, 131,072`, `beta` coefficients `0.005` and `0.01`, and 12 seeds.

- primary rows: `96`
- target reached: `96/96`
- regret exponent: `0.852576`
- normalized-regret exponent: `0.138499`
- largest mean regret / stated scale: `0.071972`

The verifier measures `beta`, achieved budget, stopping time, phase regret, and every denominator term. The former vacuous `regret < 1000` threshold is not used.

## Evidence files

- [Contract](../../../evidence/2026/claim_4/claim_contract.json)
- [Source audit](../../../evidence/2026/claim_4/source_audit.md)
- [Method](../../../evidence/2026/claim_4/method.md)
- [Result](../../../evidence/2026/claim_4/result.json)
- [Raw sweep](../../../evidence/2026/claim_4/raw_results.csv)
- [Primary verifier](../../../evidence/2026/claim_4/verifier_output.txt)
- [Independent checker](../../../evidence/2026/claim_4/independent_checker_output.txt)
- [Non-stopping negative control](../../../evidence/2026/claim_4/negative_control_output.txt)

