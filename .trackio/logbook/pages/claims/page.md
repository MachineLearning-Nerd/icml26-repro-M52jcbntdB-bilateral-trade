# Claims


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_0be166d3aded", "created_at": "2026-07-21T22:57:09+00:00", "title": "Claims to reproduce"}
-->
## Claims to reproduce

1. Under a bounded-density assumption on buyer/seller valuation distributions, the proposed algorithm achieves Õ(T^{3/4}) regret against the best fixed price distribution satisfying Global Budget Balance (GBB) (Theorem 4.1).
2. Without the bounded-density assumption, any algorithm suffers Ω(T) linear regret against the GBB benchmark, shown via a needle-in-the-haystack construction proving discretization is impossible (Theorem 3.1).
3. Bounded density lets the learner restrict to a uniform K×K price grid with discretization error O(log(T)/K), showing no separation between one-dimensional SBB learning and two-dimensional GBB distribution learning (Lemma 5.1, Lemma 5.2).
4. In the profit-collection phase, regret is bounded by Õ(β + T/K + √(KT)) where β is the accumulated budget (Lemma 7.1, Lemma 7.2).
5. The pure-exploration phase estimates all K² price-pair outcomes using only 2K exploration samples via sample reuse across the observable/non-observable GFT decomposition (Lemma 8.1, Lemma 8.2).
6. The UCB-based constrained-bandit optimization phase achieves Õ(K√T) regret while preserving GBB feasibility, combining with the other phases to yield the overall Õ(T^{3/4}) rate (Lemma 9.1, Theorem 4.1).
