document.addEventListener("DOMContentLoaded", async () => {
  FX.particles($("#fx"));
  try {
    await API.health(); $("#status").textContent = "ONLINE";
    await Game.init();
    const { entries } = await API.board();
    if (entries[0]) $("#best").innerHTML = `BEST OPERATIVE<br>${esc(entries[0].name)} — ${entries[0].xp.toLocaleString()} XP`;
  } catch (e) { $("#status").textContent = "OFFLINE"; $("#status").className = "warn"; $("#startBtn").disabled = true; }

  $("#startBtn").onclick = () => Game.newGame();
  $("#beginBtn").onclick = () => Game.begin();
  $("#report").onsubmit = (e) => { e.preventDefault(); Game.submit(); };
  $("#nextBtn").onclick = () => Game.next();
  $("#retryBtn").onclick = () => Game.retry();
  $("#againBtn").onclick = () => Game.newGame();
  $("#nameForm").onsubmit = (e) => { e.preventDefault(); Game.saveName(); };
  $("#boardBtn").onclick = () => Game.openBoard();
  $("#boardClose").onclick = () => $("#boardDlg").close();
  $("#conBtn").onclick = () => { const c = $("#con"); c.hidden = !c.hidden; $("#conBtn").setAttribute("aria-expanded", String(!c.hidden)); };
});
