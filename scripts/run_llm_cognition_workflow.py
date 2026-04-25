#!/usr/bin/env python3
"""Run or dry-run a multi-role LLM cognition workflow."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} did not parse to object")
    return data


def build_prompt(job: dict[str, Any]) -> str:
    prompt = (REPO_ROOT / job["prompt_ref"]).read_text(encoding="utf-8")
    lines = [prompt, "", "## Job", json.dumps(job, indent=2, ensure_ascii=False)]
    lines.append("\n## Input Artifact Excerpts")
    for ref in job["input_refs"][:12]:
        p = REPO_ROOT / ref
        if p.exists() and p.is_file():
            lines.extend([f"### {ref}", p.read_text(encoding="utf-8")[:1800], ""])
    lines.append("## Predecessor Output Excerpts")
    for ref in job.get("predecessor_output_refs", [])[:12]:
        p = REPO_ROOT / ref
        if p.exists() and p.is_file():
            lines.extend([f"### {ref}", p.read_text(encoding="utf-8")[:1800], ""])
    return "\n".join(lines)


def parse_json_response(text: str) -> dict[str, Any]:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise RuntimeError("response does not contain JSON object")
    payload = json.loads(text[start : end + 1])
    if not isinstance(payload, dict):
        raise RuntimeError("response JSON is not object")
    return payload


def default_output(job: dict[str, Any]) -> dict[str, Any]:
    output = {
        "job_id": job["job_id"],
        "agent_role": job["agent_role"],
        "input_refs": job["input_refs"],
        "strongest_supported_claim": "dry-run only",
        "strongest_unsupported_claim": "",
        "alternative_interpretation": "",
        "discriminating_missing_evidence": [],
        "agreement_with_rule_baseline": "not_evaluated",
        "new_insights": [],
        "overclaim_warnings": [],
        "evidence_used": [],
        "recommended_action": "run_with_llm",
        "confidence": "low",
    }
    if job["workflow_role"] == "adjudicator":
        output["accepted_interpretation"] = "dry-run only"
        output["rejected_interpretation"] = "dry-run only"
        output["claim_ceiling_recommendation"] = "dry-run only"
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a LLM cognition workflow.")
    parser.add_argument("workflow")
    parser.add_argument("--command", help="Command that accepts prompt on stdin and returns JSON.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output-dir", default="agents/cognition/outputs")
    args = parser.parse_args()
    workflow = load_json(REPO_ROOT / args.workflow)
    output_dir = REPO_ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    for job in workflow["jobs"]:
        prompt = build_prompt(job)
        (output_dir / f"{job['job_id']}.prompt.md").write_text(prompt, encoding="utf-8")
        if args.dry_run or not args.command:
            (output_dir / f"{job['job_id']}.raw.txt").write_text("", encoding="utf-8")
            (output_dir / f"{job['job_id']}.json").write_text(
                json.dumps(default_output(job), indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            continue
        result = subprocess.run(args.command, input=prompt, cwd=REPO_ROOT, text=True, shell=True, capture_output=True)
        raw = result.stdout + ("\nSTDERR:\n" + result.stderr if result.stderr else "")
        (output_dir / f"{job['job_id']}.raw.txt").write_text(raw, encoding="utf-8")
        if result.returncode != 0:
            print(raw)
            return result.returncode
        parsed = parse_json_response(result.stdout)
        parsed.setdefault("job_id", job["job_id"])
        parsed.setdefault("agent_role", job["agent_role"])
        (output_dir / f"{job['job_id']}.json").write_text(json.dumps(parsed, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"LLM cognition workflow executed: {workflow['workflow_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
