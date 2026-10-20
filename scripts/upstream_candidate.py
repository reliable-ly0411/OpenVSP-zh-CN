#!/usr/bin/env python3
"""Read-only deduplication of staged, history-preserving upstream candidates."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], text=True, capture_output=True, check=check)


def candidate_branch(base: str, upstream: str, source_ref: str) -> str:
    for sha in (base, upstream):
        if not re.fullmatch(r"[0-9a-f]{40}", sha):
            raise ValueError("Candidate source identities must be exact commit SHAs")
    # Include the explicit ref so a main snapshot cannot be reused as a tag
    # candidate. The base already binds the trusted workflow/tooling revision.
    ref_digest = hashlib.sha256(source_ref.encode("utf-8")).hexdigest()[:16]
    return f"automation/upstream-source-{base}-{upstream}-{ref_digest}"


def inspect_candidate(upstream: str, source_ref: str, remote: str = "origin") -> dict:
    base = git("rev-parse", "HEAD").stdout.strip()
    branch = candidate_branch(base, upstream, source_ref)
    target = f"refs/heads/{branch}"
    lookup = git("ls-remote", "--exit-code", "--heads", remote, target, check=False)
    if lookup.returncode == 2 and not lookup.stdout.strip():
        return {"branch": branch, "changed": "true", "sha": ""}
    if lookup.returncode:
        raise RuntimeError(f"Candidate lookup failed: {lookup.stderr.strip()}")
    lines = lookup.stdout.strip().splitlines()
    if len(lines) != 1 or len(lines[0].split()) != 2:
        raise ValueError("Ambiguous candidate branch identity")
    sha, ref = lines[0].split()
    if ref != target or not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise ValueError("Unexpected candidate branch identity")
    # FETCH_HEAD only, no local/remote branch update and no merged-tree code.
    git("fetch", "--no-tags", remote, target)
    fetched = git("rev-parse", "FETCH_HEAD^{commit}").stdout.strip()
    if fetched != sha:
        raise ValueError("Candidate changed during read; refusing to reuse")
    parents = git("show", "-s", "--format=%P", sha).stdout.strip().split()
    if parents != [base, upstream]:
        raise ValueError("Candidate parents do not match exact source identities")
    expected_tree = git("write-tree").stdout.strip()
    actual_tree = git("rev-parse", f"{sha}^{{tree}}").stdout.strip()
    if expected_tree != actual_tree:
        raise ValueError("Candidate tree differs from the checked staged source")
    return {"branch": branch, "changed": "false", "sha": sha}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", required=True)
    args = parser.parse_args()
    print(json.dumps(inspect_candidate(args.upstream, os.environ["UPSTREAM_SOURCE_REF"])))


if __name__ == "__main__":
    main()
