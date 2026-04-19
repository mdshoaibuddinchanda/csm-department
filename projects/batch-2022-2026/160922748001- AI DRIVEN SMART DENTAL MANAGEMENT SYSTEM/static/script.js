async function sendMessage() {
    const input   = document.getElementById("message");
    const chatBox = document.getElementById("chat-box");
    const text    = input.value.trim();

    if (!text) return;

    // Show user message
    const userMsg = document.createElement("p");
    userMsg.className = "message user";
    userMsg.textContent = text;
    chatBox.appendChild(userMsg);
    chatBox.scrollTop = chatBox.scrollHeight;
    input.value = "";

    // Show typing indicator
    const typing = document.createElement("div");
    typing.className = "typing";
    typing.id = "typing-indicator";
    typing.innerHTML = `<span></span><span></span><span></span>`;
    chatBox.appendChild(typing);
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({ message: text }),
        });

        const data = await response.json();

        // Remove typing indicator
        const indicator = document.getElementById("typing-indicator");
        if (indicator) indicator.remove();

        // Render bot reply
        const botMsg = document.createElement("p");
        botMsg.className = "message bot";
        botMsg.innerHTML = formatBotMessage(data.reply);
        chatBox.appendChild(botMsg);
        chatBox.scrollTop = chatBox.scrollHeight;

    } catch (error) {
        const indicator = document.getElementById("typing-indicator");
        if (indicator) indicator.remove();

        const errMsg = document.createElement("p");
        errMsg.className = "message bot";
        errMsg.textContent = "❌ Error connecting to server";
        chatBox.appendChild(errMsg);
        console.error(error);
    }
}

/**
 * Safely formats a bot reply for HTML rendering.
 *
 * Steps — ORDER MATTERS:
 *  1. Split on \n to get individual lines
 *  2. Escape raw HTML characters per line
 *  3. Apply *bold* markdown within each line
 *  4. Join lines back with <br>
 */
function formatBotMessage(text) {
    return text
        .split('\n')
        .map(line => {
            // Step 1: escape HTML in this line
            let safe = line
                .replace(/&/g, '&amp;')
                .replace(/</g,  '&lt;')
                .replace(/>/g,  '&gt;')
                .replace(/"/g, '&quot;');

            // Step 2: **bold** → <strong>
            safe = safe.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

            // Step 3: *bold* (single asterisk) → <strong>
            safe = safe.replace(/\*([^*]+?)\*/g, '<strong>$1</strong>');

            return safe;
        })
        .join('<br>');
}