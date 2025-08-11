document.addEventListener('DOMContentLoaded', () => {
    const chatHistoryEl = document.getElementById('chat-history');
    const formEl = document.getElementById('topic-form');
    const inputEl = document.getElementById('custom-topic');

    function getStoredHistory() {
        try { return JSON.parse(localStorage.getItem('chatHistory') || '[]'); } catch { return []; }
    }
    function setStoredHistory(history) {
        localStorage.setItem('chatHistory', JSON.stringify(history));
    }

    function renderHistory() {
        chatHistoryEl.innerHTML = '';
        const history = getStoredHistory();
        history.forEach(item => {
            const div = document.createElement('div');
            div.className = 'message ' + item.sender;
            const avatar = item.sender === 'user' ? 'user.png' : 'bot.png';
            const time = item.time || '';
            div.innerHTML = `<img class="avatar" src="${avatar}" alt="${item.sender}"><span class="msg-text">${item.html}${time ? `<br><small class=\"timestamp\">${time}</small>` : ''}</span>`;
            chatHistoryEl.appendChild(div);
        });
        chatHistoryEl.scrollTop = chatHistoryEl.scrollHeight;
    }

    const initialBotMessage = `
        <strong>Welcome to MITK AI Assistant!</strong><br>
        Ask me anything about Moodlakatte Institute of Technology – academics, departments, hostels, and more.<br><br>
        Here are some things I can help with:
        <ul>
            <li>Admissions, fees and scholarships</li>
            <li>Library timings and borrowing rules</li>
            <li>Departments and HoDs (e.g., CS HoD)</li>
            <li>Hostel rules and canteen timings</li>
            <li>Transport, placements, and academic calendar</li>
        </ul>
        What would you like to know?<br>
        <div class="inline-suggested">
            <button class="inline-btn" data-topic="admissions">🎓 Admissions</button>
            <button class="inline-btn" data-topic="library">📚 Library</button>
            <button class="inline-btn" data-topic="hod_cs">👨‍🏫 CS HoD</button>
            <button class="inline-btn" data-topic="hostel">🏠 Hostel</button>
            <button class="inline-btn" data-topic="placements">💼 Placements</button>
        </div>
    `;

    if (getStoredHistory().length === 0) {
        addMessage(initialBotMessage, 'bot');
    } else {
        renderHistory();
    }

    // Theme removed per request

    chatHistoryEl.addEventListener('click', e => {
        if (e.target.classList.contains('inline-btn')) {
            const topic = e.target.getAttribute('data-topic');
            addMessage(e.target.textContent, 'user');
            askServer(topic);
        }
    });

    // Auto-grow textarea behavior on input
    inputEl.addEventListener('input', () => {
        inputEl.style.height = 'auto';
        inputEl.style.height = Math.min(inputEl.scrollHeight, 160) + 'px';
    });

    // Enter to send (no Shift behavior)
    inputEl.addEventListener('keydown', e => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            formEl.requestSubmit();
        }
    });

    formEl.addEventListener('submit', e => {
        e.preventDefault();
        const message = inputEl.value.trim();
        if (!message) return;
        addMessage(message, 'user');
        askServer(message);
        inputEl.value = '';
        inputEl.style.height = 'auto';
    });

    function formatTime(date = new Date()) {
        const h = date.getHours();
        const m = String(date.getMinutes()).padStart(2, '0');
        const ampm = h >= 12 ? 'PM' : 'AM';
        const hr12 = h % 12 || 12;
        return `${hr12}:${m} ${ampm}`;
    }

    function addMessage(html, sender, persist = true) {
        const div = document.createElement('div');
        div.className = 'message ' + sender;
        const avatar = sender === 'user' ? 'user.png' : 'bot.png';
        const time = formatTime();
        div.innerHTML = `<img class=\"avatar\" src=\"${avatar}\" alt=\"${sender}\"><span class=\"msg-text\">${html}<br><small class=\"timestamp\">${time}</small></span>`;
        chatHistoryEl.appendChild(div);
        chatHistoryEl.scrollTop = chatHistoryEl.scrollHeight;
        if (persist) {
            const history = getStoredHistory();
            history.push({ html, sender, time });
            setStoredHistory(history);
        }
    }

    function showTyping() {
        const typing = document.createElement('div');
        typing.className = 'message bot typing';
        typing.innerHTML = `<img class="avatar" src="bot.png" alt="bot"><span class="msg-text"><span class="dots"><span></span><span></span><span></span></span></span>`;
        chatHistoryEl.appendChild(typing);
        chatHistoryEl.scrollTop = chatHistoryEl.scrollHeight;
        return typing;
    }

    async function askServer(text) {
        const typingEl = showTyping();
        formEl.querySelector('button[type="submit"]').disabled = true;
        inputEl.disabled = true;
        try {
            const res = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });
            const data = await res.json();
            typingEl.remove();
            addMessage(data.response, 'bot');
            // Fetch and show follow-up suggestions if a topic matched
            if (data.matched) {
                try {
                    const s = await fetch(`/suggestions?topic=${encodeURIComponent(data.matched)}`);
                    const sData = await s.json();
                    const chips = (sData.suggestions || []).slice(0,3)
                      .map(t => `<button class=\"inline-btn\" data-topic=\"${t.toLowerCase()}\">${t}</button>`)
                      .join(' ');
                    if (chips) addMessage(`<div class=\"inline-suggested\">${chips}</div>`, 'bot');
                } catch {}
            }
        } catch (e) {
            typingEl.remove();
            addMessage('Error connecting to server.', 'bot');
        } finally {
            formEl.querySelector('button[type="submit"]').disabled = false;
            inputEl.disabled = false;
            inputEl.focus();
        }
    }

    // Removed clear button per request
});
