from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import difflib

app = Flask(__name__)
CORS(app)

COLLEGE_INFO = {
    "admissions": "Admissions open in June every year. Contact admissions@mitkundapura.edu.",
    "library": "The library is open from 8 AM to 8 PM, Monday to Saturday.",
    "hod_cs": "Dr. A. Kumar is the Head of the Department for Computer Science."
}

GREETINGS = {
    "hi": "Hello! How can I help you today?",
    "hello": "Hello! How can I help you today?",
    "hey": "Hey there! Need any info about the college?",
    "good morning": "Good morning! How can I assist you?",
    "good afternoon": "Good afternoon! How can I assist you?",
    "good evening": "Good evening! How can I help?",
    "goodnight": "Good night! Feel free to ask me anything 24/7.",
}

SMALL_TALK = {
    "how are you": "I'm great! Thanks for asking. How can I help you at MIT Kundapura?",
    "how are you doing": "I'm just a bot, but I'm ready to help! What would you like to know?",
    "what's your name": "I'm your College Assistant Bot. Here to help with anything about MIT Kundapura!",
    "thank you": "You're welcome! If you have more questions, just ask.",
    "thanks": "Glad to help! 😊",
    "who made you": "I was built by the team at MIT Kundapura to assist students and visitors.",
    "goodbye": "Goodbye! Feel free to come back anytime with your questions.",
    "see you": "See you soon! Wishing you a great day.",
    "tell me something": "Did you know? Our library is open from 8 AM to 8 PM, Monday to Saturday.",
    "ok": "Alright! Let me know if you need anything else.",
    "yes": "Great! Please tell me more or ask your question.",
    "no": "No problem. Just let me know if you have any questions."
}

QUESTION_PATTERNS = {
    "admissions": ["admission", "admition", "admidon", "admisson", "apply", "join", "enroll"],
    "library": ["library", "books", "timings", "reading"],
    "hod_cs": ["head of cs", "cs hod", "hod computer", "department head", "hod", "computer science hod"]
}

@app.route('/info')
def info():
    user_input = request.args.get('topic', '').lower().strip()

    greet_match = difflib.get_close_matches(user_input, GREETINGS.keys(), n=1, cutoff=0.7)
    if greet_match:
        return jsonify({"response": GREETINGS[greet_match[0]]})

    st_match = difflib.get_close_matches(user_input, SMALL_TALK.keys(), n=1, cutoff=0.7)
    if st_match:
        return jsonify({"response": SMALL_TALK[st_match[0]]})

    for key, patterns in QUESTION_PATTERNS.items():
        for pat in patterns:
            if pat in user_input or difflib.get_close_matches(pat, user_input.split(), n=1, cutoff=0.7):
                return jsonify({"response": COLLEGE_INFO.get(key)})
            if difflib.SequenceMatcher(None, pat, user_input).ratio() > 0.77:
                return jsonify({"response": COLLEGE_INFO.get(key)})

    topic_match = difflib.get_close_matches(user_input, COLLEGE_INFO.keys(), n=1, cutoff=0.7)
    if topic_match:
        return jsonify({"response": COLLEGE_INFO.get(topic_match[0])})

    return jsonify({"response": "Sorry, I don't have information on that topic."})

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)

if __name__ == '__main__':
    app.run(debug=True)
