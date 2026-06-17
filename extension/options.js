const DEFAULT_SETTINGS = {
  apiEndpoint: "http://127.0.0.1:8000",
  defaultProvider: "demo",
  defaultTemplate: "tech_research"
};

const apiEndpointInput = document.getElementById("apiEndpointInput");
const defaultProviderSelect = document.getElementById("defaultProviderSelect");
const defaultTemplateSelect = document.getElementById("defaultTemplateSelect");
const saveButton = document.getElementById("saveButton");
const resetButton = document.getElementById("resetButton");
const statusText = document.getElementById("status");

loadSettings();

saveButton.addEventListener("click", async () => {
  const settings = {
    apiEndpoint: normalizeEndpoint(apiEndpointInput.value),
    defaultProvider: defaultProviderSelect.value,
    defaultTemplate: defaultTemplateSelect.value
  };
  await chrome.storage.sync.set(settings);
  statusText.textContent = "设置已保存。";
});

resetButton.addEventListener("click", async () => {
  await chrome.storage.sync.set(DEFAULT_SETTINGS);
  applySettings(DEFAULT_SETTINGS);
  statusText.textContent = "已恢复默认设置。";
});

async function loadSettings() {
  const settings = await chrome.storage.sync.get(DEFAULT_SETTINGS);
  applySettings(settings);
}

function applySettings(settings) {
  apiEndpointInput.value = settings.apiEndpoint;
  defaultProviderSelect.value = settings.defaultProvider;
  defaultTemplateSelect.value = settings.defaultTemplate;
}

function normalizeEndpoint(value) {
  return (value || DEFAULT_SETTINGS.apiEndpoint).trim().replace(/\/+$/, "");
}
