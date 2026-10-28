/* E0.1: fixed synthetic fixture presentation only; no market inference or execution. */
(function (root) {
  "use strict";

  const ACTIONS = Object.freeze({
    OBSERVE: { label: "观察", tone: "caution" },
    WAIT_TRIGGER: { label: "等待触发", tone: "caution" },
    DECISION_REVIEW: { label: "决策审查", tone: "review" },
    HOLD: { label: "持有情景", tone: "review" },
    REDUCE: { label: "减仓情景", tone: "caution" },
    EXIT: { label: "退出情景", tone: "blocked" },
    NO_TRADE: { label: "不交易", tone: "blocked" }
  });
  const BLOCK_REASONS = Object.freeze({
    NONE: "无额外情景阻断（风险门仍关闭）",
    INSUFFICIENT_EVIDENCE: "证据不足",
    CONFOUNDED: "多重解释混杂",
    WINDOW_CLOSED: "交易窗口关闭",
    NON_EXECUTABLE: "不可执行"
  });
  const POSTURES = Object.freeze({ SELECTIVE: "选择性研究", NO_NEW_RISK: "不新增风险", UNKNOWN: "市场姿态未知" });
  const FIXTURE_PATH = "./fixtures/decision-demo.json";
  const asObject = (shape) => ({ type: "object", shape });
  const asArray = (item, min = 1, max = 30) => ({ type: "array", item, min, max });
  const oneOf = (...values) => ({ type: "enum", values });
  const text = { type: "string" };
  const timestamp = { type: "timestamp" };
  const syntheticId = { type: "syntheticId" };
  const unknownValue = asObject({ value: oneOf(null), status: oneOf("UNKNOWN"), reason: text });
  const timeLine = asObject({ first_public_at: unknownValue, available_at: unknownValue, ingested_at: timestamp, signal_generated_at: unknownValue });
  const candidateShape = asObject({
    id: syntheticId, code: syntheticId, name: text, data_classification: oneOf("SYNTHETIC_DEMO_DATA"),
    action: oneOf(...Object.keys(ACTIONS)), block_reason: oneOf(...Object.keys(BLOCK_REASONS)),
    trigger_or_wait: text, earliest_execution: unknownValue, reference_price_area: unknownValue,
    risk_gate: asObject({ status: oneOf("BLOCKED_NEW_RISK"), reason: text, new_risk_allowed: oneOf(false), risk_reduction_allowed: oneOf(true) }),
    maximum_candidate_position: asObject({ value: oneOf(null), status: oneOf("CEO_RISK_MANDATE_PENDING"), reason: text }),
    invalidation: text,
    exit_profit_management: asObject({ summary: text, right_tail_status: oneOf("RESEARCH_ONLY"), right_tail_reason: text }),
    evidence: asObject({ grade: oneOf("SYNTHETIC_UNVALIDATED"), strongest_support: text, strongest_counterevidence: text }),
    execution: asObject({ residual_risk: text, exit_feasibility: asObject({ status: oneOf("UNKNOWN", "CONDITIONAL_DEMO"), reason: text }), constraints: asArray(text) }),
    no_trade_reason: text, unknown_reason: text,
    details: asObject({
      why_research: text, why_fail: text, alternatives: asArray(text), market_state: text, sentiment_state: text, portfolio_state: text,
      capital_proxy: unknownValue, information_timeline: timeLine, expectation_gap: text, business_exposure: text,
      claims: asArray(asObject({ kind: oneOf("FACT", "INFERENCE", "HYPOTHESIS"), text })), monitoring: text, defensive_exit: text
    }),
    audit: asObject({
      source_id: { type: "syntheticSource" }, source_description: text, first_public_at: unknownValue, data_version: text, rule_version: text,
      model_version: unknownValue, validation_status: oneOf("SYNTHETIC_NOT_VALIDATED"), support_path: asArray(text), counterevidence_path: asArray(text),
      historical_samples: unknownValue, invalidation_status: oneOf("NOT_VALIDATED"), snapshot_id: text, attribution_status: oneOf("NOT_VALIDATED")
    })
  });
  const fixtureShape = asObject({
    contract_version: oneOf("0.1"), data_classification: oneOf("SYNTHETIC_DEMO_DATA"), disclaimer: text,
    snapshot: asObject({ id: text, generated_at: timestamp, data_as_of: timestamp, timezone: oneOf("Asia/Singapore"), freshness: oneOf("STATIC_SYNTHETIC_SNAPSHOT"), system_status: oneOf("READ_ONLY_PROTOTYPE") }),
    authorization: asObject({
      id: oneOf("AUTH-ENG-0002"),
      content_hash: oneOf("e221e81ffae10410703569512060c3c6adb1e05078d0a64004f406c34be4fcc1"),
      genesis_c1_commit: oneOf("b2a975e06aa0ac30061a880d7a4877a61fa7db5d"),
      genesis_c2_commit: oneOf("4f988f01a57929756b4d2c6b0f678dfaf564dc19"),
      issued_at: oneOf("2026-10-28T07:11:04Z"), expires_at: oneOf("2026-11-04T07:11:04Z"), engineering_scope: oneOf("E0.1_SYNTHETIC_DECISION_WEB_PROTOTYPE"),
      data_4_1: oneOf("PAUSED_NOT_AUTHORIZED"), read_only: oneOf(true), live_data_authorized: oneOf(false), models_authorized: oneOf(false),
      backtesting_authorized: oneOf(false), real_recommendations_authorized: oneOf(false), merge_authorized: oneOf(false),
      deployment_authorized: oneOf(false), broker_access_authorized: oneOf(false), trading_authorized: oneOf(false), human_release_reference: text
    }),
    display: asObject({ max_candidates: oneOf(3), default_scenario: text }),
    scenarios: asArray(asObject({ id: text, label: text, market_posture: oneOf(...Object.keys(POSTURES)), posture_reason: text, new_risk_allowed: oneOf(false), risk_reduction_allowed: oneOf(true), candidate_ids: asArray(syntheticId, 1, 3) }), 1, 10),
    candidates: asArray(candidateShape, 1, 30)
  });

  function fail(path, message) {
    throw new TypeError(`${path}: ${message}`);
  }

  // A deliberately finite structural validator, not a general JSON Schema engine.
  // Strict keys and fixed safety enums cover every field this prototype displays.
  function check(value, rule, path) {
    if (rule.type === "object") {
      if (value === null || typeof value !== "object" || Array.isArray(value)) fail(path, "应为对象");
      for (const key of Object.keys(rule.shape)) {
        if (!Object.prototype.hasOwnProperty.call(value, key)) fail(`${path}.${key}`, "缺少必需字段");
        check(value[key], rule.shape[key], `${path}.${key}`);
      }
      for (const key of Object.keys(value)) {
        if (!Object.prototype.hasOwnProperty.call(rule.shape, key)) fail(`${path}.${key}`, "未支持的额外字段");
      }
    } else if (rule.type === "array") {
      if (!Array.isArray(value) || value.length < rule.min || value.length > rule.max) fail(path, "数组长度或类型无效");
      value.forEach((item, index) => check(item, rule.item, `${path}[${index}]`));
    } else if (rule.type === "enum") {
      if (!rule.values.includes(value)) fail(path, "枚举值不合法或超出原型边界");
    } else if (rule.type === "string") {
      if (typeof value !== "string" || value.trim().length === 0 || value.length > 4000) fail(path, "应为非空且长度受限的文本");
    } else if (rule.type === "timestamp") {
      if (typeof value !== "string" || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/.test(value) || !Number.isFinite(Date.parse(value)) || new Date(value).toISOString().replace(".000Z", "Z") !== value) fail(path, "应为有效的固定 UTC 时间戳");
    } else if (rule.type === "syntheticId") {
      if (typeof value !== "string" || !/^SYN-[A-Z]+$/.test(value)) fail(path, "仅接受 SYN- 前缀的虚构证券标识");
    } else if (rule.type === "syntheticSource") {
      if (typeof value !== "string" || !/^SYN-SOURCE-[A-Z]+$/.test(value)) fail(path, "仅接受虚构来源标识");
    }
  }

  function validateFixture(fixture) {
    check(fixture, fixtureShape, "fixture");
    const candidates = new Map();
    for (const candidate of fixture.candidates) {
      if (candidates.has(candidate.id)) fail("fixture.candidates", "候选标识重复");
      if (candidate.id !== candidate.code || !candidate.name.startsWith("虚构·") || candidate.name.length <= 3) fail(`fixture.candidates.${candidate.id}`, "候选必须明确为虚构证券");
      if (candidate.audit.snapshot_id !== fixture.snapshot.id) fail(`fixture.candidates.${candidate.id}.audit.snapshot_id`, "快照引用不一致");
      if (candidate.action === "NO_TRADE" && candidate.block_reason === "NONE") fail(`fixture.candidates.${candidate.id}.block_reason`, "不交易状态须有明确阻断原因");
      candidates.set(candidate.id, candidate);
    }
    const scenarios = new Set();
    const referencedCandidates = new Set();
    for (const scenario of fixture.scenarios) {
      if (scenarios.has(scenario.id)) fail("fixture.scenarios", "场景标识重复");
      scenarios.add(scenario.id);
      if (new Set(scenario.candidate_ids).size !== scenario.candidate_ids.length) fail(`fixture.scenarios.${scenario.id}`, "场景候选重复");
      for (const id of scenario.candidate_ids) {
        if (!candidates.has(id)) fail(`fixture.scenarios.${scenario.id}.candidate_ids`, "引用的候选不存在");
        referencedCandidates.add(id);
      }
    }
    if (referencedCandidates.size !== candidates.size) fail("fixture.candidates", "存在未被任何固定场景引用的候选");
    if (!scenarios.has(fixture.display.default_scenario)) fail("fixture.display.default_scenario", "默认场景不存在");
    if (Date.parse(fixture.authorization.expires_at) <= Date.parse(fixture.authorization.issued_at)) fail("fixture.authorization.expires_at", "到期时间须晚于签发时间");
    return true;
  }

  if (typeof module !== "undefined" && module.exports) module.exports = Object.freeze({ validateFixture });
  if (typeof document === "undefined") return;
  root.E01Prototype = Object.freeze({ validateFixture });

  function element(tag, className, value) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (value !== undefined) node.textContent = value;
    return node;
  }
  const byId = (id) => document.getElementById(id);
  const setText = (id, value) => { byId(id).textContent = value; };
  function formatDate(value) {
    const parts = new Intl.DateTimeFormat("zh-CN", { timeZone: "Asia/Singapore", year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", hourCycle: "h23" }).format(new Date(value));
    return `${parts} SGT`;
  }
  function compactField(label, value, className = "") {
    const field = element("div", `compact-field ${className}`.trim());
    field.append(element("p", "field-label", label), element("p", "", value));
    return field;
  }
  function unknownMetric(label, value) {
    const metric = element("div");
    metric.append(element("p", "field-label", label), element("p", "unknown-value", value.status), element("p", "unknown-reason", value.reason));
    return metric;
  }
  function detailsSection(title) {
    const details = element("details", "card-details");
    const summary = element("summary");
    const marker = element("span", "", "＋");
    marker.setAttribute("aria-hidden", "true");
    summary.append(element("span", "", title), marker);
    const content = element("div", "detail-content");
    details.append(summary, content);
    return { details, content };
  }
  function addNarrative(container, title, value) {
    container.append(element("h4", "", title), element("p", "", value));
  }
  function addList(container, title, values) {
    container.append(element("h4", "", title));
    const list = element("ul");
    for (const value of values) list.append(element("li", "", value));
    container.append(list);
  }
  function addDefinition(list, label, value) {
    list.append(element("dt", "", label), element("dd", "", value));
  }
  function describeUnknown(value) { return `${value.status} · ${value.reason}`; }

  function renderCandidate(candidate, index) {
    const card = element("article", "candidate-card");
    const headingId = `candidate-${candidate.id}`;
    card.setAttribute("aria-labelledby", headingId);
    const top = element("div", "candidate-card-top");
    const eyebrow = element("div", "candidate-eyebrow");
    eyebrow.append(element("span", "", `合成候选 / 0${index + 1}`), element("span", "candidate-code", candidate.code));
    const titleRow = element("div", "candidate-title-row");
    const title = element("h3", "", candidate.name);
    title.id = headingId;
    const action = element("span", "action-badge", ACTIONS[candidate.action].label);
    action.dataset.tone = ACTIONS[candidate.action].tone;
    titleRow.append(title, action);
    top.append(eyebrow, titleRow, element("p", "action-code", `${candidate.action} · ${candidate.block_reason}`));

    const body = element("div", "candidate-body");
    const trigger = element("div", "trigger-field");
    trigger.append(element("p", "field-label", "触发 / 等待条件"), element("p", "trigger-value", candidate.trigger_or_wait));
    const metrics = element("div", "metrics-grid");
    metrics.append(unknownMetric("最早可执行时间", candidate.earliest_execution), unknownMetric("参考价格区间", candidate.reference_price_area));
    const risk = element("div", "risk-gate");
    risk.append(element("strong", "", "风险门 · 禁止新增风险"), element("p", "", candidate.risk_gate.reason));
    const position = element("div", "position-group");
    const positionLine = element("div", "position-line");
    positionLine.append(element("span", "position-label", "最大候选仓位"), element("span", "position-state", "UNKNOWN / 待批准"));
    position.append(positionLine, element("p", "position-reason", candidate.maximum_candidate_position.reason));
    const evidence = element("div", "evidence-block");
    const evidenceTop = element("div", "evidence-top");
    const evidenceTag = element("span", "evidence-tag", "合成 · 未验证");
    evidenceTag.title = candidate.evidence.grade;
    evidenceTop.append(element("span", "evidence-label", "证据对照"), evidenceTag);
    evidence.append(evidenceTop);
    for (const [label, value, marker, className] of [["最强支持", candidate.evidence.strongest_support, "+", ""], ["最强反证", candidate.evidence.strongest_counterevidence, "−", "counter"]]) {
      const item = element("div", `evidence-item ${className}`.trim());
      const paragraph = element("p");
      paragraph.append(element("strong", "", `${label} · `), document.createTextNode(value));
      item.append(element("span", "evidence-marker", marker), paragraph);
      evidence.append(item);
    }
    const unknown = element("div", "unknown-alert");
    unknown.append(element("strong", "", "UNKNOWN / 未知原因"), element("p", "", candidate.unknown_reason));
    body.append(trigger, metrics, risk, position, evidence,
      compactField("失效条件", candidate.invalidation), compactField("退出与利润管理", candidate.exit_profit_management.summary),
      compactField("残余执行风险", candidate.execution.residual_risk), compactField(`退出可行性 · ${candidate.execution.exit_feasibility.status}`, candidate.execution.exit_feasibility.reason),
      compactField(`当前未执行原因 · ${BLOCK_REASONS[candidate.block_reason]}`, candidate.no_trade_reason), unknown);

    const reasoning = detailsSection("研究解释与执行约束");
    addNarrative(reasoning.content, "为什么研究 / 为什么可能错", `${candidate.details.why_research} ${candidate.details.why_fail}`);
    addList(reasoning.content, "替代解释", candidate.details.alternatives);
    addNarrative(reasoning.content, "市场 / 情绪 / 组合状态", `${candidate.details.market_state} ${candidate.details.sentiment_state} ${candidate.details.portfolio_state}`);
    addNarrative(reasoning.content, "资金代理", describeUnknown(candidate.details.capital_proxy));
    const timeline = element("dl", "audit-dl");
    const times = candidate.details.information_timeline;
    addDefinition(timeline, "首次公开", describeUnknown(times.first_public_at));
    addDefinition(timeline, "首次可得", describeUnknown(times.available_at));
    addDefinition(timeline, "夹具记录时间", formatDate(times.ingested_at));
    addDefinition(timeline, "信号生成", describeUnknown(times.signal_generated_at));
    reasoning.content.append(element("h4", "", "信息时间链"), timeline);
    addNarrative(reasoning.content, "预期差与业务暴露", `${candidate.details.expectation_gap} ${candidate.details.business_exposure}`);
    reasoning.content.append(element("h4", "", "事实 / 推断 / 假设"));
    for (const claim of candidate.details.claims) {
      const paragraph = element("p");
      paragraph.append(element("span", "claim-kind", claim.kind), document.createTextNode(claim.text));
      reasoning.content.append(paragraph);
    }
    addList(reasoning.content, "执行约束", candidate.execution.constraints);
    addNarrative(reasoning.content, "监控与防守退出", `${candidate.details.monitoring} ${candidate.details.defensive_exit}`);
    addNarrative(reasoning.content, `Right-Tail / ${candidate.exit_profit_management.right_tail_status}`, candidate.exit_profit_management.right_tail_reason);

    const audit = detailsSection("来源、验证与审计记录");
    const auditList = element("dl", "audit-dl");
    for (const [label, value] of [
      ["来源标识", candidate.audit.source_id], ["来源说明", candidate.audit.source_description], ["首次公开", describeUnknown(candidate.audit.first_public_at)],
      ["数据版本", candidate.audit.data_version], ["规则版本", candidate.audit.rule_version], ["模型版本", describeUnknown(candidate.audit.model_version)],
      ["验证状态", candidate.audit.validation_status], ["支持路径", candidate.audit.support_path.join("；")], ["反证路径", candidate.audit.counterevidence_path.join("；")],
      ["历史样本", describeUnknown(candidate.audit.historical_samples)], ["失效验证", candidate.audit.invalidation_status], ["归因状态", candidate.audit.attribution_status],
      ["快照引用", candidate.audit.snapshot_id], ["仓位状态", candidate.maximum_candidate_position.status], ["证据级别", candidate.evidence.grade], ["数据分类", candidate.data_classification]
    ]) addDefinition(auditList, label, value);
    audit.content.append(auditList);
    card.append(top, body, reasoning.details, audit.details);
    return card;
  }

  function renderScenario(fixture, id) {
    const scenario = fixture.scenarios.find((entry) => entry.id === id);
    if (!scenario) throw new TypeError("场景不在已校验的固定夹具中");
    const candidateMap = new Map(fixture.candidates.map((candidate) => [candidate.id, candidate]));
    const cards = scenario.candidate_ids.map((candidateId, index) => renderCandidate(candidateMap.get(candidateId), index));
    setText("candidate-count", `${cards.length} 项 / 最多 ${fixture.display.max_candidates} 项`);
    setText("posture-name", POSTURES[scenario.market_posture]);
    setText("posture-code", scenario.market_posture);
    setText("posture-reason", scenario.posture_reason);
    byId("candidate-grid").replaceChildren(...cards);
  }

  function render(fixture) {
    setText("snapshot-date", formatDate(fixture.snapshot.data_as_of));
    setText("snapshot-freshness", "固定合成快照 · 无实时刷新");
    byId("snapshot-freshness").title = fixture.snapshot.freshness;
    setText("snapshot-system", "只读展示 / 未做经济验证");
    byId("snapshot-system").title = fixture.snapshot.system_status;
    setText("snapshot-id", fixture.snapshot.id);
    setText("data-disclaimer", fixture.disclaimer);
    setText("contract-version", `Decision Output / v${fixture.contract_version}`);
    setText("generated-at", `夹具生成：${formatDate(fixture.snapshot.generated_at)}`);
    setText("authorization-id", fixture.authorization.id);
    setText("authorization-issued", formatDate(fixture.authorization.issued_at));
    setText("authorization-expires", formatDate(fixture.authorization.expires_at));
    const registration = byId("registration-metadata");
    registration.replaceChildren();
    for (const [label, value] of [["授权内容哈希", fixture.authorization.content_hash], ["Genesis / C1", fixture.authorization.genesis_c1_commit], ["Genesis / C2", fixture.authorization.genesis_c2_commit], ["工程范围", fixture.authorization.engineering_scope], ["DATA-4.1", fixture.authorization.data_4_1], ["人类放行记录", fixture.authorization.human_release_reference]]) addDefinition(registration, label, value);
    const select = byId("scenario-select");
    select.replaceChildren();
    for (const scenario of fixture.scenarios) {
      const option = element("option", "", scenario.label);
      option.value = scenario.id;
      select.append(option);
    }
    select.value = fixture.display.default_scenario;
    renderScenario(fixture, select.value);
    select.addEventListener("change", () => {
      try { renderScenario(fixture, select.value); } catch (error) { showError(error); }
    });
    byId("load-status").hidden = true;
    byId("validated-content").hidden = false;
  }

  function showError(error) {
    byId("validated-content").hidden = true;
    byId("candidate-grid").replaceChildren();
    const status = byId("load-status");
    status.hidden = false;
    status.className = "load-status load-error";
    status.setAttribute("role", "alert");
    status.replaceChildren(element("strong", "", "演示数据校验未通过，已停止渲染。"), element("p", "", error instanceof Error ? error.message : "无法读取受支持的本地合成夹具。"), element("p", "", "请通过本地 HTTP 服务打开并检查本仓库的固定夹具；本页不会补值、改用外部数据或自动重试。"));
  }

  async function initialize() {
    try {
      if (!/^https?:$/.test(root.location.protocol)) throw new Error("当前不是 HTTP 页面；浏览器无法安全加载本地 JSON 文件。");
      const url = new URL(FIXTURE_PATH, root.location.href);
      if (url.origin !== root.location.origin) throw new Error("拒绝加载非同源数据。");
      const response = await root.fetch(url.href, { credentials: "omit", cache: "no-store", redirect: "error" });
      if (!response.ok) throw new Error(`本地夹具加载失败（HTTP ${response.status}）。`);
      const fixture = await response.json();
      validateFixture(fixture);
      render(fixture);
    } catch (error) { showError(error); }
  }
  initialize();
})(typeof globalThis !== "undefined" ? globalThis : this);
