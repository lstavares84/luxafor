// HEURÍSTICA, FRÁGIL: nenhum desses sites tem API oficial de estado. Seletores e textos conferidos
// só por inspeção e vão quebrar quando o HTML mudar. Cada item é "a validar" no navegador do Lucas.
// Ajuste aqui sem mexer na lógica (content.js).
const SIGNA_SITES = {
  "chatgpt.com": {
    source: "chatgpt-web",
    generating: ['button[data-testid="stop-button"]', 'button[aria-label*="Stop" i]'],
    error: ['[class*="text-token-text-error"]', 'div[role="alert"]'],
    errorText: /something went wrong|an error occurred|network error|algo deu errado/i,
    limitText: /you'?ve (hit|reached) (the|your) .*limit|usage limit|limit resets|try again after|atingiu o limite/i,
  },
  "claude.ai": {
    source: "claude-web",
    generating: ['button[aria-label="Stop response"]', 'button[aria-label*="Stop" i]'],
    error: ['div[role="alert"]'],
    errorText: /something went wrong|error|erro/i,
    limitText: /out of (free )?messages|usage limit|message limit|5-hour limit|weekly limit|limit will reset|limite/i,
  },
  "grok.com": {
    source: "grok-web",
    generating: ['button[aria-label*="Stop" i]'],
    error: ['div[role="alert"]'],
    errorText: /something went wrong|error|erro/i,
    limitText: /reached your limit|rate limit|usage limit|limit resets|upgrade to continue|limite/i,
  },
};
// 5 h vs semanal (só pelo texto da mensagem de limite; a validar)
const SIGNA_WEEKLY = /week|semana|7[- ]day/i;
