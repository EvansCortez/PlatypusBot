document.getElementById("sendButton").addEventListener("click", function(e) {
    e.preventDefault();
    sendMessage();
});
document.getElementById("chat-form").addEventListener("submit", function(e) {
    e.preventDefault();
    sendMessage();
});
document.getElementById("userInput").addEventListener("keypress", function(e){
    if (e.key === "Enter") {
        e.preventDefault();
        sendMessage();
    }
});

function formatTimestamp() {
    const now = new Date();
    return now.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
}

function appendMessage(sender, text, timestamp = null) {
    const msgDiv = document.createElement("div");
    msgDiv.className = "message " + sender;

    // Bubble
    const bubble = document.createElement("div");
    bubble.className = "bubble";
    // Timestamp
    const ts = document.createElement("span");
    ts.className = "timestamp";
    ts.textContent = timestamp || formatTimestamp();

    if (sender === "bot") {
        // Render markdown for bot
        bubble.innerHTML = renderMarkdown(text);
        // Add copy button for code blocks
        bubble.querySelectorAll('pre code').forEach(codeBlock => {
            const copyBtn = document.createElement('button');
            copyBtn.textContent = "Copy";
            copyBtn.className = "copy-btn";
            copyBtn.onclick = function() {
                navigator.clipboard.writeText(codeBlock.textContent);
                copyBtn.textContent = "Copied!";
                setTimeout(() => copyBtn.textContent = "Copy", 1200);
            };
            codeBlock.parentNode.style.position = "relative";
            codeBlock.parentNode.appendChild(copyBtn);
        });
    } else {
        bubble.textContent = text;
    }

    bubble.appendChild(ts);
    msgDiv.appendChild(bubble);
    document.getElementById("messageList").appendChild(msgDiv);
    // Auto-scroll to bottom
    document.getElementById("messageList").scrollTop = document.getElementById("messageList").scrollHeight;
}

function renderMarkdown(text) {
    // Minimal markdown rendering: code blocks, inline code, bold, italics, links
    let html = text
        .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/\*\*([^\*]+)\*\*/g, '<b>$1</b>')
        .replace(/\*([^\*]+)\*/g, '<i>$1</i>')
        .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
    return html.replace(/\n/g, "<br>");
}

function showTypingIndicator() {
    if (document.getElementById("typing-indicator")) return;
    const msgDiv = document.createElement("div");
    msgDiv.className = "message bot";
    msgDiv.id = "typing-indicator";
    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.innerHTML = '<span class="typing-dots"><span>.</span><span>.</span><span>.</span></span>';
    msgDiv.appendChild(bubble);
    document.getElementById("messageList").appendChild(msgDiv);
    document.getElementById("messageList").scrollTop = document.getElementById("messageList").scrollHeight;
}

function removeTypingIndicator() {
    const el = document.getElementById("typing-indicator");
    if (el) el.remove();
}

function sendMessage() {
    const input = document.getElementById("userInput");
    const message = input.value.trim();
    if (!message) return;

    appendMessage("user", message);

    showTypingIndicator();

    fetch("/api/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({message})
    })
    .then(res => res.json())
    .then(data => {
        removeTypingIndicator();
        appendMessage("bot", data.response || "Error");
    })
    .catch(err => {
        removeTypingIndicator();
        console.error(err);
    });

    input.value = "";
}

// Responsive: adjust chat height on resize
window.addEventListener("resize", function() {
    const chatContainer = document.querySelector(".chat-container");
    if (chatContainer) {
        chatContainer.style.height = window.innerHeight + "px";
    }
});

// No major changes needed if you use #messageList and .chat-history as in the HTML/CSS above.
