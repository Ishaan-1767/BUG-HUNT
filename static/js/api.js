// Thin fetch wrapper. Every call is also written to the dev console.
const Con = {
  log(msg) {
    const t = new Date().toLocaleTimeString("en-GB");
    const el = document.getElementById("conLog");
    if (!el) return;
    el.textContent += `[${t}] ${msg}\n`;
    el.parentElement.scrollTop = el.parentElement.scrollHeight;
  },
};

const API = {
  async req(path, body, method) {
    const opts = { method: method || (body === undefined ? "GET" : "POST"), headers: { "Content-Type": "application/json" }, credentials: "same-origin" };
    if (body !== undefined) opts.body = JSON.stringify(body);
    Con.log(`API REQUEST ${opts.method} ${path}`);
    const res = await fetch(path, opts);
    const data = await res.json().catch(() => ({}));
    Con.log(`STATUS ${res.status}`);
    if (!res.ok) throw Object.assign(new Error(data.error || "Request failed"), { status: res.status });
    return data;
  },
  health: () => API.req("/api/health"),
  missions: () => API.req("/api/game/missions"),
  mission: (id) => API.req(`/api/game/mission/${id}`),
  start: (id) => API.req(`/api/game/mission/${id}/start`, {}),
  submit: (id, report) => API.req(`/api/game/mission/${id}/submit`, report),
  state: () => API.req("/api/game/state"),
  reset: () => API.req("/api/game/reset", {}),
  retry: () => API.req("/api/game/retry", {}),
  board: () => API.req("/api/leaderboard"),
  saveScore: (name) => API.req("/api/leaderboard", { name }),
};
