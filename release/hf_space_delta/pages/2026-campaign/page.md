# 2026 claim-by-claim reproduction audit

This page is an additive update. Every page and evidence file from the judged revision `a3bd9c2e315f02cb584c634c58036238f87289f5` remains present and byte-for-byte unchanged.

## Outcome

| Claim | Verdict | Direct evidence |
|---:|---|---|
| 1 | **BLOCKED** | End-to-end exponent `0.9903` (95% CI `[0.9873, 0.9935]`) through `T=1,048,576`; phases 2–3 never ran; three manuscript proof obligations remain open. |
| 2 | **VERIFIED** | Exact hard-instance GBB LP gap `0.005211 > 1/200` plus a feedback-history packing certificate. |
| 3 | **VERIFIED** | Comparator-only bounded-density projection and grid audit through `K=257`; zero projection violations. |
| 4 | **VERIFIED** | Actual Profit-Max at four horizons over 64×, two budget coefficients, and 12 seeds; every conditional target reached. |
| 5 | **VERIFIED** | Actual Algorithm 2 at `K=8,16,32`, 128 trials each, exactly `2KN` rounds, all `K²` estimates, zero simultaneous failures. |
| 6 | **VERIFIED** | Actual constrained UCB with 64× horizon and 4× grid sweeps, 12 seeds; regret exponents below preregistered finite-sample ceilings. |

These are reproduction verdicts, not a claimed live-judge score. The last judged score remains **2/12** until the judge evaluates a published revision.

## Fixed command and compute

```sh
uv sync --frozen && .venv/bin/python repro/src/verify_bt.py
```

- Winning evidence Git SHA: `d171f3cc28c2a117061697e79fc09110008f40ab`
- Formal cumulative runtime: `834.9 s`
- Hardware: local Apple M2 CPU
- Hugging Face runtime/cost: `0 s / $0`
- GPU runtime: `0 s`

Each claim page links to its raw text evidence, contract, verifier output, independent-checker output, and deliberately failing negative control.

