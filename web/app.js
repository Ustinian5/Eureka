const API_BASE = "http://127.0.0.1:8000";

const providerSelect = document.getElementById("providerSelect");
const templateSelect = document.getElementById("templateSelect");
const titleInput = document.getElementById("titleInput");
const urlInput = document.getElementById("urlInput");
const contextInput = document.getElementById("contextInput");
const queryInput = document.getElementById("queryInput");
const traceList = document.getElementById("traceList");
const reportOutput = document.getElementById("reportOutput");
const evidenceList = document.getElementById("evidenceList");
const historyList = document.getElementById("historyList");
const savedState = document.getElementById("savedState");
const demoButton = document.getElementById("demoButton");
const runButton = document.getElementById("runButton");
const copyButton = document.getElementById("copyButton");
const exportMarkdownButton = document.getElementById("exportMarkdownButton");
const exportPdfButton = document.getElementById("exportPdfButton");
const refreshHistoryButton = document.getElementById("refreshHistoryButton");

let currentReportId = null;

loadProviders();
loadHistory();

demoButton.addEventListener("click", () => startResearch("/api/demo/research"));
runButton.addEventListener("click", () => startResearch("/api/research"));
copyButton.addEventListener("click", async () => {
  await navigator.clipboard.writeText(reportOutput.textContent);
});
exportMarkdownButton.addEventListener("click", exportMarkdown);
exportPdfButton.addEventListener("click", exportPdf);
refreshHistoryButton.addEventListener("click", loadHistory);

async function loadProviders() {
  try {
    const response = await fetch(`${API_BASE}/api/providers`);
    const data = await response.json();
    providerSelect.innerHTML = data.providers
      .map((provider) => `<option value="${provider.id}">${provider.name} (${provider.model})</option>`)
      .join("");
    providerSelect.value = "demo";
  } catch (_error) {
    providerSelect.innerHTML = '<option value="demo">Demo Offline Model</option>';
  }
}

async function startResearch(path) {
  traceList.innerHTML = "";
  reportOutput.textContent = "";
  evidenceList.innerHTML = "";
  currentReportId = null;
  savedState.textContent = "正在生成报告";
  setBusy(true);

  try {
    const response = await fetch(`${API_BASE}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        context: contextInput.value,
        user_query: queryInput.value,
        page_title: titleInput.value,
        page_url: urlInput.value,
        provider: providerSelect.value,
        template: templateSelect.value
      })
    });

    if (!response.ok || !response.body) {
      throw new Error(`请求失败：${response.status}`);
    }

    await readNdjsonStream(response.body, handleStreamEvent);
  } catch (error) {
    addTrace("Client", error.message || String(error));
  } finally {
    setBusy(false);
    loadHistory();
  }
}

async function readNdjsonStream(body, onEvent) {
  const reader = body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) {
      break;
    }
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";
    for (const line of lines) {
      if (line.trim()) {
        onEvent(JSON.parse(line));
      }
    }
  }

  buffer += decoder.decode();
  if (buffer.trim()) {
    onEvent(JSON.parse(buffer));
  }
}

function handleStreamEvent(event) {
  if (event.type === "trace") {
    addTrace(event.agent, event.content);
    return;
  }
  if (event.type === "token") {
    reportOutput.textContent += event.content;
    reportOutput.scrollTop = reportOutput.scrollHeight;
    return;
  }
  if (event.type === "done") {
    currentReportId = event.report_id || null;
    savedState.textContent = currentReportId ? `报告已保存：#${currentReportId}` : "报告生成完成但未保存";
    renderEvidence(event.report?.evidence || []);
    addTrace("Done", currentReportId ? `报告已保存：#${currentReportId}` : "报告生成完成");
  }
}

async function loadHistory() {
  try {
    const response = await fetch(`${API_BASE}/api/reports`);
    const data = await response.json();
    historyList.innerHTML = data.reports
      .map((report) => `<li><button data-report-id="${report.id}">#${report.id} ${escapeHtml(report.title)}</button></li>`)
      .join("");
    historyList.querySelectorAll("button").forEach((button) => {
      button.addEventListener("click", () => loadReport(button.dataset.reportId));
    });
  } catch (_error) {
    historyList.innerHTML = "<li>暂无历史</li>";
  }
}

async function loadReport(reportId) {
  const response = await fetch(`${API_BASE}/api/reports/${reportId}`);
  const data = await response.json();
  currentReportId = reportId;
  savedState.textContent = `已打开历史报告：#${reportId}`;
  reportOutput.textContent = data.report.final_report;
  traceList.innerHTML = "";
  data.traces.forEach((event) => addTrace(event.agent, event.content));
  renderEvidence(data.evidence || []);
}

function renderEvidence(evidence) {
  evidenceList.innerHTML = evidence
    .map((item, index) => `
      <article class="evidence-card">
        <strong>[${index + 1}] ${escapeHtml(item.title)}</strong>
        <div class="evidence-meta">${escapeHtml(item.source_type || "web")} · confidence ${Number(item.confidence || 0).toFixed(2)}</div>
        <p>${escapeHtml(item.quote || item.snippet || "")}</p>
        <a href="${escapeHtml(item.url)}" target="_blank" rel="noreferrer">${escapeHtml(item.url)}</a>
      </article>
    `)
    .join("");
}

function exportMarkdown() {
  if (!currentReportId) {
    addTrace("Export", "当前报告尚未保存，无法导出 Markdown。");
    return;
  }
  window.open(`${API_BASE}/api/reports/${currentReportId}/markdown`, "_blank");
}

function exportPdf() {
  if (!currentReportId) {
    addTrace("Export", "当前报告尚未保存，无法导出 PDF。");
    return;
  }
  window.open(`${API_BASE}/api/reports/${currentReportId}/pdf`, "_blank");
}

function addTrace(agent, content) {
  const item = document.createElement("li");
  item.innerHTML = `<span class="agent">${agent}</span>${escapeHtml(content)}`;
  traceList.appendChild(item);
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;"
  })[char]);
}

function setBusy(isBusy) {
  demoButton.disabled = isBusy;
  runButton.disabled = isBusy;
}
