#!/usr/bin/env python3
"""Evaluate Pi provider/model compatibility for DaoShuGuo."""

from __future__ import annotations

import json
import sys
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.pi_runtime import ensure_pi_config, run_pi_prompt, write_json, PI_HOME
OUT_DIR = REPO_ROOT / "analysis" / "pi_harness" / "provider_matrix"


def has_tool_call(run: dict) -> bool:
    for event in run["events"]:
        if event.get("type") == "tool_execution_start":
            return True
        message = event.get("message", {})
        if isinstance(message, dict):
            for block in message.get("content", []):
                if isinstance(block, dict) and block.get("type") == "toolCall":
                    return True
    return False


def has_tool_execution(run: dict) -> bool:
    return any(event.get("type") == "tool_execution_end" for event in run["events"])


def has_agent_error(run: dict) -> bool:
    for event in run["events"]:
        message = event.get("message")
        if isinstance(message, dict) and message.get("stopReason") == "error":
            return True
    return False


def run_case(name: str, provider: str, model: str, prompt: str, *, thinking: str = "off") -> dict:
    workdir = REPO_ROOT / "analysis" / "pi_harness" / f"provider_case_{name}"
    workdir.mkdir(parents=True, exist_ok=True)
    run = run_pi_prompt(prompt, workdir, provider=provider, model=model, thinking=thinking)
    result = {
        "case": name,
        "provider": provider,
        "model": model,
        "thinking": thinking,
        "exit_code": run["exit_code"],
        "has_agent_error": has_agent_error(run),
        "has_tool_call": has_tool_call(run),
        "has_tool_execution": has_tool_execution(run),
        "stdout_excerpt": run["stdout"][:8000],
        "stderr": run["stderr"],
    }
    write_json(OUT_DIR / f"{name}.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate Pi provider/model compatibility.")
    parser.add_argument("--provider", default="openai")
    parser.add_argument("--model", default="gpt-5.4")
    parser.add_argument("--thinking", default="off")
    args = parser.parse_args()

    ensure_pi_config(args.provider)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    prefix = f"{args.provider}_{args.model}".replace("/", "_").replace(".", "")
    results = []
    results.append(
        run_case(
            f"{prefix}_text",
            args.provider,
            args.model,
            "Say ok in one short sentence.",
            thinking=args.thinking,
        )
    )
    results.append(
        run_case(
            f"{prefix}_init_tool",
            args.provider,
            args.model,
            "Use init_research_task with task_ref task.power.ieee69_renewable_reactive_opt and objective 'Provider matrix tool-call test.'",
            thinking=args.thinking,
        )
    )
    write_json(OUT_DIR / f"summary_{prefix}.json", {"results": results, "pi_home": str(PI_HOME)})
    print(json.dumps({"results": results}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
