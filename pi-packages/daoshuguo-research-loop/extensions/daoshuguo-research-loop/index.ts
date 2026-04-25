import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";
import { Type } from "@sinclair/typebox";
import { spawn } from "node:child_process";
import * as fs from "node:fs";
import * as path from "node:path";

type LoopEntry = {
  timestamp: string;
  event: string;
  task_ref?: string;
  data: Record<string, unknown>;
};

function now(): string {
  return new Date().toISOString();
}

function loopPath(cwd: string, fileName: string): string {
  return path.join(cwd, fileName);
}

function appendJsonl(cwd: string, entry: LoopEntry): void {
  fs.appendFileSync(loopPath(cwd, "research_loop.jsonl"), JSON.stringify(entry) + "\n", "utf8");
}

function ensureMarkdown(cwd: string, taskRef: string, objective: string): void {
  const file = loopPath(cwd, "research_loop.md");
  if (fs.existsSync(file)) return;
  fs.writeFileSync(
    file,
    [
      `# DaoShuGuo Research Loop: ${taskRef}`,
      "",
      "## Objective",
      objective,
      "",
      "## Current Constraints",
      "- Keep task, evaluator, and evidence boundaries explicit.",
      "- Skill agents change candidate skill code only.",
      "- Cognition agents change next-round constraints only.",
      "- Effectiveness claims must stay below the evidence ceiling.",
      "",
      "## Files",
      "- `research_loop.md`: durable human-readable loop memory.",
      "- `research_loop.jsonl`: append-only structured loop log.",
      "",
      "## What Has Been Tried",
      "- Initialized Pi research loop.",
      "",
    ].join("\n"),
    "utf8",
  );
}

function appendMarkdown(cwd: string, text: string): void {
  fs.appendFileSync(loopPath(cwd, "research_loop.md"), text, "utf8");
}

function parseTaskRunPath(stdout: string): string | null {
  const match = stdout.match(/Task00[34] real run written to (.+)$/m);
  return match ? match[1].trim() : null;
}

function parseRunRefFromRunYaml(runDir: string): string | null {
  try {
    const runYaml = fs.readFileSync(path.join(runDir, "run.yaml"), "utf8");
    const match = runYaml.match(/^object_id:\s*(.+)$/m);
    return match ? match[1].trim() : null;
  } catch {
    return null;
  }
}

function parseReportRefFromReportYaml(runDir: string): string | null {
  try {
    const reportYaml = fs.readFileSync(path.join(runDir, "report.yaml"), "utf8");
    const match = reportYaml.match(/^object_id:\s*(.+)$/m);
    return match ? match[1].trim() : null;
  } catch {
    return null;
  }
}

async function runCommand(
  command: string,
  cwd: string,
): Promise<{ exitCode: number | null; stdout: string; stderr: string }> {
  return await new Promise((resolve) => {
    const child = spawn(command, {
      cwd,
      shell: true,
      stdio: ["ignore", "pipe", "pipe"],
      env: process.env,
    });
    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (chunk) => {
      stdout += chunk.toString();
    });
    child.stderr.on("data", (chunk) => {
      stderr += chunk.toString();
    });
    child.on("close", (code) => resolve({ exitCode: code, stdout, stderr }));
  });
}

export default function daoshuguoResearchLoop(pi: ExtensionAPI) {
  pi.on("before_agent_start", async (event, ctx) => {
    const loopMd = loopPath(ctx.cwd, "research_loop.md");
    if (!fs.existsSync(loopMd)) return;
    const text = fs.readFileSync(loopMd, "utf8").slice(0, 6000);
    return {
      systemPrompt:
        event.systemPrompt +
        "\n\nDaoShuGuo research-loop context is active. Treat research_loop.md and research_loop.jsonl as durable loop memory. Do not make unsupported broad claims.\n" +
        text,
    };
  });

  pi.registerTool({
    name: "init_research_task",
    label: "Init Research Task",
    description: "Initialize durable DaoShuGuo research-loop files.",
    promptSnippet: "Initialize DaoShuGuo research-loop files for a bounded task.",
    promptGuidelines: [
      "Use init_research_task when beginning a DaoShuGuo research loop for a specific task.",
    ],
    parameters: Type.Object({
      task_ref: Type.String({ description: "Task object reference." }),
      objective: Type.String({ description: "Bounded research objective." }),
    }),
    async execute(_toolCallId, params, _signal, _onUpdate, ctx) {
      ensureMarkdown(ctx.cwd, params.task_ref, params.objective);
      appendJsonl(ctx.cwd, {
        timestamp: now(),
        event: "init_research_task",
        task_ref: params.task_ref,
        data: { objective: params.objective },
      });
      return {
        content: [{ type: "text", text: "Initialized research_loop.md and research_loop.jsonl." }],
        details: { files: ["research_loop.md", "research_loop.jsonl"] },
      };
    },
  });

  pi.registerTool({
    name: "log_research_iteration",
    label: "Log Research Iteration",
    description: "Append one structured DaoShuGuo research-loop event.",
    promptSnippet: "Record a bounded DaoShuGuo iteration summary.",
    promptGuidelines: [
      "Use log_research_iteration after each meaningful DaoShuGuo step to preserve durable loop memory.",
    ],
    parameters: Type.Object({
      task_ref: Type.String(),
      iteration: Type.Number(),
      role: Type.String({ description: "skill_agent, cognition_agent, evaluator, or reviewer." }),
      summary: Type.String(),
      status: Type.String({ description: "kept, discarded, blocked, or needs_review." }),
    }),
    async execute(_toolCallId, params, _signal, _onUpdate, ctx) {
      appendJsonl(ctx.cwd, {
        timestamp: now(),
        event: "research_iteration",
        task_ref: params.task_ref,
        data: params,
      });
      appendMarkdown(
        ctx.cwd,
        `\n- Iteration ${params.iteration} [${params.role}/${params.status}]: ${params.summary}\n`,
      );
      return {
        content: [{ type: "text", text: `Logged iteration ${params.iteration}: ${params.status}` }],
        details: params,
      };
    },
  });

  pi.registerTool({
    name: "record_skill_trial",
    label: "Record Skill Trial",
    description: "Record a skill trial result without making external claims.",
    promptSnippet: "Record a DaoShuGuo skill trial outcome with evidence path and next constraint.",
    promptGuidelines: [
      "Use record_skill_trial immediately after a DaoShuGuo skill trial to capture run-level evidence without broad claims.",
    ],
    parameters: Type.Object({
      task_ref: Type.String(),
      skill_ref: Type.String(),
      run_ref: Type.String(),
      outcome: Type.String({ description: "success, failure, blocked, or inconclusive." }),
      evidence_path: Type.String({ description: "Path to the run/evidence artifact." }),
      next_constraint: Type.String({ description: "Constraint to feed the next iteration." }),
    }),
    async execute(_toolCallId, params, _signal, _onUpdate, ctx) {
      appendJsonl(ctx.cwd, {
        timestamp: now(),
        event: "skill_trial",
        task_ref: params.task_ref,
        data: params,
      });
      appendMarkdown(
        ctx.cwd,
        [
          "",
          `### Skill Trial: ${params.skill_ref}`,
          `- run_ref: ${params.run_ref}`,
          `- outcome: ${params.outcome}`,
          `- evidence_path: ${params.evidence_path}`,
          `- next_constraint: ${params.next_constraint}`,
          "",
        ].join("\n"),
      );
      return {
        content: [{ type: "text", text: `Recorded skill trial ${params.run_ref}: ${params.outcome}` }],
        details: params,
      };
    },
  });

  pi.registerTool({
    name: "record_cognition_constraint",
    label: "Record Cognition Constraint",
    description: "Record a bounded next-iteration cognition constraint.",
    promptSnippet: "Record a bounded DaoShuGuo cognition constraint for the next iteration.",
    promptGuidelines: [
      "Use record_cognition_constraint when the next DaoShuGuo iteration needs a bounded constraint, blocked path, or discriminating test.",
    ],
    parameters: Type.Object({
      task_ref: Type.String(),
      source_run_ref: Type.String(),
      constraint: Type.String({ description: "The bounded next-round constraint." }),
      blocked_path: Type.Optional(Type.String({ description: "An explicitly blocked path." })),
      required_test: Type.Optional(Type.String({ description: "A required discriminating test." })),
    }),
    async execute(_toolCallId, params, _signal, _onUpdate, ctx) {
      appendJsonl(ctx.cwd, {
        timestamp: now(),
        event: "cognition_constraint",
        task_ref: params.task_ref,
        data: params,
      });
      appendMarkdown(
        ctx.cwd,
        [
          "",
          `### Cognition Constraint from ${params.source_run_ref}`,
          `- constraint: ${params.constraint}`,
          ...(params.blocked_path ? [`- blocked_path: ${params.blocked_path}`] : []),
          ...(params.required_test ? [`- required_test: ${params.required_test}`] : []),
          "",
        ].join("\n"),
      );
      return {
        content: [{ type: "text", text: `Recorded cognition constraint from ${params.source_run_ref}` }],
        details: params,
      };
    },
  });

  pi.registerTool({
    name: "record_iteration_review",
    label: "Record Iteration Review",
    description: "Record one bounded iteration review entry.",
    promptSnippet: "Record a DaoShuGuo iteration review verdict and summary.",
    promptGuidelines: [
      "Use record_iteration_review after a DaoShuGuo iteration to capture whether there was real progress, stagnation, or blockage.",
    ],
    parameters: Type.Object({
      task_ref: Type.String(),
      iteration: Type.Number(),
      verdict: Type.String({ description: "real_progress, stagnation, blocked, or needs_revision." }),
      summary: Type.String(),
    }),
    async execute(_toolCallId, params, _signal, _onUpdate, ctx) {
      appendJsonl(ctx.cwd, {
        timestamp: now(),
        event: "iteration_review",
        task_ref: params.task_ref,
        data: params,
      });
      appendMarkdown(
        ctx.cwd,
        `\n### Iteration Review ${params.iteration}\n- verdict: ${params.verdict}\n- summary: ${params.summary}\n`,
      );
      return {
        content: [{ type: "text", text: `Recorded iteration review ${params.iteration}: ${params.verdict}` }],
        details: params,
      };
    },
  });

  pi.registerTool({
    name: "run_task003_trial",
    label: "Run Task003 Trial",
    description: "Execute the existing DaoShuGuo task003 runner and record the result.",
    promptSnippet: "Run the existing DaoShuGuo task003 real trial bridge.",
    promptGuidelines: [
      "Use run_task003_trial to execute the bounded task003 real trial before recording skill or cognition artifacts.",
    ],
    parameters: Type.Object({
      strategy: Type.Optional(Type.String({ description: "task003 strategy", default: "inverter-support" })),
      repo_root: Type.Optional(Type.String({ description: "DaoShuGuo repo root; defaults to current cwd." })),
      task_ref: Type.Optional(Type.String({ description: "task ref", default: "task.power.ieee69_renewable_reactive_opt" })),
    }),
    async execute(_toolCallId, params, _signal, _onUpdate, ctx) {
      const repoRoot = params.repo_root || ctx.cwd;
      const strategy = params.strategy || "inverter-support";
      const taskRef = params.task_ref || "task.power.ieee69_renewable_reactive_opt";
      const cmd = `python orchestrator/main.py real-run-task003 --strategy ${strategy}`;
      const result = await runCommand(cmd, repoRoot);
      const runDir = result.exitCode === 0 ? parseTaskRunPath(result.stdout) : null;
      const runRef = runDir ? parseRunRefFromRunYaml(runDir) : null;
      const reportRef = runDir ? parseReportRefFromReportYaml(runDir) : null;
      appendJsonl(ctx.cwd, {
        timestamp: now(),
        event: "task003_trial",
        task_ref: taskRef,
        data: {
          strategy,
          exitCode: result.exitCode,
          runDir,
          runRef,
          reportRef,
          stdout: result.stdout.trim(),
          stderr: result.stderr.trim(),
        },
      });
      if (runDir && runRef) {
        appendMarkdown(
          ctx.cwd,
          [
            "",
            `### Task003 Trial: ${strategy}`,
            `- run_dir: ${runDir}`,
            `- run_ref: ${runRef}`,
            ...(reportRef ? [`- report_ref: ${reportRef}`] : []),
            "",
          ].join("\n"),
        );
      }
      return {
        content: [
          {
            type: "text",
            text:
              result.exitCode === 0
                ? `Task003 trial completed: ${result.stdout.trim()}`
                : `Task003 trial failed with exit code ${result.exitCode}`,
          },
        ],
        details: {
          strategy,
          repo_root: repoRoot,
          exitCode: result.exitCode,
          runDir,
          runRef,
          reportRef,
          stdout: result.stdout,
          stderr: result.stderr,
        },
      };
    },
  });

  pi.registerTool({
    name: "run_task004_trial",
    label: "Run Task004 Trial",
    description: "Execute the existing DaoShuGuo task004 runner and record the result.",
    promptSnippet: "Run the existing DaoShuGuo task004 hosting-capacity trial bridge.",
    promptGuidelines: [
      "Use run_task004_trial to execute a bounded task004 real trial before recording boundary or effectiveness artifacts.",
    ],
    parameters: Type.Object({
      strategy: Type.Optional(Type.String({ description: "task004 strategy", default: "inverter-support" })),
      candidate_q_step_mvar: Type.Optional(Type.Number({ description: "Override candidate reactive support step in MVar." })),
      repo_root: Type.Optional(Type.String({ description: "DaoShuGuo repo root; defaults to current cwd." })),
      task_ref: Type.Optional(Type.String({ description: "task ref", default: "task.power.ieee69_hosting_capacity" })),
    }),
    async execute(_toolCallId, params, _signal, _onUpdate, ctx) {
      const repoRoot = params.repo_root || ctx.cwd;
      const strategy = params.strategy || "inverter-support";
      const taskRef = params.task_ref || "task.power.ieee69_hosting_capacity";
      const qStepArg =
        typeof params.candidate_q_step_mvar === "number"
          ? ` --candidate-q-step-mvar ${params.candidate_q_step_mvar}`
          : "";
      const cmd = `python orchestrator/main.py real-run-task004 --strategy ${strategy}${qStepArg}`;
      const result = await runCommand(cmd, repoRoot);
      const runDir = result.exitCode === 0 ? parseTaskRunPath(result.stdout) : null;
      const runRef = runDir ? parseRunRefFromRunYaml(runDir) : null;
      const reportRef = runDir ? parseReportRefFromReportYaml(runDir) : null;
      appendJsonl(ctx.cwd, {
        timestamp: now(),
        event: "task004_trial",
        task_ref: taskRef,
        data: {
          strategy,
          candidate_q_step_mvar: params.candidate_q_step_mvar,
          exitCode: result.exitCode,
          runDir,
          runRef,
          reportRef,
          stdout: result.stdout.trim(),
          stderr: result.stderr.trim(),
        },
      });
      if (runDir && runRef) {
        appendMarkdown(
          ctx.cwd,
          [
            "",
            `### Task004 Trial: ${strategy}`,
            ...(typeof params.candidate_q_step_mvar === "number"
              ? [`- candidate_q_step_mvar: ${params.candidate_q_step_mvar}`]
              : []),
            `- run_dir: ${runDir}`,
            `- run_ref: ${runRef}`,
            ...(reportRef ? [`- report_ref: ${reportRef}`] : []),
            "",
          ].join("\n"),
        );
      }
      return {
        content: [
          {
            type: "text",
            text:
              result.exitCode === 0
                ? `Task004 trial completed: ${result.stdout.trim()}`
                : `Task004 trial failed with exit code ${result.exitCode}`,
          },
        ],
        details: {
          strategy,
          candidate_q_step_mvar: params.candidate_q_step_mvar,
          repo_root: repoRoot,
          exitCode: result.exitCode,
          runDir,
          runRef,
          reportRef,
          stdout: result.stdout,
          stderr: result.stderr,
        },
      };
    },
  });

  pi.registerTool({
    name: "record_boundary_judgment",
    label: "Record Boundary Judgment",
    description: "Record a bounded hosting-capacity boundary judgment.",
    promptSnippet: "Record a DaoShuGuo boundary judgment with claim ceiling and boundary type.",
    promptGuidelines: [
      "Use record_boundary_judgment when task004 needs a bounded statement about hosting-capacity boundary meaning or claim ceiling.",
    ],
    parameters: Type.Object({
      task_ref: Type.String(),
      run_ref: Type.String(),
      boundary_statement: Type.String(),
      claim_ceiling: Type.String(),
      boundary_type: Type.String(),
    }),
    async execute(_toolCallId, params, _signal, _onUpdate, ctx) {
      appendJsonl(ctx.cwd, {
        timestamp: now(),
        event: "boundary_judgment",
        task_ref: params.task_ref,
        data: params,
      });
      appendMarkdown(
        ctx.cwd,
        [
          "",
          `### Boundary Judgment from ${params.run_ref}`,
          `- boundary_statement: ${params.boundary_statement}`,
          `- claim_ceiling: ${params.claim_ceiling}`,
          `- boundary_type: ${params.boundary_type}`,
          "",
        ].join("\n"),
      );
      return {
        content: [{ type: "text", text: `Recorded boundary judgment from ${params.run_ref}` }],
        details: params,
      };
    },
  });

  pi.registerTool({
    name: "record_effectiveness_status",
    label: "Record Effectiveness Status",
    description: "Record deliverable/readiness status for the current task.",
    promptSnippet: "Record DaoShuGuo effectiveness status, readiness level, and missing items for the next level.",
    promptGuidelines: [
      "Use record_effectiveness_status when a task needs an explicit readiness judgment such as internal_report_ready or paper_candidate.",
    ],
    parameters: Type.Object({
      task_ref: Type.String(),
      readiness_level: Type.String(),
      supported_output: Type.String(),
      missing_for_next_level: Type.String(),
    }),
    async execute(_toolCallId, params, _signal, _onUpdate, ctx) {
      appendJsonl(ctx.cwd, {
        timestamp: now(),
        event: "effectiveness_status",
        task_ref: params.task_ref,
        data: params,
      });
      appendMarkdown(
        ctx.cwd,
        [
          "",
          `### Effectiveness Status`,
          `- readiness_level: ${params.readiness_level}`,
          `- supported_output: ${params.supported_output}`,
          `- missing_for_next_level: ${params.missing_for_next_level}`,
          "",
        ].join("\n"),
      );
      return {
        content: [{ type: "text", text: `Recorded effectiveness status: ${params.readiness_level}` }],
        details: params,
      };
    },
  });

  pi.registerCommand("daoshuguo", {
    description: "Show DaoShuGuo research-loop status.",
    handler: async (_args, ctx) => {
      const jsonl = loopPath(ctx.cwd, "research_loop.jsonl");
      const count = fs.existsSync(jsonl)
        ? fs.readFileSync(jsonl, "utf8").split("\n").filter(Boolean).length
        : 0;
      ctx.ui.notify(`DaoShuGuo loop entries: ${count}`, "info");
    },
  });
}
