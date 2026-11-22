const t = document.getElementById("t");
chrome.storage.local.get("token").then(({ token }) => { t.value = token || ""; });
document.getElementById("s").onclick = async () => {
  await chrome.storage.local.set({ token: t.value.trim() });
  document.getElementById("ok").textContent = "salvo";
};
