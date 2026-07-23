# Claim 1 source audit

Primary source: arXiv:2602.05681v1 / `https://ar5iv.labs.arxiv.org/html/2602.05681#S4.Thmtheorem1; proof #A6; Algorithm #alg1`.

Exact imported claim: Under bounded density, Algorithm 1 is GBB and has soft-O(T^(3/4)) regret (Theorem 4.1).

The full shared assumptions, quantifiers, source hashes, and manuscript ambiguities are recorded in `../startup/source_audit.md`. This claim uses the seller-price `p`, buyer-price `q` convention from Section 2.

## Unresolved source obligations

- Appendix F explicitly assumes the `tau_2 < T` case and does not supply the complementary Profit-Max-nontermination derivation.
- Appendix C promises omitted Section 7 proofs but contains only the proof of Lemma 7.1; no proof of Lemma 7.2 is present.
- Lemmas 8.2 and 9.1 each state a `1-delta` event, while Theorem 4.1 also states `1-delta`; Algorithm 1 does not specify a confidence split.
These omissions prevent a rigorous VERIFIED verdict even though the power-counting composition is exactly `T^(3/4)` up to logarithms.
