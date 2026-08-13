# ICML 2026 — A Stronger Benchmark for Online Bilateral Trade

[![Open in Molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/MachineLearning-Nerd/icml26-online-bilateral-trade/blob/main/notebooks/bilateral_trade_reproduction.py)

This repository contains an independent, CPU-only audit of the six claims
associated with the ICML 2026 paper
[*A Stronger Benchmark for Online Bilateral Trade: From Fixed Prices to Distributions*](https://arxiv.org/abs/2602.05681).
The paper studies online bilateral trade with one-bit feedback, global budget
balance, and a benchmark defined by the best fixed distribution over seller and
buyer prices.

The current evidence package resolves **Claims 2–6 as VERIFIED within their
documented contracts and Claim 1 as BLOCKED**. Claim 2 uses a disclosed repair
of an inconsistent hard-instance transcription. Claim 1 is not promoted from
power-counting evidence because three proof obligations remain open and the
largest end-to-end run never reached the paper’s exploration and constrained-UCB
phases. The evidence release is complete; the strict publication gate is
**NOT_READY** and no new live score is claimed.

## Paper

- **Title:** A Stronger Benchmark for Online Bilateral Trade: From Fixed Prices to Distributions
- **Authors:** Anna Lunghi, Mattia Piccinato, Matteo Castiglioni, and Alberto Marchesi
- **arXiv:** [2602.05681v1](https://arxiv.org/abs/2602.05681)
- **OpenReview:** [M52jcbntdB](https://openreview.net/forum?id=M52jcbntdB)
- **Venue:** To appear at ICML 2026
- **Pinned source:** arXiv v1; hashes and theorem anchors are recorded in
  [SOURCE_MANIFEST.md](SOURCE_MANIFEST.md).

At each round, a learner posts a seller price p and buyer price q, observes
only whether trade occurred, receives gain from trade when the transaction
happens, and must keep cumulative realized profit non-negative (GBB). The
paper’s main positive result is a soft-O(T^(3/4)) regret guarantee under a
bounded joint valuation density. Its algorithm has three phases: profit
collection, compressed exploration, and constrained bandit optimization.

## Claim-by-claim result

| Claim | Paper statement audited | Verdict | How the result is produced |
| --- | --- | --- | --- |
| 1 | Theorem 4.1: Algorithm 1 is globally budget balanced and achieves soft-O(T^(3/4)) regret under bounded density | **BLOCKED** | verify_bt.py::run_claim_1 checks Appendix-F exponents and theorem dependencies, but the source omits the Profit-Max nontermination case, the promised Lemma 7.2 proof, and a confidence split. The million-round diagnostic also never reached phases 2–3. |
| 2 | Theorem 3.1: without bounded density, every algorithm has an Omega(T) hard instance | **VERIFIED WITH DISCLOSED SOURCE REPAIR** | verify_bt.py::run_claim_2 enumerates the four-atom action cells, solves exact GBB LPs with and without the needle, and applies Yao feedback-history packing. It uses the +epsilon atom shown in Figure 1 and the Section 2 price ordering; the appendix-literal -epsilon construction is retained as a rejected negative control. |
| 3 | Lemmas 5.1–5.2: directed K-by-K discretization has O(log(T)/K) comparator loss under bounded density | **VERIFIED SCOPED** | verify_bt.py::run_claim_3 compares dense and nested-grid GBB comparator LPs for three analytic bounded-density environments, checks directed projection on feasible zero-profit mixtures, and cross-checks selected LPs with SciPy HiGHS. No online regret is included. |
| 4 | Lemmas 7.1–7.2: conditional Profit-Max phase regret is soft-O(beta + T/K + sqrt(KT log(1/delta))) | **VERIFIED SCOPED** | verify_bt.py::run_claim_4 runs the actual Exp3 Profit-Max phase over four 64x horizons, two budget coefficients, and 12 seeds. All 96 conditional runs reached beta; the largest normalized regret was 0.07197. |
| 5 | Lemmas 8.1–8.2: Algorithm 2 estimates all K-squared GFT components in exactly 2KN rounds | **VERIFIED SCOPED** | verify_bt.py::run_claim_5 executes the sample-reuse exploration at K = 8, 16, 32 with 128 trials per configuration, checks simultaneous confidence failures, exact round counts, and the GFT = L + R + PRO identity. |
| 6 | Lemma 9.1: constrained UCB has soft-O(K sqrt(T log(1/delta))) regret and profit shortfall | **VERIFIED SCOPED** | verify_bt.py::run_claim_6 isolates Algorithm 3 with exact L/R biases, sweeps T over 64x through 131072 and K over 4x, and checks regret, profit shortfall, slopes, and the negative-profit-arm control. |

The authoritative machine-readable results are under
.openresearch/artifacts/claim_1/ through claim_6/. The cumulative campaign
summary is [.openresearch/artifacts/campaign_summary.json](.openresearch/artifacts/campaign_summary.json).

## Reproduce the evidence

The fixed command used on every experiment node is:

~~~text
uv sync --frozen && .venv/bin/python repro/src/verify_bt.py
~~~

The command writes claim contracts, source audits, methods, raw JSON/CSV,
primary verifier output, independent checker output, negative controls,
provenance, and limitations. A verified contract requires the primary verifier
to pass, the negative control to fail, and the independent checker to pass.
The recorded winning run used Python 3.12.11 on a local Apple M2 CPU. No GPU
or Hugging Face compute was used.

Read the [technical report](reports/bilateral-trade-reproduction/report.md)
for the derivations, finite results, source ambiguities, and the reason Claim 1
remains blocked. The [Molab notebook](notebooks/bilateral_trade_reproduction.py)
is a presentation layer and does not rerun the expensive formal campaign.

## Code and evidence map

- repro/src/bilateral.py — analytic valuation environments, GFT/profit
  expectations, GBB LPs, grids, Profit-Max, exploration, and constrained UCB.
- repro/src/verify_bt.py — runs Claims 1–6, records provenance, and writes the
  durable evidence artifacts.
- repro/src/claim_verifier.py — primary fail-closed claim checks.
- repro/src/independent_checker.py — independent slope, LP, confidence, scale,
  and round-count checks.
- .openresearch/artifacts/ — authoritative per-claim evidence.
- release/hf_space_delta/ — text-only Hugging Face candidate overlay and
  preserved protected evidence.
- outputs/ — legacy baseline output plus a navigation note; it is not the
  authoritative current verdict location.

## Branches and experiment lineage

The public branch names are normalized from the original orx refs. The full
old-to-new mapping and historical tips are in
[BRANCH_AUDIT.md](BRANCH_AUDIT.md).

| Clean branch | Purpose |
| --- | --- |
| [main](https://github.com/MachineLearning-Nerd/icml26-online-bilateral-trade/tree/main) | Public README, report, notebook, and preserved evidence |
| [research/frozen-judged-baseline](https://github.com/MachineLearning-Nerd/icml26-online-bilateral-trade/tree/research/frozen-judged-baseline) | Reproduce the original judged toy harness as a negative control |
| [research/faithful-claim-contracts](https://github.com/MachineLearning-Nerd/icml26-online-bilateral-trade/tree/research/faithful-claim-contracts) | First direct implementations and claim contracts |
| [research/feasible-projection-phase](https://github.com/MachineLearning-Nerd/icml26-online-bilateral-trade/tree/research/feasible-projection-phase) | Feasible projection audit and million-round phase diagnostic |
| [research/theorem-4-1-proof-gaps](https://github.com/MachineLearning-Nerd/icml26-online-bilateral-trade/tree/research/theorem-4-1-proof-gaps) | Cumulative evidence and explicit Claim 1 proof-gap audit |
| [release/candidate-report](https://github.com/MachineLearning-Nerd/icml26-online-bilateral-trade/tree/release/candidate-report) | Final report, preserved logbook, and publication candidate |

## Publication status

The text-only candidate was published to the existing
DineshAI/M52jcbntdB Space at revision
4c4e95f577956c896d3286ae303237b856f5ae6d. The historical live score remains
2/12 at judge revision a3bd9c2e315f02cb584c634c58036238f87289f5, and the newer
candidate is awaiting evaluation. See [GATE_READY.md](GATE_READY.md) and
[publication_gate.json](publication_gate.json) for the conservative release
state.

## Citation

~~~bibtex
@article{lunghi2026stronger,
  title   = {A Stronger Benchmark for Online Bilateral Trade: From Fixed Prices to Distributions},
  author  = {Lunghi, Anna and Piccinato, Mattia and Castiglioni, Matteo and Marchesi, Alberto},
  journal = {arXiv preprint arXiv:2602.05681},
  year    = {2026},
  note    = {To appear at ICML 2026}
}
~~~

## Acknowledgement

Thank you to Anna Lunghi, Mattia Piccinato, Matteo Castiglioni, and Alberto
Marchesi for making this careful study of online bilateral trade available.
The paper’s explicit separation of budget balance, one-bit feedback, and the
GBB benchmark made it possible to audit the algorithm phase by phase and to
separate source-level gaps from finite experimental behavior.

This reproduction audit is maintained by
[MachineLearning-Nerd](https://github.com/MachineLearning-Nerd).
