// Repassa o estado de cada aba ao app SIGNA em http://127.0.0.1:47623 (token nas opções).
const URL_AI = "http://127.0.0.1:47623/v1/ai";

async function post(body) {
  const { token } = await chrome.storage.local.get("token");
  if (!token) return;
  try {
    await fetch(URL_AI, { method: "POST", headers: { "Content-Type": "application/json", "X-Signa-Token": token },
                          body: JSON.stringify(body) });
  } catch (e) { /* app fechado: ignora */ }
}

const tabSource = new Map();
chrome.runtime.onMessage.addListener((msg, sender) => {
  if (msg?.type !== "signa-state" || !sender.tab) return;
  tabSource.set(sender.tab.id, msg.source);
  post({ source: msg.source, session: `tab-${sender.tab.id}`, state: msg.state });
});
chrome.tabs.onRemoved.addListener((tabId) => {
  const src = tabSource.get(tabId);
  if (src) post({ source: src, session: `tab-${tabId}`, state: "remove" });
  tabSource.delete(tabId);
});
