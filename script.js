window.addEventListener("DOMContentLoaded", () => {
    const messages = document.getElementById("messages");
    const chatForm = document.getElementById("chat-form");
    const topicInput = document.getElementById("topic-input");
    const suggestionBtns = document.querySelectorAll(".suggested-questions button");

    function addMessage(text, sender = "bot") {
        const message = document.createElement("div");
        message.className = `message ${sender}`;
        message.innerHTML = `
            <img class="avatar" src="${sender === 'user' ? 'user.png' : 'bot.png'}" />
            <div class="bubble">${text}</div>
        `;
        messages.appendChild(message);
        messages.scrollTop = messages.scrollHeight;
    }
    async function getBotResponse(question) {
        addMessage(question, "user");
        topicInput.value = "";
        const resp = await fetch(`/info?topic=${encodeURIComponent(question)}`);
        const data = await resp.json();
        setTimeout(() => {
            addMessage(data.response, "bot");
        }, 450);
    }

    chatForm.addEventListener("submit", e => {
        e.preventDefault();
        const q = topicInput.value.trim();
        if (q) getBotResponse(q);
    });

    suggestionBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            getBotResponse(btn.innerText);
        });
    });
});
