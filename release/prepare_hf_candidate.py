"""Build and validate the additive, text-only Hugging Face Space candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys


ALLOWED_SUFFIXES = {".csv", ".json", ".md", ".txt"}
SECRET_PATTERNS = {
    "generic_api_key": re.compile(r"(?i)(api[_-]?key|access[_-]?token|secret)\s*[:=]\s*[\"']?[A-Za-z0-9_\-]{20,}"),
    "github_token": re.compile(r"\b(?:ghp|github_pat)_[A-Za-z0-9_]{20,}\b"),
    "hf_token": re.compile(r"\bhf_[A-Za-z0-9]{20,}\b"),
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def files(root: Path) -> dict[str, Path]:
    return {
        path.relative_to(root).as_posix(): path
        for path in root.rglob("*")
        if path.is_file() and ".git" not in path.relative_to(root).parts
    }


def fail(message: str) -> None:
    raise RuntimeError(message)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protected", type=Path, required=True)
    parser.add_argument("--delta", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--manifest-dir", type=Path, required=True)
    args = parser.parse_args()

    protected = args.protected.resolve()
    delta = args.delta.resolve()
    candidate = args.candidate.resolve()
    manifest_dir = args.manifest_dir.resolve()
    if not protected.is_dir() or not delta.is_dir():
        fail("protected source or delta directory is missing")
    if candidate.exists():
        fail("candidate already exists; pass a new empty target")

    shutil.copytree(protected, candidate, ignore=shutil.ignore_patterns(".git"))
    for relative, source in files(delta).items():
        target = candidate / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)

    old = files(protected)
    new = files(candidate)
    missing = sorted(set(old) - set(new))
    if missing:
        fail(f"candidate omits protected paths: {missing}")
    changed_old = sorted(path for path in old if digest(old[path]) != digest(new[path]))
    if changed_old != ["logbook.json"]:
        fail(f"unexpected changed protected paths: {changed_old}")
    old_pages = [path for path in old if path.startswith("pages/")]
    changed_pages = [path for path in old_pages if digest(old[path]) != digest(new[path])]
    if changed_pages:
        fail(f"protected page content changed: {changed_pages}")

    delta_files = files(delta)
    secret_hits: list[tuple[str, str]] = []
    for relative, path in delta_files.items():
        if path.suffix.lower() not in ALLOWED_SUFFIXES:
            fail(f"non-text suffix in upload delta: {relative}")
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise RuntimeError(f"non-UTF-8 upload file: {relative}") from exc
        if "\x00" in text:
            fail(f"NUL byte in upload file: {relative}")
        if path.suffix.lower() == ".json":
            json.loads(text)
        for name, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                secret_hits.append((relative, name))
    if secret_hits:
        fail(f"secret-pattern hits (paths and rule names only): {secret_hits}")

    logbook = json.loads((candidate / "logbook.json").read_text())

    def page_entries(node: dict) -> list[str]:
        output = [node["file"]]
        for child in node.get("children", []):
            output.extend(page_entries(child))
        return output

    referenced_pages = page_entries(logbook["root"])
    absent_pages = sorted(path for path in referenced_pages if path not in new)
    if absent_pages:
        fail(f"logbook references missing pages: {absent_pages}")

    manifest_dir.mkdir(parents=True, exist_ok=True)
    allowlist = sorted(delta_files)
    (manifest_dir / "HF_UPLOAD_ALLOWLIST.txt").write_text(
        "\n".join(allowlist) + "\n"
    )
    manifest_lines = [
        f"{digest(delta_files[path])}  {delta_files[path].stat().st_size}  {path}"
        for path in allowlist
    ]
    (manifest_dir / "HF_UPLOAD_MANIFEST.sha256-bytes-path.txt").write_text(
        "\n".join(manifest_lines) + "\n"
    )
    subset = {
        "protected_revision": "a3bd9c2e315f02cb584c634c58036238f87289f5",
        "protected_path_count": len(old),
        "candidate_path_count": len(new),
        "missing_protected_paths": missing,
        "changed_protected_paths": changed_old,
        "changed_protected_pages": changed_pages,
        "protected_logbook_copy": (
            "evidence/2026/protected/"
            "logbook_a3bd9c2e315f02cb584c634c58036238f87289f5.json"
        ),
        "upload_file_count": len(allowlist),
        "all_uploads_utf8_text": True,
        "json_valid": True,
        "secret_pattern_hits": [],
        "logbook_references_valid": True,
    }
    (manifest_dir / "OLD_NEW_SUBSET_CHECK.json").write_text(
        json.dumps(subset, indent=2, sort_keys=True) + "\n"
    )
    print(
        json.dumps(
            {
                "candidate": str(candidate),
                "protected_paths": len(old),
                "candidate_paths": len(new),
                "upload_files": len(allowlist),
                "changed_protected_paths": changed_old,
                "status": "PASS",
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"candidate validation failed: {exc}", file=sys.stderr)
        sys.exit(1)
