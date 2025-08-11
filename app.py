from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import difflib

app = Flask(__name__)
CORS(app)

COLLEGE_INFO = {
    "admissions": "Admissions open in June every year. Contact admissions@mitkundapura.edu.",
    "library": "The library is open from 8 AM to 8 PM, Monday to Saturday.",
    "hod_cs": "Mr. Muralidhara B K is the Head of the Department for Computer Science."
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
    "what's your name": "I'm your College Assistant Bot.",
    "thank you": "You're welcome! If you have more questions, just ask.",
    "goodbye": "Goodbye! Come back anytime with questions.",
}

QUESTION_PATTERNS = {
    "admissions": ["admission", "apply", "join", "enroll"],
    "library": ["library", "books", "timings"],
    "hod_cs": ["head of cs", "cs hod", "hod computer"]
}


def generate_response(user_input: str) -> dict:
    text = (user_input or "").strip().lower()
    if not text:
        return {"response": "Please type a question or pick a suggested topic below.", "matched": None}

    if m := difflib.get_close_matches(text, GREETINGS.keys(), n=1, cutoff=0.7):
        return {"response": GREETINGS[m[0]], "matched": m[0]}
    if m := difflib.get_close_matches(text, SMALL_TALK.keys(), n=1, cutoff=0.7):
        return {"response": SMALL_TALK[m[0]], "matched": m[0]}

    for key, patterns in QUESTION_PATTERNS.items():
        for pat in patterns:
            if pat in text:
                return {"response": COLLEGE_INFO.get(key, ""), "matched": key}

    if m := difflib.get_close_matches(text, COLLEGE_INFO.keys(), n=1, cutoff=0.7):
        key = m[0]
        return {"response": COLLEGE_INFO[key], "matched": key}

    return {"response": "Sorry, I don't have information on that topic.", "matched": None}


@app.route('/info')
def info():
    user_input = request.args.get('topic', '')
    result = generate_response(user_input)
    return jsonify({"response": result["response"], "matched": result["matched"]})


@app.post('/chat')
def chat():
    data = request.get_json(silent=True) or {}
    user_input = data.get('message', '')
    result = generate_response(user_input)
    return jsonify({"response": result["response"], "matched": result["matched"]})


@app.get('/health')
def health():
    return jsonify({"status": "ok"})


@app.route('/')
def home():
    return send_from_directory('.', 'index.html')


@app.route('/<path:filename>')
def files(filename):
    return send_from_directory('.', filename)


if __name__ == '__main__':
    app.run(debug=True)
