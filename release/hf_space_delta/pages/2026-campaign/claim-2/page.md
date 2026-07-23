# Claim 2 — VERIFIED

**Paper claim.** Without bounded density, every algorithm has an `Omega(T)` instance via the needle-in-the-haystack construction (Theorem 3.1).

The check enumerates the distinct action/feedback cells of the four-atom hard family and solves the GBB comparator LP with and without the needle action:

- full optimum: `0.0833333333`
- no-needle optimum: `0.0781221395`
- constant gap: `0.0052111938 > 1/200`
- needle GFT: `1/8`
- needle profit: `-1/8`
- feedback-history identification upper bound: `1/8`

The manuscript is internally inconsistent. The primary certificate uses the `+epsilon` fourth atom drawn in Figure 1 and the seller/buyer coordinate order from Section 2. The appendix-literal `-epsilon` construction is preserved as the negative control and is rejected.

## Evidence files

- [Contract](../../../evidence/2026/claim_2/claim_contract.json)
- [Source audit](../../../evidence/2026/claim_2/source_audit.md)
- [Method](../../../evidence/2026/claim_2/method.md)
- [Exact LP and packing result](../../../evidence/2026/claim_2/result.json)
- [Primary verifier](../../../evidence/2026/claim_2/verifier_output.txt)
- [Independent checker](../../../evidence/2026/claim_2/independent_checker_output.txt)
- [Rejected appendix-literal control](../../../evidence/2026/claim_2/negative_control_output.txt)

