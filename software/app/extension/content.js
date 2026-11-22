// Decide o estado da IA nesta aba e avisa o background só quando muda.
//   gerando (botão "parar" visível)              -> processando
//   texto de limite                               -> limite (5 h ou semanal pelo texto)
//   alerta de erro                                -> erro
//   terminou com a aba em segundo plano           -> atencao (até você voltar para a aba)
//   resto                                         -> desocupada
(() => {
  const site = SIGNA_SITES[location.hostname.replace(/^www\./, "")];
  if (!site) return;
  let last = null, wasGenerating = false, needsLook = false;

  const any = (sels) => sels.some((s) => { try { return document.querySelector(s); } catch { return false; } });
  const text = (sels) => sels.map((s) => [...document.querySelectorAll(s)].map((e) => e.innerText).join(" ")).join(" ");

  function compute() {
    const gen = any(site.generating);
    if (gen) { wasGenerating = true; needsLook = false; return "processando"; }
    if (wasGenerating) { wasGenerating = false; needsLook = document.hidden; }
    const body = (document.body?.innerText || "").slice(-4000); // só o fim da conversa
    if (site.limitText.test(body)) return SIGNA_WEEKLY.test(body) ? "limite-semanal" : "limite";
    if (any(site.error) && site.errorText.test(text(site.error))) return "erro";
    if (needsLook) return "atencao";
    return "desocupada";
  }

  function tick() {
    const st = compute();
    if (st !== last) {
      last = st;
      chrome.runtime.sendMessage({ type: "signa-state", source: site.source, state: st }).catch(() => {});
    }
  }

  document.addEventListener("visibilitychange", () => { if (!document.hidden) needsLook = false; tick(); });
  new MutationObserver(() => { clearTimeout(tick.t); tick.t = setTimeout(tick, 250); })
    .observe(document.documentElement, { subtree: true, childList: true, attributes: true });
  setInterval(tick, 2000);
  tick();
})();
