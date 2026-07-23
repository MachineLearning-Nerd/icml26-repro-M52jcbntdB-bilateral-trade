# Evidence and release manifest

## Cumulative formal result

| Claim | Primary verifier | Negative control | Independent checker | Verdict |
|---:|---:|---:|---:|---|
| 1 | 1 | 1 | 0 | BLOCKED |
| 2 | 0 | 1 | 0 | VERIFIED |
| 3 | 0 | 1 | 0 | VERIFIED |
| 4 | 0 | 1 | 0 | VERIFIED |
| 5 | 0 | 1 | 0 | VERIFIED |
| 6 | 0 | 1 | 0 | VERIFIED |

Negative controls are required to exit nonzero.

## Provenance

- Git SHA: `d171f3cc28c2a117061697e79fc09110008f40ab`
- Fixed command: `uv sync --frozen && .venv/bin/python repro/src/verify_bt.py`
- Formal cumulative runtime: `834.870674 s`
- Python: `3.12.11`
- Dependency manager: `uv`, frozen lock
- Compute: local CPU
- Hugging Face CPU usage: none
- GPU usage: none

[Campaign summary JSON](../../../evidence/2026/campaign_summary.json)

The exact upload allowlist, SHA-256 manifest, secret scan, JSON validation, and old/new subset proof are generated before publication. Publication requires explicit user approval.
