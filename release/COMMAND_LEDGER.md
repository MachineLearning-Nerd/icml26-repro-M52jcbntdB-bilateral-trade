# Reproduction command ledger

This ledger records the substantive commands used to audit, execute, validate, and
package the 2026 claim-by-claim reproduction. Repeated polling commands are shown
once with the number of repetitions because they are observationally identical.
Secrets, credentials, generated wrappers, and tool-internal implementation
commands are intentionally excluded.

## Startup and source audit

```text
orx skill
orx skill orx-experiment-tree
orx skill orx-evidence
orx skill orx-git
orx skill orx-compute
orx projects --json
orx project view 1e36f712-56b4-4325-ae0b-21bc7fba3b6c
orx runs 1e36f712-56b4-4325-ae0b-21bc7fba3b6c
git branch -a
git rev-parse HEAD
git rev-parse master
git rev-parse origin/master
git status --short
df -h .
env | sed 's/=.*//' | sort
curl --fail --location --user-agent 'OpenResearch-Reproduction/1.0 (paper source audit)' https://ar5iv.labs.arxiv.org/html/2602.05681
curl --fail --location --user-agent 'OpenResearch-Reproduction/1.0 (paper source audit)' https://arxiv.org/e-print/2602.05681
shasum -a 256 paper_2602.05681_ar5iv.html paper_2602.05681_eprint.tar
```

The exact judged Space revision and the live verdict dataset were downloaded
read-only with `huggingface_hub` at revisions
`a3bd9c2e315f02cb584c634c58036238f87289f5` and
`e67eaebfaf8c1f36c63c3fb384af562a85f261cb`, respectively. The verdict was
selected by the exact predicate `space_id == "DineshAI/M52jcbntdB"`. The frozen
downloads, hashes, and selection result are in the dashboard startup-audit
directory.

## Fixed environment and experiment tree

```text
orx create-experiment 1e36f712-56b4-4325-ae0b-21bc7fba3b6c --title "Frozen judged baseline" --run-command "uv sync --frozen && .venv/bin/python repro/src/verify_bt.py"
orx exp run 8ac37a5a-7ea4-42aa-98f9-80cc44bbb505 --backend local
orx exp wait 8ac37a5a-7ea4-42aa-98f9-80cc44bbb505 --timeout 480
orx logs c8fbcae4-8ca2-40e0-a5b5-059d733bb765

orx create-experiment 1e36f712-56b4-4325-ae0b-21bc7fba3b6c --title "Faithful claim contracts and phase implementations" --parent 8ac37a5a-7ea4-42aa-98f9-80cc44bbb505
orx exp run 56a34b24-e858-4392-829c-23238e8c648d --backend local
orx exp wait 56a34b24-e858-4392-829c-23238e8c648d --timeout 480
orx logs b12de041-539b-4b01-bb67-9fb1597ebf80

orx create-experiment 1e36f712-56b4-4325-ae0b-21bc7fba3b6c --title "Feasible projection audit and asymptotic phase calibration" --parent 56a34b24-e858-4392-829c-23238e8c648d
orx exp run 89aa08e0-921c-4a9b-9a67-66bbcb245981 --backend local
orx exp wait 89aa08e0-921c-4a9b-9a67-66bbcb245981 --timeout 480
orx logs 9bb95a2e-7f29-42cb-bca4-be27f227d159

orx create-experiment 1e36f712-56b4-4325-ae0b-21bc7fba3b6c --title "Compositional Theorem 4.1 certificate" --parent 89aa08e0-921c-4a9b-9a67-66bbcb245981
orx exp run 13af05bb-88d6-402b-924d-237c983e8322 --backend local
orx exp wait 13af05bb-88d6-402b-924d-237c983e8322 --timeout 480
orx logs 5c486d91-dac3-478b-bb5d-84c4ef8400ab

orx create-experiment 1e36f712-56b4-4325-ae0b-21bc7fba3b6c --title "Release candidate report and preserved logbook" --parent 13af05bb-88d6-402b-924d-237c983e8322
orx exp run a3eb0269-7eef-44a2-a26e-554829b8867d --backend local
orx exp wait a3eb0269-7eef-44a2-a26e-554829b8867d --timeout 480
orx logs <release-run-id>
```

Each wait command above was repeated at five-to-eight-minute intervals until
the run reached a terminal state. The fixed command was never varied:

```text
uv sync --frozen && .venv/bin/python repro/src/verify_bt.py
```

## Git publication of experiment inputs

For every experiment node, the branch from `orx exp status` was checked out,
the scoped changes were inspected, and the exact input commit was pushed before
launch:

```text
git fetch origin
git checkout <experiment-branch>
git status --short
git diff --check
git add <scoped-files>
git commit -m <experiment-summary>
git push origin <experiment-branch>
git rev-parse HEAD
git status --short
```

No completed experiment branch was rebased, merged, or rewritten.

## Release validation

```text
uv run --frozen python -m py_compile repro/src/verify_bt.py release/prepare_hf_candidate.py reports/bilateral-trade-reproduction/generate_report_assets.py notebooks/bilateral_trade_reproduction.py
uv run --frozen marimo check notebooks/bilateral_trade_reproduction.py
uv run --frozen marimo export html notebooks/bilateral_trade_reproduction.py -o /tmp/bilateral_trade_reproduction.html
uv run --frozen python reports/bilateral-trade-reproduction/generate_report_assets.py
uv run --frozen python release/prepare_hf_candidate.py
git diff --cached --check
```

The candidate builder produced and validated:

```text
release/manifests/HF_UPLOAD_ALLOWLIST.txt
release/manifests/HF_UPLOAD_MANIFEST.sha256-bytes-path.txt
release/manifests/OLD_NEW_SUBSET_CHECK.json
```

No Hugging Face publication command has been executed. Publication remains
gated on explicit user approval.
