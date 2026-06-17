function extractPageContext() {
  const title = document.title ? `# ${document.title}\n\n` : "";
  const text = document.body?.innerText || "";
  return `${title}${text}`.trim();
}

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message?.type !== "EUREKA_GET_CONTEXT") {
    return false;
  }

  sendResponse({
    context: extractPageContext(),
    page_title: document.title || "",
    page_url: location.href
  });
  return true;
});
