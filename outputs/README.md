# Output provenance

The root verdict files are retained as historical evidence from the original
judged baseline. Their six boolean passes were toy/proxy checks and correspond
to the live judge's 2/12 assessment; they are not the current claim verdicts.

The current claim-by-claim evidence is authoritative under:

- .openresearch/artifacts/campaign_summary.json
- .openresearch/artifacts/claim_1/ through claim_6/
- GATE_READY.md
- publication_gate.json

Recreate the formal evidence with:

~~~text
uv sync --frozen && .venv/bin/python repro/src/verify_bt.py
~~~
