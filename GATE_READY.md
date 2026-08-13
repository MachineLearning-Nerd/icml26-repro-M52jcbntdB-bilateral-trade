# Evidence and publication gate

## Current state

- **EVIDENCE_RELEASE_GATE:** PASSED
- **PUBLICATION_GATE:** NOT_READY
- **Evidence verdicts:** Claims 2–6 VERIFIED within their contracts; Claim 1 BLOCKED
- **Hugging Face status:** text-only candidate published; awaiting live judge
- **Recorded live score:** 2/12

The evidence-release gate passed the cumulative claim suite, independent
checkers, negative controls, source and artifact checks, protected-file
preservation checks, byte manifests, JSON validation, and secret scanning.

The strict publication gate remains NOT_READY. Claim 1 still has three
source-level proof gaps and the large end-to-end diagnostic never reached the
paper's exploration and constrained-UCB phases. Claims 2–6 are finite or
conditional evidence contracts, not a replacement for a formal proof or a
fresh live evaluation.

## Candidate

- **Space:** DineshAI/M52jcbntdB
- **Published revision:** 4c4e95f577956c896d3286ae303237b856f5ae6d
- **Previous judged revision:** a3bd9c2e315f02cb584c634c58036238f87289f5
- **Previous score:** 2/12
- **Candidate judged:** no
- **Candidate type:** text-only additive release
- **Hugging Face compute:** none

## Claim gate

| Claim | Status | Scope and limitation |
| --- | --- | --- |
| 1 | BLOCKED | Appendix-F exponent arithmetic passes, but the nontermination case, Lemma 7.2 proof, and total confidence allocation are unresolved; the finite rollout is phase-incomplete. |
| 2 | VERIFIED WITH DISCLOSED REPAIR | Exact GBB LP and Yao packing certificate; the Figure-1 +epsilon atom and Section-2 price ordering replace an inconsistent appendix transcription, which remains a rejected negative control. |
| 3 | VERIFIED SCOPED | Comparator-only bounded-density discretization audit; no online regret is inferred. |
| 4 | VERIFIED SCOPED | Conditional Profit-Max phase sweep; all tested runs reached beta, but this is not a proof of the missing source lemma. |
| 5 | VERIFIED SCOPED | Algorithm 2 sample-reuse and identity audit at K = 8, 16, 32 with 128 trials per configuration. |
| 6 | VERIFIED SCOPED | Algorithm 3 constrained-UCB scaling sweep with exact L/R biases, finite horizons, and negative-profit control. |

## Reproduction command

~~~text
uv sync --frozen && .venv/bin/python repro/src/verify_bt.py
~~~

The authoritative evidence is under .openresearch/artifacts/. The historical
baseline output under outputs/ is preserved but is not the current claim
verdict.
