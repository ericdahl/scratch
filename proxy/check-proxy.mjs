// Preflight: does the proxy + CA trust work for pi's exact HTTP stack?
//   source proxy-env.sh && node check-proxy.mjs
// Uses pi's own bundled undici + EnvHttpProxyAgent, same as pi does.
const PIROOT = "/opt/homebrew/lib/node_modules/@earendil-works/pi-coding-agent";
const undici = await import(
  process.argv[2] ??
    "/opt/homebrew/Cellar/pi-coding-agent/0.85.0/libexec/lib/node_modules/@earendil-works/pi-coding-agent/node_modules/undici/index.js"
);
undici.setGlobalDispatcher(new undici.EnvHttpProxyAgent({ allowH2: false, proxyTunnel: true }));
undici.install?.();
const urls = [
  "https://chatgpt.com/backend-api/codex/responses", // pi openai-codex
  "https://api.anthropic.com/v1/messages",           // claude
  "https://github.com",                              // blind-tunnelled control
];
for (const url of urls) {
  try {
    const r = await fetch(url, { method: "GET" });
    console.log("OK  ", String(r.status).padEnd(4), url);
  } catch (e) {
    console.log("FAIL", "    ", url, "->", e.message, "|", e.cause?.code ?? e.cause?.message);
  }
}
