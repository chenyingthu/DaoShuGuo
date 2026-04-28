#!/usr/bin/env python3
"""Smoke-verify the repo-local DaoShuGuo Pi package artifacts."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    required = [
        REPO_ROOT / "pi-packages/daoshuguo-research-loop/package.json",
        REPO_ROOT / "pi-packages/daoshuguo-research-loop/README.md",
        REPO_ROOT / "pi-packages/daoshuguo-research-loop/extensions/daoshuguo-research-loop/index.ts",
        REPO_ROOT / "pi-packages/daoshuguo-research-loop/skills/daoshuguo-research-create/SKILL.md",
        REPO_ROOT / "docs/pi-runtime-setup-note.md",
        REPO_ROOT / "docs/research-loop-file-contract.md",
    ]
    missing = [str(path.relative_to(REPO_ROOT)) for path in required if not path.exists()]
    if missing:
        raise RuntimeError(f"missing Pi package smoke artifacts: {missing}")
    extension_text = (REPO_ROOT / "pi-packages/daoshuguo-research-loop/extensions/daoshuguo-research-loop/index.ts").read_text(encoding="utf-8")
    for required_tool in [
        "init_research_task",
        "log_research_iteration",
        "record_skill_trial",
        "record_cognition_constraint",
        "record_iteration_review",
        "run_task003_trial",
    ]:
        if required_tool not in extension_text:
            raise RuntimeError(f"missing tool definition in extension: {required_tool}")
    print("Pi package smoke verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
