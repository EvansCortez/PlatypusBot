from __future__ import annotations

from flask import Flask, jsonify, render_template_string, request

from platypusbot.core.chatbot import Chatbot


HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>PlatypusBot</title>
  <style>
    :root {
      --bg: #08111d;
      --panel: rgba(15, 34, 56, 0.92);
      --panel-soft: #102840;
      --text: #f7fbff;
      --muted: #9db5cf;
      --accent: #57c7ff;
      --accent-2: #8ef6d1;
      --user: #1d8fe1;
      --assistant: #edf5ff;
      --assistant-text: #17324d;
      --border: rgba(255,255,255,0.08);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Segoe UI", sans-serif;
      color: var(--text);
      background:
        radial-gradient(circle at top left, rgba(87, 199, 255, 0.18), transparent 28%),
        radial-gradient(circle at top right, rgba(142, 246, 209, 0.16), transparent 20%),
        linear-gradient(160deg, #050b13, #08111d 55%, #0e1d30);
      min-height: 100vh;
    }
    .shell {
      display: grid;
      grid-template-columns: 300px 1fr;
      min-height: 100vh;
    }
    .sidebar {
      border-right: 1px solid var(--border);
      background: rgba(8, 17, 29, 0.7);
      backdrop-filter: blur(14px);
      padding: 24px;
    }
    .hero {
      border-radius: 24px;
      padding: 22px;
      background: linear-gradient(145deg, rgba(29,143,225,0.26), rgba(87,199,255,0.08));
      margin-bottom: 20px;
    }
    .hero h1 {
      margin: 0 0 8px;
      font: 700 2rem Georgia, serif;
    }
    .hero p, .sidebar p, .memory-item p {
      margin: 0;
      color: var(--muted);
      line-height: 1.5;
    }
    .label {
      margin: 22px 0 10px;
      color: var(--accent);
      font-size: 0.83rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      font-weight: 700;
    }
    .quick, .memory-item {
      width: 100%;
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 12px 14px;
      margin-bottom: 10px;
      text-align: left;
      color: var(--text);
      background: rgba(255,255,255,0.03);
      cursor: pointer;
    }
    .quick:hover { border-color: rgba(87,199,255,0.45); }
    .memory-item strong {
      display: block;
      margin-bottom: 6px;
      font-size: 0.95rem;
    }
    .main {
      padding: 24px;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }
    .topbar, .composer {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 24px;
      padding: 18px;
      backdrop-filter: blur(14px);
    }
    .topbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }
    .badges {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }
    .badge {
      padding: 8px 12px;
      border-radius: 999px;
      font-size: 0.9rem;
      font-weight: 700;
    }
    .badge.route { background: rgba(142, 246, 209, 0.16); color: #aaf8dd; }
    .badge.lang { background: rgba(224, 195, 252, 0.18); color: #f2deff; }
    .badge.model { background: rgba(87, 199, 255, 0.15); color: #d7f3ff; }
    .chat {
      flex: 1;
      overflow-y: auto;
      padding: 8px 6px 8px 0;
    }
    .message {
      max-width: min(78%, 780px);
      margin-bottom: 16px;
      padding: 4px 0;
    }
    .message.user { margin-left: auto; }
    .meta {
      color: var(--muted);
      font-size: 0.82rem;
      margin: 0 8px 6px;
    }
    .bubble {
      border-radius: 24px;
      padding: 16px 18px;
      line-height: 1.55;
      white-space: pre-wrap;
      box-shadow: 0 8px 24px rgba(0,0,0,0.12);
    }
    .user .bubble {
      background: linear-gradient(145deg, #1d8fe1, #49c6e5);
      color: white;
    }
    .assistant .bubble {
      background: var(--assistant);
      color: var(--assistant-text);
    }
    .composer textarea {
      width: 100%;
      min-height: 90px;
      resize: vertical;
      border: 0;
      outline: none;
      border-radius: 18px;
      padding: 16px;
      font: inherit;
      background: rgba(255,255,255,0.96);
      color: #17324d;
    }
    .composer-row {
      margin-top: 12px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }
    .status {
      color: var(--muted);
      font-size: 0.92rem;
    }
    .actions {
      display: flex;
      gap: 10px;
    }
    button.send, button.clear {
      border: 0;
      border-radius: 999px;
      padding: 12px 18px;
      font-weight: 700;
      cursor: pointer;
    }
    button.send { background: linear-gradient(145deg, #1d8fe1, #57c7ff); color: white; }
    button.clear { background: rgba(255,255,255,0.08); color: var(--text); }
    @media (max-width: 980px) {
      .shell { grid-template-columns: 1fr; }
      .sidebar { border-right: 0; border-bottom: 1px solid var(--border); }
      .message { max-width: 92%; }
    }
  </style>
</head>
<body>
  <div class="shell">
    <aside class="sidebar">
      <div class="hero">
        <h1>PlatypusBot</h1>
        <p>Redesigned for live data, multilingual chat, and an optional LLM layer.</p>
      </div>
      <p>Use the browser chatbox for a more current experience with live status, recent memory, and quick prompts.</p>
      <div class="label">Quick actions</div>
      <button class="quick" onclick="useQuick('latest news about AI')">latest news about AI</button>
      <button class="quick" onclick="useQuick('translate hello to Spanish')">translate hello to Spanish</button>
      <button class="quick" onclick="useQuick('what time is it in Tokyo')">what time is it in Tokyo</button>
      <button class="quick" onclick="useQuick('Explain machine learning in French')">Explain machine learning in French</button>
      <div class="label">Recent memory</div>
      <div id="memory"></div>
    </aside>
    <main class="main">
      <section class="topbar">
        <div>
          <div style="font:700 1.45rem Georgia, serif;">Modern chatbox</div>
          <div class="status" id="status">Ready for live, multilingual, and LLM-backed prompts</div>
        </div>
        <div class="badges">
          <span class="badge route" id="routeBadge">Route: general</span>
          <span class="badge lang" id="langBadge">Language: english</span>
          <span class="badge model" id="modelBadge">Model: gpt-5-mini</span>
        </div>
      </section>
      <section class="chat" id="chat"></section>
      <section class="composer">
        <textarea id="prompt" placeholder="Ask anything. Try a live question, a translation, or an open-ended prompt."></textarea>
        <div class="composer-row">
          <div class="status">The UI streams replies chunk by chunk so the redesign feels closer to a current chat app.</div>
          <div class="actions">
            <button class="clear" onclick="resetChat()">New chat</button>
            <button class="send" onclick="sendMessage()">Send</button>
          </div>
        </div>
      </section>
    </main>
  </div>

  <script>
    const chat = document.getElementById("chat");
    const promptInput = document.getElementById("prompt");
    const statusNode = document.getElementById("status");
    const memoryNode = document.getElementById("memory");

    function appendMessage(role, speaker, text) {
      const wrapper = document.createElement("div");
      wrapper.className = `message ${role}`;
      const time = new Date().toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
      wrapper.innerHTML = `
        <div class="meta">${speaker} • ${time}</div>
        <div class="bubble"></div>
      `;
      wrapper.querySelector(".bubble").textContent = text;
      chat.appendChild(wrapper);
      chat.scrollTop = chat.scrollHeight;
      return wrapper.querySelector(".bubble");
    }

    function streamInto(node, chunks, index = 0) {
      if (index >= chunks.length) return;
      node.textContent += chunks[index];
      chat.scrollTop = chat.scrollHeight;
      setTimeout(() => streamInto(node, chunks, index + 1), 28);
    }

    function useQuick(text) {
      promptInput.value = text;
      promptInput.focus();
    }

    async function refreshMemory() {
      const response = await fetch("/api/history");
      const data = await response.json();
      memoryNode.innerHTML = "";
      if (!data.history.length) {
        memoryNode.innerHTML = '<div class="memory-item"><p>No saved conversations yet.</p></div>';
        return;
      }
      data.history.forEach(item => {
        const card = document.createElement("div");
        card.className = "memory-item";
        card.innerHTML = `<strong>You: ${item.user_input.slice(0, 44)}</strong><p>Bot: ${item.response.slice(0, 80)}</p>`;
        memoryNode.appendChild(card);
      });
    }

    function updateBadges(status) {
      document.getElementById("routeBadge").textContent = `Route: ${status.route}`;
      document.getElementById("langBadge").textContent = `Language: ${status.language}`;
      document.getElementById("modelBadge").textContent = `Model: ${status.model}`;
    }

    async function sendMessage() {
      const text = promptInput.value.trim();
      if (!text) return;
      appendMessage("user", "You", text);
      promptInput.value = "";
      statusNode.textContent = "PlatypusBot is thinking across live tools and the LLM layer...";

      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text })
      });
      const data = await response.json();
      const bubble = appendMessage("assistant", "PlatypusBot", "");
      streamInto(bubble, data.chunks);
      updateBadges(data.status);
      statusNode.textContent = "Ready for live, multilingual, and LLM-backed prompts";
      refreshMemory();
    }

    async function resetChat() {
      chat.innerHTML = "";
      appendMessage("assistant", "PlatypusBot", "Fresh chat started. Ask for weather, headlines, translation, multilingual help, or anything else in the toolkit.");
      await refreshMemory();
    }

    promptInput.addEventListener("keydown", (event) => {
      if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
        sendMessage();
      }
    });

    resetChat();
  </script>
</body>
</html>
"""


def create_app() -> Flask:
    app = Flask(__name__)
    bot = Chatbot()
    bot.set_preference("interface", "web")

    @app.get("/")
    def index() -> str:
        return render_template_string(HTML)

    @app.get("/api/history")
    def history() -> tuple[str, int] | object:
        rows = bot.database.get_history(limit=6)
        return jsonify(
            {
                "history": [
                    {"user_input": user_input, "response": response, "timestamp": timestamp}
                    for user_input, response, timestamp in rows
                ]
            }
        )

    @app.post("/api/chat")
    def chat() -> object:
        payload = request.get_json(silent=True) or {}
        message = str(payload.get("message", "")).strip()
        response = bot.handle_message(message)
        bot.set_preference("interface", "web")
        return jsonify(
            {
                "response": response,
                "chunks": bot.stream_response(response),
                "status": bot.get_ui_status(),
            }
        )

    return app


def run_web(host: str = "127.0.0.1", port: int = 5000) -> None:
    app = create_app()
    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    run_web()
