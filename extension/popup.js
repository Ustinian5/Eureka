const DEFAULT_SETTINGS = {
  apiEndpoint: "http://127.0.0.1:8000",
  defaultProvider: "demo",
  defaultTemplate: "tech_research"
};

const queryInput = document.getElementById("queryInput");
const providerSelect = document.getElementById("providerSelect");
const templateSelect = document.getElementById("templateSelect");
const submitButton = document.getElementById("submitButton");
const cancelButton = document.getElementById("cancelButton");
const settingsButton = document.getElementById("settingsButton");
const clearButton = document.getElementById("clearButton");
const output = document.getElementById("output");
const traceList = document.getElementById("traceList");
const sourceList = document.getElementById("sourceList");
const statusText = document.getElementById("status");
const savedState = document.getElementById("savedState");
const exportMarkdownButton = document.getElementById("exportMarkdownButton");
const exportPdfButton = document.getElementById("exportPdfButton");
const connectionDot = document.getElementById("connectionDot");
const connectionText = document.getElementById("connectionText");

let settings = { ...DEFAULT_SETTINGS };
let activeController = null;
let currentReportId = null;

init();

settingsButton.addEventListener("click", () => chrome.runtime.openOptionsPage());
clearButton.addEventListener("click", resetOutput);
cancelButton.addEventListener("click", () => {
  if (activeController) {
    activeController.abort();
    addTrace("Client", "已取消当前请求。");
    setBusy(false, "已取消");
  }
});
submitButton.addEventListener("click", startResearch);
exportMarkdownButton.addEventListener("click", exportMarkdown);
exportPdfButton.addEventListener("click", exportPdf);

async function init() {
  settings = await chrome.storage.sync.get(DEFAULT_SETTINGS);
  templateSelect.value = settings.defaultTemplate;
  await loadProviders();
  await checkBackend();
}

async function loadProviders() {
  try {
    const response = await fetch(`${settings.apiEndpoint}/api/providers`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    providerSelect.innerHTML = data.providers
      .map((provider) => `<option value="${provider.id}">${escapeHtml(provider.name)}</option>`)
      .join("");
    providerSelect.value = settings.defaultProvider;
  } catch (_error) {
    providerSelect.innerHTML = '<option value="demo">Demo Offline Model</option>';
    providerSelect.value = "demo";
  }
}

async function checkBackend() {
  try {
    const response = await fetch(`${settings.apiEndpoint}/health`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    setConnection("ok", "本地后端已连接");
  } catch (_error) {
    setConnection("warn", "未连接后端，可在设置中检查地址");
  }
}

async function startResearch() {
  resetOutput();
  setBusy(true, "正在读取网页");
  activeController = new AbortController();

  try {
    const page = await getActivePageContext();
    if (!page.context) {
      throw new Error("当前页面没有可读取的正文内容。");
    }

    setBusy(true, "正在生成报告");
    await streamResearch(page, queryInput.value.trim(), activeController.signal);
    statusText.textContent = "已完成";
  } catch (error) {
    if (error.name !== "AbortError") {
      statusText.textContent = "请求失败";
      addTrace("Error", error.message || String(error));
    }
  } finally {
    activeController = null;
    setBusy(false);
  }
}

async function getActivePageContext() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab?.id) {
    throw new Error("无法获取当前标签页。");
  }

  const [injected] = await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: () => {
      const title = document.title ? `# ${document.title}\n\n` : "";
      return {
        context: `${title}${document.body?.innerText || ""}`.trim(),
        page_title: document.title || "",
        page_url: location.href
      };
    }
  });
  return injected?.result || { context: "", page_title: tab.title || "", page_url: tab.url || "" };
}

async function streamResearch(page, userQuery, signal) {
  const endpoint = providerSelect.value === "demo" ? "/api/demo/research" : "/api/research";
  const response = await fetch(`${settings.apiEndpoint}${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    signal,
    body: JSON.stringify({
      context: page.context,
      user_query: userQuery,
      page_title: page.page_title,
      page_url: page.page_url,
      provider: providerSelect.value,
      template: templateSelect.value
    })
  });

  if (!response.ok || !response.body) {
    throw new Error(`后端返回错误：${response.status}`);
  }

  await readNdjsonStream(response.body, handleStreamEvent);
}

async function readNdjsonStream(body, onEvent) {
  const reader = body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";
    for (const line of lines) {
      if (line.trim()) onEvent(JSON.parse(line));
    }
  }

  buffer += decoder.decode();
  if (buffer.trim()) onEvent(JSON.parse(buffer));
}

function handleStreamEvent(event) {
  if (event.type === "trace") {
    addTrace(event.agent, event.content);
    return;
  }
  if (event.type === "token") {
    output.textContent += event.content;
    output.scrollTop = output.scrollHeight;
    return;
  }
  if (event.type === "done") {
    currentReportId = event.report_id || null;
    savedState.textContent = currentReportId ? `已保存 #${currentReportId}` : "报告已生成";
    exportMarkdownButton.disabled = !currentReportId;
    exportPdfButton.disabled = !currentReportId;
    renderSources(event.report?.evidence || []);
    addTrace("Done", currentReportId ? `报告已保存：#${currentReportId}` : "报告生成完成");
  }
}

function renderSources(sources) {
  sourceList.innerHTML = sources
    .map((source, index) => `
      <article class="source-card">
        <strong>[${index + 1}] ${escapeHtml(source.title)}</strong>
        <span>${escapeHtml(source.source_type || "web")} · confidence ${Number(source.confidence || 0).toFixed(2)}</span>
        <p>${escapeHtml(source.quote || source.snippet || "")}</p>
      </article>
    `)
    .join("");
}

function addTrace(agent, content) {
  const item = document.createElement("li");
  item.innerHTML = `<span class="agent">${escapeHtml(agent)}</span>${escapeHtml(content)}`;
  traceList.appendChild(item);
  traceList.scrollTop = traceList.scrollHeight;
}

function exportMarkdown() {
  if (currentReportId) {
    chrome.tabs.create({ url: `${settings.apiEndpoint}/api/reports/${currentReportId}/markdown` });
  }
}

function exportPdf() {
  if (currentReportId) {
    chrome.tabs.create({ url: `${settings.apiEndpoint}/api/reports/${currentReportId}/pdf` });
  }
}

function resetOutput() {
  output.textContent = "";
  traceList.innerHTML = "";
  sourceList.innerHTML = "";
  currentReportId = null;
  savedState.textContent = "尚未生成报告";
  exportMarkdownButton.disabled = true;
  exportPdfButton.disabled = true;
  statusText.textContent = "准备读取当前网页";
}

function setBusy(isBusy, label) {
  submitButton.disabled = isBusy;
  cancelButton.disabled = !isBusy;
  if (label) statusText.textContent = label;
}

function setConnection(state, text) {
  connectionDot.dataset.state = state;
  connectionText.textContent = text;
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
