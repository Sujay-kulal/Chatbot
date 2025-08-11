document.addEventListener('DOMContentLoaded', () => {
    // Add initial bot welcome message with rich content
    const initialBotMessage = `
    <strong>Welcome to MITK AI Assistant!</strong><br>
    Ask me anything about Moodlakatte Institute of Technology – academics, departments, hostels, and more.<br><br>
    Here are some things I can help with:<br>
    <ul>
        <li>Academic programs and syllabus</li>
        <li>Departments and HoDs (HoD CS, etc)</li>
        <li>Opening times like library and Soudeshakar</li>
        <li>Events and festival information</li>
        <li>Hostel rules and administration</li>
    </ul>
    What would you like to know?
    `;

    addMessage(initialBotMessage, 'bot');

    // Suggested quick buttons remain as they are
    document.querySelectorAll('.suggested button').forEach(button => {
        button.addEventListener('click', () => {
            let topic = button.getAttribute('data-topic');
            addMessage(topic, 'user');
            getTopicInfo(topic);
        });
    });

    // Form submission to send user message
    document.getElementById('topic-form').addEventListener('submit', function(e) {
        e.preventDefault();
        let topicInput = document.getElementById('custom-topic');
        let topic = topicInput.value.trim();
        if (topic) {
            addMessage(topic, 'user');
            getTopicInfo(topic);
            topicInput.value = '';
        }
    });

    // addMessage and getTopicInfo functions as before...

    function addMessage(text, sender) {
        const chatHistory = document.getElementById('chat-history');
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender);
        let imgHTML;
        if (sender === 'user') {
            imgHTML = `<img class="avatar" src="user.jpg" alt="User">`;
        } else {
            imgHTML = `<img class="avatar" src="bot.jpg" alt="Bot">`;
        }
        messageDiv.innerHTML = imgHTML + `<span class="msg-text">${text}</span>`;
        chatHistory.appendChild(messageDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    function showTypingIndicator() {
        const chatHistory = document.getElementById('chat-history');
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing bot';
        typingDiv.id = 'typing-indicator';
        typingDiv.innerHTML = `<img class="avatar" src="bot.jpg" alt="Bot">
        <span class="typing-dots">
            <span></span><span></span><span></span>
        </span>`;
        chatHistory.appendChild(typingDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    function hideTypingIndicator() {
        const typingDiv = document.getElementById('typing-indicator');
        if (typingDiv) typingDiv.remove();
    }

    function getTopicInfo(topic) {
        showTypingIndicator();
        fetch(`/info?topic=${encodeURIComponent(topic)}`)
            .then(res => res.json())
            .then(data => {
                hideTypingIndicator();
                addMessage(data.response, 'bot');
            })
            .catch(() => {
                hideTypingIndicator();
                addMessage("Error connecting to server.", 'bot');
            });
    }
});
