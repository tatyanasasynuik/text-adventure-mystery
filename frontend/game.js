const log = document.getElementById("log");
const form = document.getElementById("input-row");
const input = document.getElementById("input");
const roomName = document.getElementById("room-name");
const notebook = document.getElementById("notebook");
const notebookToggle = document.getElementById("notebook-toggle");
const notebookVisited = document.getElementById("notebook-visited");
const notebookInventory = document.getElementById("notebook-inventory");

function appendLine(text) {
  const p = document.createElement("p");
  p.textContent = text;
  log.appendChild(p);
  log.scrollTop = log.scrollHeight;
}

function renderList(el, items, emptyText) {
  el.innerHTML = "";
  if (items.length === 0) {
    const li = document.createElement("li");
    li.textContent = emptyText;
    li.className = "empty";
    el.appendChild(li);
    return;
  }
  for (const item of items) {
    const li = document.createElement("li");
    li.textContent = item;
    el.appendChild(li);
  }
}

function renderState(state) {
  roomName.textContent = state.room.name;
  renderList(notebookVisited, state.notebook.visited, "Nowhere yet.");
  renderList(notebookInventory, state.notebook.inventory, "Nothing yet.");
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
  // flash a small 8-bit-style sprite/animation here as a "check your notebook"
  // hint — probably keyed off a flag the action response adds (e.g.
  // state.item_acquired) rather than parsing the message text.
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  appendLine(`> ${text}`);
  input.value = "";
  sendAction(text);
});

notebookToggle.addEventListener("click", () => {
  notebook.hidden = !notebook.hidden;
});

loadState();
