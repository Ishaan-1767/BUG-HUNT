const FX = {
  typewrite(el, text, speed = 18) {
    el.textContent = "";
    return new Promise((done) => {
      let i = 0;
      const tick = () => { el.textContent = text.slice(0, ++i) + (i < text.length ? "█" : ""); i < text.length ? setTimeout(tick, speed) : done(); };
      tick();
    });
  },
  countUp(el, to, ms = 700, prefix = "") {
    const t0 = performance.now();
    const step = (now) => {
      const p = Math.min(1, (now - t0) / ms);
      el.textContent = prefix + Math.round(to * p).toLocaleString();
      if (p < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  },
  shake(el) { el.classList.remove("shake"); void el.offsetWidth; el.classList.add("shake"); },
  fmtTime(s) { s = Math.max(0, Math.round(s)); return `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`; },
  particles(canvas) {
    const ctx = canvas.getContext("2d");
    let w, h;
    const resize = () => { w = canvas.width = innerWidth; h = canvas.height = innerHeight; };
    resize(); addEventListener("resize", resize);
    const dots = Array.from({ length: 50 }, () => ({ x: Math.random() * innerWidth, y: Math.random() * innerHeight, v: 0.2 + Math.random() * 0.5, c: Math.random() > 0.5 ? "0,240,255" : "168,85,255" }));
    (function loop() {
      ctx.clearRect(0, 0, w, h);
      for (const d of dots) { d.y -= d.v; if (d.y < 0) { d.y = h; d.x = Math.random() * w; } ctx.fillStyle = `rgba(${d.c},.55)`; ctx.fillRect(d.x, d.y, 2, 2); }
      requestAnimationFrame(loop);
    })();
  },
};
