# Repository status

## Scope

This repository audits six claims from
*A Stronger Benchmark for Online Bilateral Trade: From Fixed Prices to
Distributions*, arXiv 2602.05681v1, OpenReview M52jcbntdB.

The audit covers the paper's needle lower bound, bounded-density
discretization, Profit-Max phase, sample-reuse exploration, constrained UCB
phase, and the complete Theorem 4.1 composition.

## Current scientific result

| Result | Count | Meaning |
| --- | ---: | --- |
| VERIFIED within contract | 5 | Claims 2–6 have evidence, independent checks, and rejected negative controls. |
| BLOCKED | 1 | Claim 1 has unresolved source obligations and a phase-incomplete finite diagnostic. |
| FALSIFIED | 0 | No claim is reported as falsified by this campaign. |

Claim 2 is verified only with a visible source repair: the paper's Figure 1
and Section 2 convention are implemented, while the appendix-literal
construction is preserved as a failing control. Claim 3 is comparator-only;
Claims 4–6 are finite/scoped phase contracts.

## Evidence and publication state

- Fixed command: uv sync --frozen && .venv/bin/python repro/src/verify_bt.py
- Evidence release gate: passed
- Strict publication gate: not ready
- Candidate revision: 4c4e95f577956c896d3286ae303237b856f5ae6d
- Recorded live score: 2/12; newer candidate awaiting judge
- Compute: local Apple M2 CPU; no Hugging Face compute

## Open scientific work

1. Supply the missing Profit-Max nontermination proof in Theorem 4.1.
2. Supply the promised Lemma 7.2 proof.
3. Specify a confidence-event allocation that preserves the theorem's total
   1-delta guarantee.
4. Run an end-to-end regime that actually reaches all three algorithm phases,
   without treating finite behavior as an asymptotic proof.

## Repository hygiene

- Public repository target: MachineLearning-Nerd/icml26-online-bilateral-trade
- Default branch: main
- Branch roles and old-to-new names: [BRANCH_AUDIT.md](BRANCH_AUDIT.md)
- Public maintainer identity: MachineLearning-Nerd
