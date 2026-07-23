# Reproduction: online bilateral trade against price distributions

[![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/MachineLearning-Nerd/icml26-repro-M52jcbntdB-bilateral-trade/blob/master/notebooks/bilateral_trade_reproduction.py)

This repository reproduces the six judged claims from [*A Stronger Benchmark for Online Bilateral Trade: From Fixed Prices to Distributions*](https://arxiv.org/abs/2602.05681) (OpenReview `M52jcbntdB`). The paper’s headline number is a soft-\(O(T^{3/4})\) regret rate under bounded density. Our largest direct run instead measured a \(T^{0.9903}\) regret exponent (95% CI `[0.9873, 0.9935]`) through \(T=1{,}048{,}576\), because the algorithm never left its profit-collection phase.

The cumulative assessment is therefore **Claims 2–6 VERIFIED; Claim 1 BLOCKED**. The text-only evidence release is published at Hugging Face revision [`4c4e95f577956c896d3286ae303237b856f5ae6d`](https://huggingface.co/spaces/DineshAI/M52jcbntdB/commit/4c4e95f577956c896d3286ae303237b856f5ae6d), but this is not a claimed live-score increase: the judge still points to `a3bd9c2e315f02cb584c634c58036238f87289f5` at 2/12 and the new revision is awaiting evaluation.

What changed:

- implemented the paper’s actual needle construction, directed grid projection, Profit-Max, \(2KN\) exploration, and constrained UCB phases;
- replaced one-point or arithmetic-only thresholds with 64× sweeps, 12 deterministic seeds, exact LP certificates, independent checkers, and failing negative controls;
- used local Apple M2 CPU only, with Python 3.12.11 and a committed `uv.lock`; no GPU or Hugging Face compute was used;
- documented the Claim 2 sign/coordinate repair, and kept the appendix-literal version as a rejected negative control;
- retained Claim 1 as BLOCKED because its finite run did not exercise all phases and the source leaves three proof obligations unresolved.

Read the [illustrated technical report](reports/bilateral-trade-reproduction/report.md) or open the [self-contained marimo tutorial](notebooks/bilateral_trade_reproduction.py). Raw machine-readable evidence and checker output live under `.openresearch/artifacts/`.

## Experiment log

Every formal experiment used this exact command: `uv sync --frozen && .venv/bin/python repro/src/verify_bt.py`.

| Branch / experiment | Purpose or change | Exact run command | Assessment / outcome | Compute |
|---|---|---|---|---|
| `master` | Public README, report, notebook, and preserved evidence | Not run as an experiment (publication surface) | Presentation-only | — |
| [`orx/frozen-judged-baseline`](https://github.com/MachineLearning-Nerd/icml26-repro-M52jcbntdB-bilateral-trade/tree/orx/frozen-judged-baseline) | Freeze and reproduce the judged six-check harness | `uv sync --frozen && .venv/bin/python repro/src/verify_bt.py` | Harness 6/6 PASS, but live judge remained 2/12 because checks were toy/proxy evidence | Local CPU, 20 s |
| [`orx/faithful-claim-contracts-and-phase-implementatio`](https://github.com/MachineLearning-Nerd/icml26-repro-M52jcbntdB-bilateral-trade/tree/orx/faithful-claim-contracts-and-phase-implementatio) | First clean-room direct implementations and claim contracts | `uv sync --frozen && .venv/bin/python repro/src/verify_bt.py` | Claims 2, 5, 6 verified; Claims 1, 3, 4 correctly blocked | Local CPU, 7 m 15 s |
| [`orx/feasible-projection-audit-and-asymptotic-phase-c`](https://github.com/MachineLearning-Nerd/icml26-repro-M52jcbntdB-bilateral-trade/tree/orx/feasible-projection-audit-and-asymptotic-phase-c) | Correct feasible projection domain; run million-round theorem diagnostic | `uv sync --frozen && .venv/bin/python repro/src/verify_bt.py` | Claims 2–6 verified; Claim 1 blocked with observed exponent 0.9903 | Local CPU, 1 h 9 m |
| [`orx/compositional-theorem-4-1-certificate`](https://github.com/MachineLearning-Nerd/icml26-repro-M52jcbntdB-bilateral-trade/tree/orx/compositional-theorem-4-1-certificate) | Cumulative regression plus exact Appendix-F exponent and proof-obligation audit | `uv sync --frozen && .venv/bin/python repro/src/verify_bt.py` | Claims 2–6 verified; Claim 1 honestly blocked on three source gaps | Local CPU, 14 m 35 s |
| [`orx/release-candidate-report-and-preserved-logbook`](https://github.com/MachineLearning-Nerd/icml26-repro-M52jcbntdB-bilateral-trade/tree/orx/release-candidate-report-and-preserved-logbook) | Final cumulative regression and immutable-Space preservation package | `uv sync --frozen && .venv/bin/python repro/src/verify_bt.py` | Claims 2–6 verified; Claim 1 blocked; 94-file text release published and awaiting judge | Local CPU, 13 m 29 s |

## Reproduce locally

```sh
uv sync --frozen
.venv/bin/python repro/src/verify_bt.py
```

The command exits zero when every claim has one of the allowed honest outcomes (`VERIFIED`, `FALSIFIED`, or `BLOCKED`) and all accepted-claim regressions, negative controls, and independent checks behave as specified. Regenerate the report figures with:

```sh
uv run --frozen python reports/bilateral-trade-reproduction/generate_report_assets.py
```

The marimo article embeds the small headline results, so opening it does not rerun the expensive formal experiments:

```sh
uv run --frozen marimo edit notebooks/bilateral_trade_reproduction.py
uv run --frozen marimo run notebooks/bilateral_trade_reproduction.py
```

## Original project marker

OpenReview `M52jcbntdB`. arXiv `2602.05681`. Six judged claims / 12 possible points. Owner: loop12pt.
