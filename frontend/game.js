const log = document.getElementById("log");
const form = document.getElementById("input-row");
const input = document.getElementById("input");
const roomName = document.getElementById("room-name");

function appendLine(text) {
  const p = document.createElement("p");
  p.textContent = text;
  log.appendChild(p);
  log.scrollTop = log.scrollHeight;
}

function renderState(state) {
  roomName.textContent = state.room.name;
}

async function loadState() {
  const res = await fetch("/api/game/state");
  const state = await res.json();
  renderState(state);
  appendLine(state.room.description);
}

async function sendAction(text) {
  const res = await fetch("/api/game/action", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ input: text }),
  });
  const state = await res.json();
  renderState(state);
  appendLine(state.message);
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  appendLine(`> ${text}`);
  input.value = "";
  sendAction(text);
});

loadState();
