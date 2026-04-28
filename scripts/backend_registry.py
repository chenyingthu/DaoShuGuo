#!/usr/bin/env python3
"""Agent runtime registry helpers for generic loop execution."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY_PATH = REPO_ROOT / "configs" / "agent_runtimes" / "registry.yaml"


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} did not parse to mapping")
    return data


def load_backend_registry(path: Path | None = None) -> dict[str, Any]:
    registry_path = path or DEFAULT_REGISTRY_PATH
    registry = load_yaml(registry_path)
    runtimes = registry.get("runtimes")
    if not isinstance(runtimes, dict):
        legacy_backends = registry.get("backends")
        if isinstance(legacy_backends, dict):
            registry["runtimes"] = legacy_backends
        else:
            raise RuntimeError(f"{registry_path} missing mapping field runtimes")
    return registry


def resolve_backend(backend_id: str, path: Path | None = None) -> dict[str, Any]:
    registry = load_backend_registry(path)
    backend = registry["runtimes"].get(backend_id)
    if not isinstance(backend, dict):
        known = ", ".join(sorted(registry["runtimes"]))
        raise RuntimeError(f"unknown backend/runtime {backend_id!r}; known runtimes: {known}")
    resolved = dict(backend)
    resolved["backend_id"] = backend_id
    resolved.setdefault("runtime_id", backend_id)
    return resolved


def backend_worker_module_path(backend: dict[str, Any]) -> Path:
    module_path = backend.get("worker_module")
    if not module_path:
        raise RuntimeError(f"backend {backend.get('backend_id')} missing worker_module")
    path = Path(str(module_path))
    return path if path.is_absolute() else REPO_ROOT / path


def require_backend_runnable(backend: dict[str, Any]) -> None:
    if backend.get("status") == "blocked":
        limitations = "; ".join(str(item) for item in backend.get("known_limitations", []))
        raise RuntimeError(
            f"backend {backend.get('backend_id')} is blocked and cannot run: {limitations}"
        )
