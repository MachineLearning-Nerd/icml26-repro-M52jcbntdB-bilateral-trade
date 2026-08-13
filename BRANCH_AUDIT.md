# Branch audit and cleanup map

The repository started with master and five experiment branches using the
orx/ prefix. They are mapped below to descriptive public names. Historical
tips are the pre-cleanup tips recorded before the documentation commit and
identity normalization.

| Old ref | Clean ref | Historical tip | Role |
| --- | --- | --- | --- |
| master | main | dbee6cc601de3c34f0fb70499af38cd4a1664359 | Public presentation surface |
| orx/frozen-judged-baseline | research/frozen-judged-baseline | 4f676b56e4e7397749711ba55b3e5f043f86f34d | Frozen toy-harness negative control |
| orx/faithful-claim-contracts-and-phase-implementatio | research/faithful-claim-contracts | 4ef0e710db93352fbc11f00741d013d4c570fba4 | First direct implementations and contracts |
| orx/feasible-projection-audit-and-asymptotic-phase-c | research/feasible-projection-phase | 0dc2a8a6d7239d1732ad1d06ed1c1c38cc06e590 | Projection audit and phase diagnostic |
| orx/compositional-theorem-4-1-certificate | research/theorem-4-1-proof-gaps | d171f3cc28c2a117061697e79fc09110008f40ab | Cumulative Claim 1 proof-gap audit |
| orx/release-candidate-report-and-preserved-logbook | release/candidate-report | c2f468be7d0d6ffe7f846167e6692f790bd444b0 | Final report and publication package |

All six final branches are intentional: main is the public surface, four
research branches preserve the audit lineage, and one release branch preserves
the publication package.

## Identity normalization

After branch cleanup, all reachable commits are rewritten to the public
maintainer identity:

- Name: MachineLearning-Nerd
- Email: MachineLearning-Nerd@users.noreply.github.com

No co-author lines or tool signatures are added.
