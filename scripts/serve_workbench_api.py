#!/usr/bin/env python3
"""Minimal file-backed API for the collaborative research workbench."""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from workbench_common import (
    WORKBENCH_ROOT,
    build_agent_response,
    compile_constraints,
    default_human_object,
    read_json,
    rel,
    topic_dir,
    write_human_object,
)
from apply_workbench_constraints_to_loop import build_context, build_skill_worker_context


ROUTES = {
    "cockpit": "cockpit.json",
    "skill-cockpit": "skill_cockpit.json",
    "skill-progression": "skill_progression.json",
    "skill-judgment-card": "skill_judgment_card.json",
    "briefs": "briefs.json",
    "evidence-graph": "evidence_graph.json",
    "human-attention-queue": "human_attention_queue.json",
    "loop-context": "loop_context.json",
    "skill-worker-context": "skill_worker_context.json",
}


def json_bytes(payload: object) -> bytes:
    return (json.dumps(payload, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    def send_json(self, status: int, payload: object) -> None:
        body = json_bytes(payload)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_json(200, {"status": "ok"})

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        parts = [part for part in parsed.path.split("/") if part]
        if parts == ["topics"]:
            topics_root = WORKBENCH_ROOT / "topics"
            topics = sorted(path.name for path in topics_root.iterdir() if path.is_dir()) if topics_root.exists() else []
            self.send_json(200, {"topics": topics})
            return
        if len(parts) == 3 and parts[0] == "topics" and parts[2] in ROUTES:
            path = topic_dir(parts[1]) / ROUTES[parts[2]]
            if not path.exists():
                self.send_json(404, {"error": f"missing {rel(path)}"})
                return
            self.send_json(200, read_json(path))
            return
        self.send_json(404, {"error": "unknown route"})

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        dry_run = query.get("dry_run", ["false"])[0].lower() in {"1", "true", "yes"}
        parts = [part for part in parsed.path.split("/") if part]
        if len(parts) != 3 or parts[0] != "topics":
            self.send_json(404, {"error": "unknown route"})
            return
        topic = parts[1]
        action = parts[2]
        if action == "direction-override":
            obj = default_human_object("direction_override", topic)
            path = write_human_object(obj, dry_run=dry_run)
            self.send_json(
                200,
                {
                    "status": "dry_run" if dry_run else "written",
                    "written_object_ref": obj["object_id"],
                    "path": rel(path),
                    "impact_summary": "Direction override targets the next skill_worker route.",
                },
            )
            return
        if action == "compile-constraints":
            constraints = compile_constraints(topic, dry_run=dry_run)
            response = None
            if constraints:
                response = build_agent_response(
                    topic,
                    constraints[0]["source_human_object_ref"],
                    [item["object_id"] for item in constraints],
                    dry_run=dry_run,
                )
            context = build_context(topic, allow_dry_run_fallback=dry_run)
            skill_worker_context = build_skill_worker_context(topic, allow_dry_run_fallback=dry_run)
            self.send_json(
                200,
                {
                    "status": "compiled",
                    "compiled_constraint_refs": [item["object_id"] for item in constraints],
                    "agent_response_ref": response["object_id"] if response else None,
                    "loop_context_status": context["status"],
                    "skill_worker_context_status": skill_worker_context["status"],
                    "dry_run": dry_run,
                },
            )
            return
        self.send_json(404, {"error": "unknown action"})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Serving workbench API at http://127.0.0.1:{args.port}")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
