# Primary-source audit

Retrieved at `2026-07-23T12:34:58Z` with the explicit browser User-Agent
`OpenResearch-Reproduction-Audit/1.0 (contact: research-local)`.

| Source | URL | Bytes | SHA-256 |
|---|---|---:|---|
| ar5iv HTML | `https://ar5iv.labs.arxiv.org/html/2602.05681` | 520314 | `84fc667da4f12a0ebde1974217d44cd5a6d22c95652481ca9d1e9d66816cbabb` |
| arXiv e-print | `https://export.arxiv.org/e-print/2602.05681` | 79968 | `038ab6f5e4660223cf5c009dc78c6735b7a2661687188d4ce518664ddbdde7df` |

The retrieved manuscript identifies arXiv `2602.05681v1`, dated 5 February
2026. The exact downloaded files are preserved in the OpenResearch Files
directory under `project/startup-audit/`.

## Anchors

- Problem formulation and feedback: `#S2`
- Theorem 3.1 and hard-instance construction: `#S3.Thmtheorem1`, proof `#A1`
- Theorem 4.1: `#S4.Thmtheorem1`, proof `#A6`
- Lemma 5.1: `#S5.Thmtheorem1`, proof `#A2`
- Lemma 5.2: `#S5.Thmtheorem2`, proof `#A2`
- Algorithm 1: `#alg1`
- Lemma 7.1: `#S7.Thmtheorem1`, proof `#A3`
- Lemma 7.2: `#S7.Thmtheorem2`
- Lemma 8.1: `#S8.Thmtheorem1`, proof `#A4`
- Lemma 8.2: `#S8.Thmtheorem2`, Algorithm 2 `#alg2`
- Lemma 9.1: `#S9.Thmtheorem1`, proof `#A5`, Algorithm 3 `#alg3`
- Revenue Maximization / Profit-Max: `#alg4`

## Shared model and exact quantifiers

At every round, `(s_t,b_t)` is drawn i.i.d. from one fixed joint distribution
on `[0,1]^2`. The learner posts seller price `p_t` and buyer price `q_t` before
seeing the valuations and receives one-bit trade feedback. Gain from trade is
`(b_t-s_t) 1{s_t<=p_t,b_t>=q_t}` and profit is
`(q_t-p_t) 1{s_t<=p_t,b_t>=q_t}`. The comparator is the best fixed
distribution over price pairs whose expected profit is nonnegative. The
algorithm itself must have nonnegative realized cumulative profit (GBB).

Theorem 3.1 quantifies over every natural horizon and every learning algorithm:
there exists a stochastic instance, without a bounded-density assumption, for
which expected regret is `Omega(T)`. Its proof uses the four-atom
`D_{epsilon,u}` family and requires locating a width-`epsilon` Region I.

Theorem 4.1 assumes the valuation distribution admits a density bounded above
by a finite `sigma`. For every `delta` in `(0,1)`, with probability at least
`1-delta`, Algorithm 1 is GBB and has soft-`O(T^(3/4))` regret. The proof sets
`K=T^(1/4)`, `N=T^(1/2)`, and
`beta=soft-Theta(NK + K sqrt(T log(1/delta)) + T/K)`.

Lemma 5.1 quantifies over every feasible price distribution and bounds the GFT
loss and expected-profit deficit of its directed grid projection by
`2 sigma/(K-1)`. Lemma 5.2 quantifies over every natural `K` and bounds the
per-round comparator gap `OPT-OPT_K` by `O(log(T)/K)`.

Lemma 7.1 gives
`OPT <= 16 log(T) sup_{(p,q) in F_K} PRO(p,q) + 10/K`.
Lemma 7.2 is conditional: with probability at least `1-delta`, if Profit-Max
reaches target budget `beta` at round `tau<=T`, its phase regret is
soft-`O(beta + T/K + sqrt(KT log(1/delta)))`.

Lemma 8.1 is an exact expectation identity decomposing GFT into `L + R + PRO`.
Lemma 8.2 is conditional on Algorithm 2 finishing before `T`: simultaneously
for all `K^2` grid pairs, both empirical errors are at most
`sqrt(log(4K^2/delta)/N)` with probability at least `1-delta`, using `2KN`
rounds.

Lemma 9.1 quantifies over every feasible grid distribution `gamma`. If
Algorithm 3 starts at `tau_0`, then with probability at least `1-delta`, both
its biased-reward regret and its cumulative profit shortfall are
soft-`O(K sqrt(T log(1/delta)))`.

## Source ambiguities retained for audit

The manuscript contains internal inconsistencies in the hard-instance
description: the main text and appendix differ on one atom; Appendix A uses an
undefined `v` in Region II; and some Region III coordinates appear transposed
relative to the stated seller/buyer price convention. Reproduction code must
state which appendix definition it implements and must not silently repair
these issues.

Algorithm 2's pseudocode uses `tau=t+N` together with `while t<=tau`, which is
off by one if read literally. The theorem and prose unambiguously state `N`
samples per row/column and `2KN` total rounds; the claim contract therefore
uses the theorem's `2KN` quantifier and records the pseudocode discrepancy.
