const log = document.getElementById("log");
const form = document.getElementById("input-row");
const input = document.getElementById("input");
const roomName = document.getElementById("room-name");

let currentRoomName = "";

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// Each kind gets its own glyph, not just a color, so the cue still reads
// without relying on color perception.
const HIGHLIGHT_GLYPH = { take: "+", combine: "»", evidence: "★" };

function appendLine(roomLabel, text, { className, highlight } = {}) {
  const p = document.createElement("p");
  if (className) p.className = className;
  p.innerHTML =
    `<span class="room-tag">${escapeHtml(roomLabel)}</span>` +
    `<span class="sep"> | </span>` +
    `<span class="log-text">${escapeHtml(text)}</span>`;
  log.appendChild(p);

  if (highlight) {
    const badge = document.createElement("p");
    badge.className = `event-badge kind-${highlight.kind}`;
    const glyph = HIGHLIGHT_GLYPH[highlight.kind] || "+";
    const label = highlight.kind === "evidence" ? "Evidence: " : "";
    badge.textContent = `${glyph} ${label}${highlight.text}`;
    log.appendChild(badge);
  }

  log.scrollTop = log.scrollHeight;
}

function renderState(state) {
  currentRoomName = state.room.name;
  roomName.textContent = state.room.name;
}

async function loadState() {
  const res = await fetch("/api/game/state");
  const state = await res.json();
  renderState(state);
  appendLine(currentRoomName, state.room.description);
}

async function sendAction(text) {
  appendLine(currentRoomName, `> ${text}`, { className: "command" });
  const res = await fetch("/api/game/action", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ input: text }),
  });
  const state = await res.json();
  renderState(state);
  appendLine(currentRoomName, state.message, { highlight: state.highlight });
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  sendAction(text);
});

loadState();
