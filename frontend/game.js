const log = document.getElementById("log");
const form = document.getElementById("input-row");
const input = document.getElementById("input");

function appendLine(text) {
  const p = document.createElement("p");
  p.textContent = text;
  log.appendChild(p);
  log.scrollTop = log.scrollHeight;
}

async function loadGreeting() {
  const res = await fetch("/api/hello");
  const data = await res.json();
  appendLine(data.message);
}

// Placeholder: echoes input until /api/game/action exists.
form.addEventListener("submit", (event) => {
  event.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  appendLine(`> ${text}`);
  input.value = "";
});

loadGreeting();
