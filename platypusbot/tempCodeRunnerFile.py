from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory, flash, jsonify
from werkzeug.utils import secure_filename
import os
from core.chatbot import Chatbot
from config import Config

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif"}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "platypus_secret"

bot = Chatbot()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>PlatypusBot</title>
  <style>
    body {
      margin: 0; padding: 0;
      font-family: 'Segoe UI', Arial, sans-serif;
      background: #f7f7f8;
      color: #23232f;
      height: 100vh;
      display: flex;
    }
    .sidebar {
      width: 270px;
      background: #fff;
      color: #23232f;
      display: flex;
      flex-direction: column;
      height: 100vh;
      box-sizing: border-box;
      border-right: 1px solid #ececf1;
    }
    .platypus-mascot {
      display: flex;
      flex-direction: column;
      align-items: center;
      margin-bottom: 24px;
      margin-top: 10px;
    }
    .platypus-mascot svg {
      width: 70px;
      height: 70px;
      margin-bottom: 8px;
    }
    .platypus-mascot span {
      color: #23232f;
      font-size: 1.1em;
      font-weight: 600;
      letter-spacing: 1px;
    }
    .color-picker {
      display: flex;
      align-items: center;
      gap: 8px;
      margin: 10px 20px 10px 20px;
    }
    .color-picker label {
      font-size: 0.98em;
      color: #23232f;
    }
    .color-picker input[type=color] {
      border: none;
      width: 28px;
      height: 28px;
      border-radius: 50%;
      cursor: pointer;
      background: none;
      padding: 0;
    }
    .sidebar .new-chat {
      margin: 20px 20px 10px 20px;
      padding: 12px 0;
      background: #e6eaf0;
      color: #23232f;
      border: none;
      border-radius: 8px;
      font-size: 1em;
      font-weight: 600;
      cursor: pointer;
      text-align: left;
      padding-left: 18px;
      transition: background 0.2s;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .sidebar .new-chat:hover {
      background: #10a37f;
      color: #fff;
    }
    .sidebar .new-chat input[type=text] {
      width: 120px;
      border: none;
      border-radius: 6px;
      padding: 4px 8px;
      font-size: 1em;
      margin-left: 8px;
      background: #ececf1;
      color: #23232f;
    }
    .sidebar .convos {
      flex: 1;
      margin: 0 20px;
      overflow-y: auto;
      margin-bottom: 20px;
    }
    .sidebar .convo {
      padding: 10px 0 10px 10px;
      border-radius: 6px;
      margin-bottom: 4px;
      color: #23232f;
      font-size: 1em;
      cursor: pointer;
      transition: background 0.2s;
    }
    .sidebar .convo.selected {
      background: #10a37f;
      color: #fff;
    }
    .sidebar .convo:hover {
      background: #ececf1;
    }
    .sidebar .bottom {
      margin: 0 20px 20px 20px;
      font-size: 0.95em;
      color: #aaa;
      border-top: 1px solid #ececf1;
      padding-top: 16px;
    }
    .sidebar .bottom a {
      cursor: pointer;
      color: #23232f;
      text-decoration: none;
    }
    .sidebar .bottom .dark-toggle {
      cursor: pointer;
      color: #23232f;
      background: none;
      border: none;
      font-size: 1em;
      padding: 0;
      margin: 0;
    }
    .main {
      flex: 1;
      display: flex;
      flex-direction: column;
      height: 100vh;
      background: #f7f7f8;
      align-items: center;
      justify-content: center;
    }
    .center-content {
      width: 100%;
      max-width: 900px;
      margin: auto;
      text-align: center;
      margin-top: 60px;
    }
    .center-content h1 {
      font-size: 2.5em;
      font-weight: 700;
      margin-bottom: 30px;
      color: #23232f;
      letter-spacing: 1px;
    }
    .features {
      display: flex;
      justify-content: center;
      gap: 30px;
      margin-bottom: 40px;
    }
    .feature-col {
      flex: 1;
      min-width: 220px;
    }
    .feature-col h3 {
      font-size: 1.1em;
      font-weight: 600;
      margin-bottom: 18px;
      color: #23232f;
      letter-spacing: 1px;
    }
    .feature-col .feature-box {
      background: #ececf1;
      color: #23232f;
      border-radius: 8px;
      padding: 14px 12px;
      margin-bottom: 12px;
      font-size: 1em;
      text-align: left;
      box-shadow: 0 1px 2px #0001;
    }
    .chat-area {
      width: 100%;
      max-width: 900px;
      margin: 0 auto;
      flex: 1;
      overflow-y: auto;
      padding: 30px 0 90px 0;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .bubble {
      max-width: 60%;
      padding: 14px 18px;
      border-radius: 16px;
      margin: 0 30px;
      font-size: 1.1em;
      line-height: 1.5;
      word-break: break-word;
      box-sizing: border-box;
      display: inline-block;
      background: #fff;
      color: #23232f;
      box-shadow: 0 1px 4px #0001;
    }
    .user {
      align-self: flex-end;
      background: #10a37f;
      color: #fff;
      border-bottom-right-radius: 4px;
    }
    .bot {
      align-self: flex-start;
      background: #ececf1;
      color: #23232f;
      border-bottom-left-radius: 4px;
    }
    .input-bar {
      position: fixed;
      bottom: 0; left: 270px; right: 0;
      background: #fff;
      padding: 18px 30px;
      display: flex;
      gap: 10px;
      box-sizing: border-box;
      box-shadow: 0 -2px 8px #0001;
    }
    .input-bar input[type=text] {
      flex: 1;
      font-size: 1.1em;
      padding: 12px 16px;
      border-radius: 8px;
      border: 1px solid #ececf1;
      outline: none;
      background: #f7f7f8;
      color: #23232f;
    }
    .input-bar button {
      background: #10a37f;
      color: #fff;
      border: none;
      border-radius: 8px;
      font-size: 1.1em;
      padding: 12px 24px;
      cursor: pointer;
      transition: background 0.2s;
    }
    .input-bar button:hover {
      background: #13c08a;
    }
    .speaker-btn {
      background: #ececf1;
      color: #23232f;
      border: none;
      border-radius: 50%;
      width: 36px;
      height: 36px;
      font-size: 1.2em;
      cursor: pointer;
      margin-left: 8px;
      vertical-align: middle;
      transition: background 0.2s;
      box-shadow: 0 1px 2px #0001;
    }
    .speaker-btn:hover {
      background: #10a37f;
      color: #fff;
    }
    .upload-form {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-top: 10px;
      margin-bottom: 10px;
      margin-left: 30px;
    }
    .upload-form input[type=file] {
      color: #23232f;
      background: #f7f7f8;
      border: none;
    }
    .upload-form button {
      background: #10a37f;
      color: #fff;
      border: none;
      border-radius: 8px;
      font-size: 1em;
      padding: 6px 16px;
      cursor: pointer;
      transition: background 0.2s;
    }
    .upload-form button:hover {
      background: #13c08a;
    }
    .uploaded-files {
      margin-left: 30px;
      margin-bottom: 10px;
      color: #23232f;
      font-size: 0.98em;
    }
    .voice-record-btn {
      background: #10a37f;
      color: #fff;
      border: none;
      border-radius: 50%;
      width: 40px;
      height: 40px;
      font-size: 1.3em;
      cursor: pointer;
      margin-left: 10px;
      transition: background 0.2s;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .voice-record-btn.recording {
      background: #e74c3c;
      color: #fff;
      animation: pulse 1s infinite;
    }
    @keyframes pulse {
      0% { box-shadow: 0 0 0 0 #e74c3c44; }
      70% { box-shadow: 0 0 0 10px #e74c3c11; }
      100% { box-shadow: 0 0 0 0 #e74c3c44; }
    }
    @media (max-width: 900px) {
      .center-content, .chat-area { max-width: 98vw; }
      .input-bar { left: 0; }
      .sidebar { display: none; }
    }
  </style>
</head>
<body>
  <div class="sidebar">
    <div class="platypus-mascot">
      <svg viewBox="0 0 64 64" fill="none">
        <ellipse cx="32" cy="32" rx="24" ry="18" fill="#8d6748"/>
        <ellipse cx="32" cy="44" rx="14" ry="6" fill="#bfa16a"/>
        <ellipse cx="22" cy="30" rx="4" ry="6" fill="#bfa16a"/>
        <ellipse cx="42" cy="30" rx="4" ry="6" fill="#bfa16a"/>
        <ellipse cx="32" cy="38" rx="10" ry="7" fill="#e2c391"/>
        <ellipse cx="26" cy="32" rx="2" ry="2.5" fill="#23232f"/>
        <ellipse cx="38" cy="32" rx="2" ry="2.5" fill="#23232f"/>
        <ellipse cx="32" cy="46" rx="4" ry="2" fill="#23232f"/>
        <ellipse cx="18" cy="48" rx="3" ry="1.5" fill="#bfa16a"/>
        <ellipse cx="46" cy="48" rx="3" ry="1.5" fill="#bfa16a"/>
      </svg>
      <span>PlatypusBot</span>
    </div>
    <div class="color-picker">
      <label for="userColor">User:</label>
      <input type="color" id="userColor" value="#10a37f" onchange="setUserColor(this.value)">
      <label for="botColor">Bot:</label>
      <input type="color" id="botColor" value="#ececf1" onchange="setBotColor(this.value)">
    </div>
    <form class="upload-form" method="post" enctype="multipart/form-data" action="/upload">
      <input type="file" name="file">
      <button type="submit">Upload</button>
    </form>
    {% if files %}
      <div class="uploaded-files">
        <b>Uploaded files:</b>
        <ul>
        {% for f in files %}
          <li><a href="{{ url_for('uploaded_file', filename=f) }}" style="color:#10a37f;">{{ f }}</a></li>
        {% endfor %}
        </ul>
      </div>
    {% endif %}
    <form class="new-chat" method="post" action="/newchat">
      <span>+ New chat</span>
      <input type="text" name="chat_title" placeholder="Chat title" maxlength="40">
      <button type="submit" style="display:none"></button>
    </form>
    <div class="convos">
      {% for convo in convos %}
        <div class="convo{% if convo == active_convo %} selected{% endif %}">{{ convo }}</div>
      {% endfor %}
    </div>
    <div class="bottom">
      <div style="margin-bottom:10px;"><a onclick="clearChat()">Clear conversations</a></div>
      <div style="margin-bottom:10px;"><button class="dark-toggle" onclick="toggleDarkMode()">Dark mode</button></div>
      <div style="margin-bottom:10px;"><a href="https://nltk.org/" target="_blank">NLTK</a></div>
      <div style="margin-bottom:10px;"><a href="https://github.com/" target="_blank">GitHub</a></div>
      <div style="margin-bottom:10px;">Log out</div>
    </div>
  </div>
  <div class="main">
    {% if not chat %}
      <div class="center-content">
        <h1>Chatbot</h1>
        <div class="features">
          <div class="feature-col">
            <h3>Examples</h3>
            <div class="feature-box">"Explain quantum computing in simple terms" →</div>
            <div class="feature-box">"Got any creative ideas for a 10 year old's birthday?" →</div>
            <div class="feature-box">"How do I make an HTTP request in Python?" →</div>
          </div>
          <div class="feature-col">
            <h3>Capabilities</h3>
            <div class="feature-box">Remembers what user said earlier in the conversation</div>
            <div class="feature-box">Allows user to provide follow-up corrections</div>
            <div class="feature-box">Trained to decline inappropriate requests</div>
          </div>
          <div class="feature-col">
            <h3>Limitations</h3>
            <div class="feature-box">May occasionally generate incorrect information</div>
            <div class="feature-box">May occasionally produce harmful instructions or biased content</div>
            <div class="feature-box">Limited knowledge of world and events after 2021</div>
          </div>
        </div>
      </div>
    {% else %}
      <div class="chat-area" id="chat-area">
        {% for sender, msg in chat %}
          <div class="bubble {{sender}}">
            {{msg}}
            {% if sender == 'bot' %}
              <button class="speaker-btn" onclick="speakText(this.previousSibling.textContent)">🔊</button>
            {% endif %}
          </div>
        {% endfor %}
      </div>
    {% endif %}
    <form class="input-bar" method="post" autocomplete="off" id="chat-form">
      <input type="text" name="user_input" id="user_input" placeholder="Type your message..." autofocus autocomplete="off">
      <button type="submit">Send</button>
      <button type="button" class="voice-record-btn" id="voiceBtn" title="Record your voice">🎤</button>
    </form>
  </div>
  <script>
    function clearChat() {
      fetch('/clear', {method: 'POST'})
        .then(() => { window.location.reload(); });
    }
    function toggleDarkMode() {
      document.body.classList.toggle('dark');
    }
    // Color theme logic
    function setUserColor(color) {
      document.documentElement.style.setProperty('--user-color', color);
      let userBubbles = document.querySelectorAll('.bubble.user');
      userBubbles.forEach(b => b.style.background = color);
    }
    function setBotColor(color) {
      document.documentElement.style.setProperty('--bot-color', color);
      let botBubbles = document.querySelectorAll('.bubble.bot');
      botBubbles.forEach(b => b.style.background = color);
    }
    // Speaker button (browser TTS)
    function speakText(text) {
      if ('speechSynthesis' in window) {
        var utter = new SpeechSynthesisUtterance(text);
        utter.lang = 'en-US';
        window.speechSynthesis.speak(utter);
      }
    }
    // Voice recording and speech recognition (Web Speech API)
    const voiceBtn = document.getElementById('voiceBtn');
    const userInput = document.getElementById('user_input');
    let recognizing = false;
    let recognition;
    if ('webkitSpeechRecognition' in window) {
      recognition = new webkitSpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-US';

      recognition.onstart = function() {
        recognizing = true;
        voiceBtn.classList.add('recording');
      };
      recognition.onend = function() {
        recognizing = false;
        voiceBtn.classList.remove('recording');
      };
      recognition.onresult = function(event) {
        if (event.results.length > 0) {
          userInput.value = event.results[0][0].transcript;
        }
      };

      voiceBtn.onclick = function() {
        if (recognizing) {
          recognition.stop();
        } else {
          recognition.start();
        }
      };
    } else {
      voiceBtn.disabled = true;
      voiceBtn.title = "Speech recognition not supported in this browser";
    }
    // Auto-scroll to bottom
    var chatArea = document.getElementById('chat-area');
    if (chatArea) chatArea.scrollTop = chatArea.scrollHeight;
  </script>
</body>
</html>
"""

chat_history = []
convos = ["Content strategy intern tasks.", "Chatbot that uses NLP", "Biases in Machine Learning."]
active_convo = convos[0]
convo_histories = {convo: [] for convo in convos}

def get_uploaded_files():
    try:
        return [f for f in os.listdir(UPLOAD_FOLDER) if os.path.isfile(os.path.join(UPLOAD_FOLDER, f))]
    except Exception:
        return []

@app.route("/", methods=["GET", "POST"])
def chat():
    global active_convo
    files = get_uploaded_files()
    if request.method == "POST":
        user_input = request.form.get("user_input")
        if user_input:
            convo_histories.setdefault(active_convo, [])
            convo_histories[active_convo].append(("user", user_input))
            if user_input.lower() == "exit":
                convo_histories[active_convo].append(("bot", "Goodbye!"))
            else:
                response = bot.generate_response(user_input)
                convo_histories[active_convo].append(("bot", response))
                bot.save_chat_history(user_input, response)
    chat = convo_histories.get(active_convo, [])
    return render_template_string(
        HTML,
        chat=chat[-40:],
        files=files,
        convos=convos,
        active_convo=active_convo
    )

@app.route("/clear", methods=["POST"])
def clear():
    convo_histories[active_convo] = []
    return ("", 204)

@app.route("/upload", methods=["POST"])
def upload():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('chat'))
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('chat'))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('File uploaded successfully')
    else:
        flash('Invalid file type')
    return redirect(url_for('chat'))

@app.route("/newchat", methods=["POST"])
def newchat():
    global active_convo
    title = request.form.get("chat_title", "").strip()
    if title and title not in convos:
        convos.append(title)
        convo_histories[title] = []
    active_convo = title if title else convos[0]
    return redirect(url_for('chat'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/api/message", methods=["POST"])
def api_message():
    """
    REST API endpoint for mobile apps to send a message and get a response.
    Expects JSON: { "message": "..." }
    Returns JSON: { "response": "..." }
    """
    data = request.get_json()
    user_input = data.get("message", "")
    if not user_input:
        return jsonify({"error": "No message provided"}), 400
    response = bot.generate_response(user_input)
    # Optionally save to history if you want mobile and web to share history
    bot.save_chat_history(user_input, response)
    return jsonify({"response": response})

if __name__ == "__main__":
    print("PlatypusBot is running as a desktop app.")
    try:
        from flaskwebgui import FlaskUI
        FlaskUI(app=app, server="flask", width=1200, height=900).run()
    except ImportError:
        print("flaskwebgui is not installed. Please install it with 'pip install flaskwebgui'.")
        app.run(debug=True, port=5050, host="127.0.0.1")

# Mobile App Integration:
# - Your mobile app (Flutter, React Native, etc.) can POST to http://<your-ip>:5050/api/message
#   with JSON: { "message": "Hello" }
# - The response will be JSON: { "response": "Hi there!" }
# - Make sure your Flask server is accessible from your mobile device (use your local IP, not 127.0.0.1).
# - The response will be JSON: { "response": "Hi there!" }
# - Make sure your Flask server is accessible from your mobile device (use your local IP, not 127.0.0.1).

