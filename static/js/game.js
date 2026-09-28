const $ = (s, r = document) => r.querySelector(s);
const show = (id) => { document.querySelectorAll(".screen").forEach((s) => (s.hidden = s.id !== id)); };
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

// Interactive "broken applications". The bugs live here on purpose; the answers live on the server.
const Widgets = {
  login(el) {
    el.innerHTML = `<h3>NEXUS PORTAL</h3><label>Username<input class="u" value="admin"></label><label>Password<input class="p" type="password"></label><button class="btn go" type="button">SIGN IN</button><p class="out" aria-live="polite"></p>`;
    $(".go", el).onclick = () => {
      const u = $(".u", el).value, p = $(".p", el).value;
      const ok = u === "admin" && (p === "nexus123" || p === ""); // BUG: empty password passes
      const out = $(".out", el); out.className = "out" + (ok ? "" : " bad");
      out.textContent = ok ? "✓ ACCESS GRANTED" : "✕ ACCESS DENIED";
      Con.log(ok ? "AUTH OK" : "AUTH REJECTED");
    };
  },
  api(el, d) {
    el.innerHTML = `<h3>${esc(d.request)}</h3><pre class="json">HTTP ${d.status} OK\n${esc(JSON.stringify(d.body, null, 2))}</pre>`;
    Con.log(`STATUS ${d.status}`);
  },
  calc(el) {
    el.innerHTML = `<h3>FINANCE CALC</h3><div class="row"><input class="a" type="number" value="10" aria-label="A"><select class="o" aria-label="Operator"><option>+</option><option>-</option><option>*</option><option selected>/</option></select><input class="b" type="number" value="2" aria-label="B"></div><button class="btn go" type="button">CALCULATE</button><p class="out" aria-live="polite"></p>`;
    $(".go", el).onclick = () => {
      const a = +$(".a", el).value, b = +$(".b", el).value, o = $(".o", el).value;
      const r = { "+": a + b, "-": a - b, "*": a * b, "/": b === 0 ? 0 : a / b }[o]; // BUG: x/0 = 0
      $(".out", el).textContent = `${a} ${o} ${b} = ${r}`;
      Con.log(`CALC ${a} ${o} ${b} -> ${r}`);
    };
  },
  form(el) {
    el.innerHTML = `<h3>REGISTER</h3><label>Email<input class="e" type="text"></label><label>Password<input class="p" type="password"></label><label>Confirm<input class="c" type="password"></label><button class="btn go" type="button">CREATE ACCOUNT</button><p class="out" aria-live="polite"></p>`;
    $(".go", el).onclick = () => {
      const e = $(".e", el).value, p = $(".p", el).value, c = $(".c", el).value, out = $(".out", el);
      let msg = "";
      if (!e) msg = "Email required"; else if (!e.includes("@")) msg = "Invalid email"; else if (p !== c) msg = "Passwords do not match";
      // BUG: password length is never checked
      out.className = "out" + (msg ? " bad" : ""); out.textContent = msg ? "✕ " + msg : "✓ ACCOUNT CREATED";
      Con.log(msg ? "VALIDATION FAILED" : "USER CREATED");
    };
  },
  state(el) {
    const T = { LOCKED: { unlock: "LOGIN", logout: "AUTHENTICATED" /* BUG */ }, LOGIN: { authenticate: "AUTHENTICATED", lock: "LOCKED" }, AUTHENTICATED: { logout: "LOCKED" } };
    let s = "LOCKED";
    el.innerHTML = `<h3>SESSION CONTROLLER</h3><div class="state-badge">STATE: <b class="st">LOCKED</b></div><div class="chips">${["unlock", "authenticate", "logout", "lock"].map((a) => `<button type="button" class="btn" data-a="${a}">${a.toUpperCase()}</button>`).join("")}</div><p class="out" aria-live="polite"></p>`;
    el.querySelectorAll("[data-a]").forEach((b) => (b.onclick = () => {
      const n = T[s][b.dataset.a];
      $(".out", el).className = "out" + (n ? "" : " bad");
      $(".out", el).textContent = n ? `${s} → ${n}` : `Invalid action in ${s}`;
      if (n) { s = n; $(".st", el).textContent = s; }
      Con.log(`STATE ${s}`);
    }));
  },
  json(el, d) {
    el.innerHTML = `<h3>EXPECTED</h3><pre class="json">${esc(JSON.stringify(d.expected, null, 2))}</pre><h3>ACTUAL</h3><pre class="json">${esc(JSON.stringify(d.actual, null, 2))}</pre>`;
  },
  counter(el) {
    let n = 0;
    el.innerHTML = `<h3>VISIT COUNTER</h3><div class="state-badge big-t"><span class="n">0</span></div><div class="row"><button class="btn add" type="button">+1</button><button class="btn ghost rst" type="button">RESET</button></div>`;
    $(".add", el).onclick = () => { n += n === 4 ? 2 : 1; $(".n", el).textContent = n; Con.log(`COUNT ${n}`); }; // BUG: 4 -> 6
    $(".rst", el).onclick = () => { n = 0; $(".n", el).textContent = n; };
  },
  checkout(el, d) {
    el.innerHTML = `<h3>CHECKOUT (unit price ${d.price})</h3><label>Quantity<input class="q" type="number" value="1"></label><label>Discount %<input class="d" type="number" value="0"></label><button class="btn go" type="button">PLACE ORDER</button><pre class="json out"></pre>`;
    $(".go", el).onclick = () => {
      const q = +$(".q", el).value, disc = +$(".d", el).value;
      const total = +(d.price * q * (1 - disc / 100)).toFixed(2); // BUG: no validation at all
      $(".out", el).textContent = JSON.stringify({ status: 200, qty: q, discount: disc, total }, null, 2);
      Con.log(`ORDER total=${total}`);
    };
  },
};

const Game = {
  s: { missions: [], cats: [], sevs: [], idx: 0, cat: null, sev: null, cur: null, remaining: 90, timer: null, state: null },

  async init() {
    const d = await API.missions();
    Object.assign(this.s, { missions: d.missions, cats: d.categories, sevs: d.severities });
    $("#defects").textContent = d.missions.length;
    this.buildChips("#cats", d.categories, "cat"); this.buildChips("#sevs", d.severities, "sev");
  },

  buildChips(sel, items, key) {
    const box = $(sel); box.innerHTML = "";
    items.forEach((it) => {
      const b = document.createElement("button");
      b.type = "button"; b.className = "chip"; b.textContent = it; b.setAttribute("aria-pressed", "false");
      b.onclick = () => { this.s[key] = it; box.querySelectorAll(".chip").forEach((c) => c.setAttribute("aria-pressed", String(c === b))); };
      box.appendChild(b);
    });
  },

  hud(st) {
    this.s.state = st;
    $("#hudXp").textContent = st.xp.toLocaleString(); $("#hudScore").textContent = st.score.toLocaleString();
    $("#hudCombo").textContent = "x" + st.combo; $("#hudRank").textContent = st.rank;
    $("#hudLives").innerHTML = Array.from({ length: 3 }, (_, i) => `<span class="${i < st.lives ? "" : "lost"}" aria-hidden="true">${i < st.lives ? "❤️" : "🖤"}</span>`).join("") + `<span class="sr" hidden>${st.lives} lives</span>`;
    $("#hudLives").setAttribute("aria-label", `${st.lives} lives left`);
    $("#hudBar").style.width = (100 * st.completed.length) / this.s.missions.length + "%";
  },

  async newGame() { this.hud(await API.reset()); this.s.idx = 0; await this.briefing(); },

  async briefing() {
    const id = this.s.missions[this.s.idx].id;
    const m = (this.s.cur = await API.mission(id));
    this.hud(await API.state());
    show("briefing");
    const n = String(id).padStart(2, "0");
    $("#beginBtn").hidden = true;
    await FX.typewrite($("#briefText"), `> MISSION ${n}\n> ${m.title}\n\n${m.briefing}\n\nYOUR TASK:\n  Find the defect.\n  Classify it.\n  Report it.`);
    $("#beginBtn").hidden = false; $("#beginBtn").focus();
  },

  async begin() {
    const m = this.s.cur;
    await API.start(m.id);
    Object.assign(this.s, { cat: null, sev: null, remaining: m.time_limit });
    $("#diag").value = ""; $("#msg").textContent = "";
    document.querySelectorAll(".chip").forEach((c) => c.setAttribute("aria-pressed", "false"));
    $("#hudMission").textContent = `MISSION ${String(m.id).padStart(2, "0")} / ${String(this.s.missions.length).padStart(2, "0")}`;
    $("#hudTitle").textContent = m.title; $("#mBrief").textContent = m.briefing;
    const art = $("#artifact"); art.innerHTML = ""; Widgets[m.widget](art, m.data);
    show("mission"); this.hud(await API.state()); this.tick(true);
    Con.log(`MISSION ${m.id} STARTED`);
  },

  tick(reset) {
    clearInterval(this.s.timer);
    const paint = () => { const t = $("#hudTime"); t.textContent = FX.fmtTime(this.s.remaining); t.classList.toggle("low", this.s.remaining <= 10); };
    paint();
    this.s.timer = setInterval(() => { if (this.s.remaining > 0) this.s.remaining--; paint(); }, 1000);
  },

  async submit() {
    const { cat, sev, cur } = this.s;
    if (!cat || !sev) { $("#msg").textContent = "Select a category AND a severity."; FX.shake($("#report")); return; }
    $("#submitBtn").disabled = true;
    try {
      const r = await API.submit(cur.id, { category: cat, severity: sev, diagnosis: $("#diag").value });
      clearInterval(this.s.timer); this.hud(r.state);
      if (r.solved) { Con.log("DEFECT DETECTED"); this.showResult(r); }
      else if (r.game_over) { show("fail"); $("#retryBtn").focus(); }
      else {
        const p = r.parts, ok = (b) => (b ? "OK" : "WRONG");
        $("#msg").textContent = `✕ Not quite (category ${ok(p.category)}, severity ${ok(p.severity)}, diagnosis ${ok(p.diagnosis)}). -1 life.`;
        FX.shake($("#report"));
      }
    } catch (e) { $("#msg").textContent = "✕ " + e.message; }
    $("#submitBtn").disabled = false;
  },

  showResult(r) {
    const b = r.breakdown, rows = [["CATEGORY", b.category], ["SEVERITY", b.severity], ["DIAGNOSIS", b.diagnosis], ["BASE", b.base], ["SPEED BONUS", b.speed], ["PERFECT MISSION", b.perfect]];
    $("#resultBody").innerHTML = `<h2 class="pop ok">✓ DEFECT CONFIRMED</h2><p>${esc(r.solution.explanation)}</p>
      <div class="line"><span>BUG CLASS</span><b>${esc(r.solution.category)}</b></div><div class="line"><span>SEVERITY</span><b>${esc(r.solution.severity)}</b></div>
      ${rows.map(([l], i) => `<div class="line ${rows[i][1] ? "" : "zero"}"><span>${l}</span><b class="v">0</b></div>`).join("")}
      <div class="line"><span>COMBO</span><b>x${r.multiplier}</b></div><p class="total pop">TOTAL +<span id="tot">0</span> XP-SCORE</p>`;
    rows.forEach(([, v], i) => setTimeout(() => FX.countUp(document.querySelectorAll("#resultBody .v")[i], v, 500, "+"), 250 * (i + 1)));
    setTimeout(() => FX.countUp($("#tot"), r.gained_score, 900), 250 * (rows.length + 1));
    const last = r.state.finished; $("#nextBtn").textContent = last ? "[ FINISH ]" : "[ NEXT MISSION ]";
    show("result"); $("#nextBtn").focus();
  },

  async next() {
    if (this.s.state.finished) return this.showFinal();
    const next = this.s.missions.findIndex((m) => !this.s.state.completed.includes(m.id));
    this.s.idx = next; await this.briefing();
  },

  async retry() { this.hud(await API.retry()); await this.begin(); },

  async showFinal() {
    const st = await API.state();
    $("#finalBody").innerHTML = `<h2 class="pop ok">QA OPERATIVE CERTIFIED</h2><p>ALL DEFECTS RESOLVED</p>
      <div class="line"><span>FINAL SCORE</span><b>${st.score.toLocaleString()}</b></div><div class="line"><span>XP</span><b>${st.xp.toLocaleString()}</b></div>
      <div class="line"><span>RANK</span><b>${st.rank}</b></div><div class="line"><span>MISSIONS</span><b>${st.completed.length} / ${st.total_missions}</b></div>
      <div class="line"><span>ACCURACY</span><b>${st.accuracy}%</b></div><div class="line"><span>TIME</span><b>${FX.fmtTime(st.time)}</b></div>`;
    $("#nameMsg").textContent = ""; show("final"); $("#pname").focus();
  },

  async saveName() {
    try { await API.saveScore($("#pname").value); $("#nameMsg").textContent = ""; await this.openBoard(); }
    catch (e) { $("#nameMsg").textContent = "✕ " + e.message; }
  },

  async openBoard() {
    const { entries } = await API.board();
    $("#boardBody").innerHTML = entries.length
      ? `<table><thead><tr><th>#</th><th>PLAYER</th><th>XP</th><th>ACC</th><th>TIME</th></tr></thead><tbody>${entries.map((e) => `<tr><td>${e.position}</td><td>${esc(e.name)}</td><td>${e.xp.toLocaleString()}</td><td>${e.accuracy}%</td><td>${FX.fmtTime(e.time_seconds)}</td></tr>`).join("")}</tbody></table>`
      : "<p class='dim'>No operatives yet. Be the first.</p>";
    $("#boardDlg").showModal();
  },
};
