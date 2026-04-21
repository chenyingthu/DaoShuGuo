"""Helpers for loading task-specific runtime modules."""

from __future__ import annotations

from importlib import import_module
from types import ModuleType


def runtime_helpers_for_task(task_package: str) -> ModuleType:
    """Load the runtime helper module for a task package."""
    return import_module(f"tasks.{task_package}.runtime_helpers")


def task_package_from_constraints(constraint_set: dict[str, object]) -> str:
    """Resolve the task package name from a solver constraint set."""
    task_package = constraint_set.get("task_package", "task001")
    if not isinstance(task_package, str) or not task_package:
        raise ValueError("constraint_set.task_package must be a non-empty string")
    return task_package
