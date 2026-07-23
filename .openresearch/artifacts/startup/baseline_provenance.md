# Frozen baseline provenance

- Required and observed GitHub baseline: `38a497c259d11d67e73ab9848bb27cc5b2d13029`
- Baseline experiment: `Frozen judged baseline`
- Baseline branch: `orx/frozen-judged-baseline`
- Repository command recovered from the tracked verification page:
  `.venv/bin/python repro/src/verify_bt.py`
- Fixed OpenResearch command:
  `uv sync --frozen && .venv/bin/python repro/src/verify_bt.py`
- Compute: local Apple M2 CPU, 8 logical CPUs, 16 GiB RAM
- Environment: one repository-local `.venv`, Python 3.12.11, dependencies
  resolved by `uv.lock`

The additional `uv sync --frozen` is the reproducible setup required for a
fresh OpenResearch clone. The scientific entrypoint is unchanged. This root
exists only to reproduce the judged toy harness; its outputs must not be
presented as rigorous verification.

At startup the project tree and run table were empty, the project command was
unset, the worktree was clean and detached at the required SHA, and no runs
belonged to this project. Other OpenResearch jobs were active on the shared
host and were left untouched. Free disk was 18 GiB.

The exact judged Space `DineshAI/M52jcbntdB@a3bd9c2e315f02cb584c634c58036238f87289f5`
was downloaded before any candidate was created. Its 17 tracked files are
listed in `protected_space_manifest.sha256-bytes-path.txt`.

The live verdict dataset `ICML-2026-agent-repro/verdicts` was resolved at
revision `e67eaebfaf8c1f36c63c3fb384af562a85f261cb`. The downloaded
`verdicts.json` has SHA-256
`3fccda875cdafc1789d535eed54e2e2fcf40163ca15bcae1633416f2cfd1a825`.
Filtering by exact equality
`space_id == "DineshAI/M52jcbntdB"` returned one record, preserved as
`live_verdict_exact_space.json`.
