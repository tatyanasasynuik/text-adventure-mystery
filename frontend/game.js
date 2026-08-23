const log = document.getElementById("log");
const form = document.getElementById("input-row");
const input = document.getElementById("input");
const roomName = document.getElementById("room-name");

function appendLine(text, className) {
  const p = document.createElement("p");
  p.textContent = text;
  if (className) p.className = className;
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
  // TODO: once item pickup exists (plans/SAVE_LOAD_PLAN.md save_inventory),
  // flash a small 8-bit-style sprite/animation here as a "check your items"
  // hint — probably keyed off a flag the action response adds (e.g.
  // state.item_acquired) rather than parsing the message text.
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  appendLine(`> ${text}`, "command");
  input.value = "";
  sendAction(text);
});

loadState();
