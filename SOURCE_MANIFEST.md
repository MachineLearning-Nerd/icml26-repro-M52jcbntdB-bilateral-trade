# Paper source manifest

## Pinned paper

- **Title:** A Stronger Benchmark for Online Bilateral Trade: From Fixed Prices to Distributions
- **Authors:** Anna Lunghi; Mattia Piccinato; Matteo Castiglioni; Alberto Marchesi
- **Version:** arXiv:2602.05681v1
- **Canonical page:** https://arxiv.org/abs/2602.05681
- **Rendered source used by the audit:** https://ar5iv.labs.arxiv.org/html/2602.05681
- **Source archive:** https://export.arxiv.org/e-print/2602.05681
- **Retrieved:** 2026-07-23T12:34:58Z
- **Rendered HTML bytes:** 520314
- **Rendered HTML SHA-256:** 84fc667da4f12a0ebde1974217d44cd5a6d22c95652481ca9d1e9d66816cbabb
- **Source archive bytes:** 79968
- **Source archive SHA-256:** 038ab6f5e4660223cf5c009dc78c6735b7a2661687188d4ce518664ddbdde7df

## Theorem and algorithm anchors

| Audit claim | Paper source | Anchor | Evidence producer |
| --- | --- | --- | --- |
| 1 | Theorem 4.1 | S4.Thmtheorem1; proof A6; Algorithm 1 | verify_bt.py::run_claim_1 |
| 2 | Theorem 3.1 | S3.Thmtheorem1; proof A1 | verify_bt.py::run_claim_2 |
| 3 | Lemmas 5.1–5.2 | S5.Thmtheorem1 and S5.Thmtheorem2; proof A2 | verify_bt.py::run_claim_3 |
| 4 | Lemmas 7.1–7.2 | S7.Thmtheorem1 and S7.Thmtheorem2; Algorithm 4 | verify_bt.py::run_claim_4 |
| 5 | Lemmas 8.1–8.2 | S8.Thmtheorem1 and S8.Thmtheorem2; Algorithm 2 | verify_bt.py::run_claim_5 |
| 6 | Lemma 9.1 | S9.Thmtheorem1; proof A5; Algorithm 3 | verify_bt.py::run_claim_6 |

## Source ambiguities retained

The manuscript's hard-instance text and figure disagree on one atom, Region I
coordinates are transposed relative to the seller/buyer convention, Appendix A
uses an undefined variable in Region II, and Algorithm 2 has a literal
tau=t+N/while-t<=tau off-by-one reading. The audit records these differences
and tests the appendix-literal version as a negative control rather than
silently changing the source.

## Citation

Lunghi, Anna, Mattia Piccinato, Matteo Castiglioni, and Alberto Marchesi.
“A Stronger Benchmark for Online Bilateral Trade: From Fixed Prices to
Distributions.” arXiv preprint arXiv:2602.05681, 2026. To appear at ICML 2026.
