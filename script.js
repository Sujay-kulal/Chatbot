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
});

function addMessage(text, sender) {
    const chatHistory = document.getElementById('chat-history');
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender);

    let imgHTML;
    if (sender === 'user') {
        imgHTML = '<img src="user.png" alt="User Logo" class="avatar user-avatar">';
    } else {
        imgHTML = '<img src="bot.png" alt="Bot Logo" class="avatar bot-avatar">';
    }
    messageDiv.innerHTML = imgHTML + '<span class="msg-text"></span>';
    messageDiv.querySelector('.msg-text').textContent = text;
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
