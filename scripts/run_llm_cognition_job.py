#!/usr/bin/env python3
"""Run or dry-run an LLM cognition job."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} did not parse to object")
    return data


def load_prompt(job_path: Path) -> str:
    prompt_path = job_path.with_suffix(".prompt.md")
    if not prompt_path.exists():
        raise RuntimeError(f"missing prompt bundle: {prompt_path}")
    return prompt_path.read_text(encoding="utf-8")


def parse_json_response(text: str) -> dict[str, Any]:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise RuntimeError("response does not contain JSON object")
    payload = json.loads(text[start : end + 1])
    if not isinstance(payload, dict):
        raise RuntimeError("response JSON is not object")
    return payload


def default_output(job_id: str, role: str, input_refs: list[str]) -> dict[str, Any]:
    return {
        "job_id": job_id,
        "agent_role": role,
        "input_refs": input_refs,
        "interpretation_summary": "dry-run only; no LLM response generated",
        "evidence_used": [],
        "agreement_with_rule_baseline": "not_evaluated",
        "new_insights": [],
        "overclaim_warnings": [],
        "missing_evidence": [],
        "recommended_action": "run_with_llm",
        "confidence": "low",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a LLM cognition job.")
    parser.add_argument("job")
    parser.add_argument("--command", help="Command that accepts prompt on stdin and returns JSON.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output-dir", default="agents/cognition/outputs")
    args = parser.parse_args()

    job_path = REPO_ROOT / args.job
    job = load_json(job_path)
    prompt = load_prompt(job_path)
    output_dir = REPO_ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_path = output_dir / f"{job['job_id']}.raw.txt"
    parsed_path = output_dir / f"{job['job_id']}.json"
    prompt_copy = output_dir / f"{job['job_id']}.prompt.md"
    prompt_copy.write_text(prompt, encoding="utf-8")

    if args.dry_run or not args.command:
        raw_path.write_text("", encoding="utf-8")
        parsed_path.write_text(
            json.dumps(default_output(job["job_id"], job["agent_role"], job["input_refs"]), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"Dry-run output written to {parsed_path}")
        return 0

    result = subprocess.run(args.command, input=prompt, cwd=REPO_ROOT, text=True, shell=True, capture_output=True)
    raw = result.stdout + ("\nSTDERR:\n" + result.stderr if result.stderr else "")
    raw_path.write_text(raw, encoding="utf-8")
    if result.returncode != 0:
        print(raw)
        return result.returncode
    parsed = parse_json_response(result.stdout)
    parsed.setdefault("job_id", job["job_id"])
    parsed.setdefault("agent_role", job["agent_role"])
    parsed_path.write_text(json.dumps(parsed, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"LLM output written to {parsed_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
