"use strict";
const $ = (id) => document.getElementById(id);
let busy = false;
let revision = -1;
let latest = null;
async function send(action, payload = {}) {
  if (busy) return;
  try {
    const response = await fetch("/api/actions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action, payload }),
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error);
    busy = true;
    updateButtons();
    $("status").textContent = "Working…";
  } catch (error) {
    $("status").textContent = error.message;
  }
}
function updateButtons() {
  document.querySelectorAll("button[data-action]").forEach((button) => {
    button.disabled = busy;
  });
}
async function poll() {
  try {
    const response = await fetch("/api/state");
    if (!response.ok)
      throw new Error(
        "Could not reach the app. Open the address printed in its terminal.",
      );
    const state = await response.json();
    busy = state.busy;
    updateButtons();
    showInfo(state.application);
    if (revision !== state.revision) {
      revision = state.revision;
      if (state.error) $("status").textContent = state.error;
      else if (state.result) {
        latest = state.result;
        $("status").textContent =
          latest.error || (latest.kind === "error" ? latest.message : "Ready");
        render(latest);
      } else $("status").textContent = "Ready";
    }
    if (busy) $("status").textContent = "Working…";
  } catch (error) {
    $("status").textContent = error.message;
  } finally {
    setTimeout(poll, 750);
  }
}
function showInfo(app) {
  $("connection").textContent = app.configured
    ? "Gemini configured"
    : "Add your Gemini key to .env";
}
function entry(who, text) {
  const row = document.createElement("div");
  row.className = "entry";
  const title = document.createElement("b");
  title.textContent = who;
  row.append(title, document.createTextNode(text));
  $("output").append(row);
  row.scrollIntoView({ block: "nearest" });
}
function render(result) {
  if (result.kind === "transcript") {
    $("message").value = result.transcript;
    return;
  }
  entry("Atlas", result.message);
}
$("command").addEventListener("submit", (event) => {
  event.preventDefault();
  const text = $("message").value.trim();
  if (!text || busy) return;
  const allow_actions = $("allow").checked;
  $("allow").checked = false;
  entry("You", text);
  send("chat", { message: text, allow_actions });
});
$("listen").addEventListener("click", () => send("listen"));
poll();
