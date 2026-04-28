const API = window.WORKBENCH_API || "http://127.0.0.1:8766";

const $ = (id) => document.getElementById(id);

async function getJson(path) {
  const response = await fetch(`${API}${path}`);
  if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
  return response.json();
}

async function postJson(path) {
  const response = await fetch(`${API}${path}`, { method: "POST" });
  if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
  return response.json();
}

function renderList(id, items) {
  const node = $(id);
  node.innerHTML = "";
  (items || []).forEach((item) => {
    const li = document.createElement("li");
    li.textContent = typeof item === "string" ? item : JSON.stringify(item);
    node.appendChild(li);
  });
}

function renderMetrics(evidence) {
  const node = $("metricEvidence");
  node.innerHTML = "";
  Object.entries(evidence || {}).forEach(([key, value]) => {
    if (Array.isArray(value)) return;
    const div = document.createElement("div");
    div.innerHTML = `<span>${key}</span><strong>${value}</strong>`;
    node.appendChild(div);
  });
}

async function loadTopic(topic) {
  const [skill, progression, briefs, attention, workerContext] = await Promise.all([
    getJson(`/topics/${topic}/skill-cockpit`),
    getJson(`/topics/${topic}/skill-progression`),
    getJson(`/topics/${topic}/briefs`),
    getJson(`/topics/${topic}/human-attention-queue`),
    getJson(`/topics/${topic}/skill-worker-context`),
  ]);

  $("activeSkill").textContent = skill.active_skill_ref || "unknown";
  $("skillJudgment").textContent = skill.skill_use_vs_structure_judgment || skill.effectiveness_judgment || "";
  $("candidateFamily").textContent = skill.candidate_family || "unknown";
  $("skillStatus").textContent = skill.skill_status || "unknown";
  $("boundaryStatus").textContent = `triggered=${skill.metric_evidence?.boundary_triggered}`;
  $("nextAction").textContent = skill.next_action || "unknown";

  renderList("methodChanges", skill.method_changes);
  renderList("processChanges", skill.process_changes);
  renderList("standardChanges", skill.standard_changes);
  renderMetrics(skill.metric_evidence);
  renderList("forbiddenClaims", skill.forbidden_claims);

  const progressionNode = $("progression");
  progressionNode.innerHTML = "";
  (progression.steps || []).forEach((step) => {
    const li = document.createElement("li");
    li.className = step.status;
    li.textContent = `${step.label}: ${step.status}`;
    progressionNode.appendChild(li);
  });

  const attentionNode = $("attentionQueue");
  attentionNode.innerHTML = "";
  attention.forEach((item) => {
    const li = document.createElement("li");
    li.innerHTML = `<strong>${item.question}</strong>${item.agent_recommendation}`;
    attentionNode.appendChild(li);
  });

  $("mentorBrief").textContent = briefs.mentor_brief?.one_minute_summary || "No mentor brief.";
  $("skillWorkerContext").textContent = JSON.stringify({
    status: workerContext.status,
    target_worker: workerContext.target_worker,
    skill_target: workerContext.skill_target,
    evidence_boundary: workerContext.evidence_boundary,
    routing_constraints: workerContext.routing_constraints,
  }, null, 2);
  $("actionOutput").textContent = "";
}

async function init() {
  const topics = await getJson("/topics");
  const select = $("topicSelect");
  select.innerHTML = "";
  (topics.topics || ["real-task-001"]).forEach((topic) => {
    const option = document.createElement("option");
    option.value = topic;
    option.textContent = topic;
    select.appendChild(option);
  });
  select.value = topics.topics?.includes("real-task-001") ? "real-task-001" : select.value;
  select.addEventListener("change", () => loadTopic(select.value));
  $("overrideDryRun").addEventListener("click", async () => {
    $("actionOutput").textContent = JSON.stringify(await postJson(`/topics/${select.value}/direction-override?dry_run=true`), null, 2);
  });
  $("compileDryRun").addEventListener("click", async () => {
    $("actionOutput").textContent = JSON.stringify(await postJson(`/topics/${select.value}/compile-constraints?dry_run=true`), null, 2);
  });
  await loadTopic(select.value);
}

init().catch((error) => {
  $("actionOutput").textContent = String(error);
});
