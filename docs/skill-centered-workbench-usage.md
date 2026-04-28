# Skill-Centered Workbench Usage

## Rebuild Topic Data

```bash
python scripts/build_workbench_topic.py --topic real-task-001
python scripts/build_researcher_lens.py --topic real-task-001
python scripts/build_research_communication_briefs.py --topic real-task-001
python scripts/build_skill_worker_context.py --topic real-task-001
```

Key generated files:

- `workbench_data/topics/real-task-001/skill_cockpit.json`
- `workbench_data/topics/real-task-001/skill_progression.json`
- `workbench_data/topics/real-task-001/skill_judgment_card.json`
- `workbench_data/topics/real-task-001/researcher_lens.json`
- `workbench_data/topics/real-task-001/human_attention_queue.json`
- `workbench_data/topics/real-task-001/skill_worker_context.json`

## Start API

```bash
python scripts/serve_workbench_api.py --port 8765
```

Useful checks:

```bash
curl http://127.0.0.1:8765/topics
curl http://127.0.0.1:8765/topics/real-task-001/skill-cockpit
```

## Open UI

After starting the API, open:

```text
workbench_ui/index.html
```

The UI reads from `http://127.0.0.1:8766` by default in the current local setup.

## Write A Direction Override

Dry-run through API:

```bash
curl -X POST 'http://127.0.0.1:8765/topics/real-task-001/direction-override?dry_run=true'
```

Persist through CLI:

```bash
python scripts/write_direction_override.py --topic real-task-001
python scripts/compile_human_decision_constraints.py --topic real-task-001
python scripts/apply_workbench_constraints_to_loop.py --topic real-task-001
python scripts/build_skill_worker_context.py --topic real-task-001
```

## Verify

```bash
python scripts/verify_skill_centered_workbench.py --topic real-task-001
python scripts/verify_workbench_topic.py --topic real-task-001
python scripts/verify_researcher_lens.py --topic real-task-001
python scripts/verify_research_communication_briefs.py --topic real-task-001
python scripts/verify_skill_worker_context.py --topic real-task-001
python scripts/validate_schemas.py --artifacts workbench
```

## Skill Worker Context

`skill_worker_context.json` is the handoff object for the next skill worker. It combines:

- active skill and candidate family
- method/process/standard change requirements
- primary metric and boundary-trigger evidence limits
- must-do and must-not-do constraints compiled from human decisions
- forbidden claims and forbidden shortcuts

The next worker should consume this object before proposing a new candidate skill variant.

## Interpretation Rule

Current `real-task-001` evidence supports a structural method attempt with bounded operational-quality gain. It does not prove verified structural skill improvement or hosting-capacity boundary improvement.
