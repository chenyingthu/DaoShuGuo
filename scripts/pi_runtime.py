#!/usr/bin/env python3
"""Shared Pi runtime helpers for DaoShuGuo LLM worker tests."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any


PI_HOME = Path(os.environ.get("DAOSHUGUO_PI_HOME", str(Path.home())))
LEGACY_TEMP_PI_HOME = Path("/tmp/daoshuguo-pi-feasibility/home")
PI_CLI = Path("/tmp/daoshuguo-pi-feasibility/pi-mono/packages/coding-agent/dist/cli.js")
CLAUDE_BAIDU_SETTINGS = Path("/home/chenying/.claude/settings-baidu.json")
CODEX_AUTH = Path("/home/chenying/.codex/auth.json")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def ensure_openai_pi_config() -> None:
    agent_dir = PI_HOME / ".pi" / "agent"
    agent_dir.mkdir(parents=True, exist_ok=True)
    auth = _read_json(CODEX_AUTH)
    (agent_dir / "models.json").write_text(
        json.dumps({"providers": {"openai": {"baseUrl": "https://relay.nf.video/v1"}}}, indent=2),
        encoding="utf-8",
    )
    (agent_dir / "auth.json").write_text(
        json.dumps({"openai": {"type": "api_key", "key": auth["OPENAI_API_KEY"]}}, indent=2),
        encoding="utf-8",
    )


def ensure_codex_relay_pi_config() -> None:
    agent_dir = PI_HOME / ".pi" / "agent"
    agent_dir.mkdir(parents=True, exist_ok=True)
    auth = _read_json(CODEX_AUTH)
    (agent_dir / "models.json").write_text(
        json.dumps(
            {
                "providers": {
                    "codex-relay": {
                        "baseUrl": "https://relay.nf.video/v1",
                        "api": "openai-responses",
                        "apiKey": auth["OPENAI_API_KEY"],
                        "models": [
                            {
                                "id": "gpt-5.5",
                                "name": "gpt-5.5 (Codex relay / OpenAI Responses)",
                                "reasoning": True,
                                "input": ["text"],
                                "contextWindow": 1000000,
                                "maxTokens": 16384,
                                "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0},
                            }
                        ],
                    }
                }
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def ensure_baidu_pi_config() -> None:
    agent_dir = PI_HOME / ".pi" / "agent"
    agent_dir.mkdir(parents=True, exist_ok=True)
    settings = _read_json(CLAUDE_BAIDU_SETTINGS)
    env = settings.get("env", {})
    candidate_models = [
        settings.get("model"),
        env.get("ANTHROPIC_MODEL"),
        env.get("ANTHROPIC_DEFAULT_HAIKU_MODEL"),
        env.get("ANTHROPIC_DEFAULT_SONNET_MODEL"),
        env.get("ANTHROPIC_DEFAULT_OPUS_MODEL"),
    ]
    models: list[dict[str, Any]] = []
    seen: set[str] = set()
    for model_id in candidate_models:
        if not model_id or model_id in seen:
            continue
        seen.add(model_id)
        models.append(
            {
                "id": model_id,
                "name": f"{model_id} (Baidu Anthropic)",
                "reasoning": True,
                "input": ["text"],
                "contextWindow": 200000,
                "maxTokens": 16384,
                "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0},
            }
        )
    (agent_dir / "models.json").write_text(
        json.dumps(
            {
                "providers": {
                    "baidu-anthropic": {
                        "baseUrl": env["ANTHROPIC_BASE_URL"],
                        "api": "anthropic-messages",
                        "authHeader": True,
                        "apiKey": env["ANTHROPIC_AUTH_TOKEN"],
                        "models": models,
                    }
                }
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def ensure_pi_config(provider: str) -> None:
    if os.environ.get("DAOSHUGUO_WRITE_TEMP_PI_CONFIG") != "1":
        return
    global PI_HOME
    PI_HOME = LEGACY_TEMP_PI_HOME
    if provider == "baidu-anthropic":
        ensure_baidu_pi_config()
        return
    if provider == "codex-relay":
        ensure_codex_relay_pi_config()
        return
    ensure_openai_pi_config()


def read_jsonl_lines(text: str) -> list[dict[str, Any]]:
    lines: list[dict[str, Any]] = []
    for raw in text.splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            lines.append(json.loads(raw))
        except Exception:
            continue
    return lines


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run_pi_prompt(
    prompt: str,
    cwd: Path,
    *,
    provider: str = "openai",
    model: str = "gpt-5.4",
    thinking: str = "off",
) -> dict[str, Any]:
    ensure_pi_config(provider)
    env = os.environ.copy()
    env["HOME"] = str(PI_HOME)
    pi_node_modules = PI_CLI.parents[4] / "node_modules"
    if pi_node_modules.exists():
        existing_node_path = env.get("NODE_PATH")
        env["NODE_PATH"] = (
            f"{pi_node_modules}:{existing_node_path}" if existing_node_path else str(pi_node_modules)
        )
    command = [
        "node",
        str(PI_CLI),
        "--no-session",
        "--mode",
        "json",
        "-p",
        "--provider",
        provider,
        "--model",
        model,
        "--thinking",
        thinking,
        prompt,
    ]
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, env=env)
    return {
        "exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "events": read_jsonl_lines(result.stdout),
    }
