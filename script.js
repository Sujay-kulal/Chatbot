document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.suggested button').forEach(button => {
        button.addEventListener('click', () => {
            let topic = button.getAttribute('data-topic');
            addMessage(topic, 'user');
            getTopicInfo(topic);
        });
    });

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

    function addMessage(text, sender) {
        const chatHistory = document.getElementById('chat-history');
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender);
        let imgHTML;
        if (sender === 'user') {
            imgHTML = `<img class="avatar" src="static/user.jpg" alt="User">`;
        } else {
            imgHTML = `<img class="avatar" src="static/bot.jpg" alt="Bot">`;
        }
        messageDiv.innerHTML = imgHTML + `<span class="msg-text">${text}</span>`;
        chatHistory.appendChild(messageDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    function getTopicInfo(topic) {
        fetch(`/info?topic=${encodeURIComponent(topic)}`)
            .then(res => res.json())
            .then(data => {
                addMessage(data.response, 'bot');
            })
            .catch(() => {
                addMessage("Error connecting to server.", 'bot');
            });
    }
});
