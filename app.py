from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import difflib
import os
import json

app = Flask(__name__)
CORS(app)

# Knowledge base (with ability to load from data/ if present)
COLLEGE_INFO = {
    "admissions": "Admissions open in June every year. Contact admissions@mitkundapura.edu.",
    "library": "The library is open from 8 AM to 8 PM, Monday to Saturday.",
    "hod_cs": "Dr. A. Kumar is the Head of the Department for Computer Science.",
    "hostel": "Hostels have in-time at 9:30 PM on weekdays and 10:00 PM on weekends.",
    "placements": "The Training & Placement Cell conducts drives from August to March.",
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
    "admissions": ["admission", "apply", "join", "enroll", "eligibility", "cutoff"],
    "library": ["library", "book", "timing", "issue", "return"],
    "hod_cs": ["head of cs", "cs hod", "hod computer", "cse hod", "hod"],
    "hostel": ["hostel", "warden", "mess", "in time", "night"],
    "placements": ["placement", "drive", "job", "internship"],
}


def load_json(path: str) -> dict:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


# Load external data if present
COLLEGE_INFO.update(load_json(os.path.join('data', 'college_info.json')))
QUESTION_PATTERNS.update(load_json(os.path.join('data', 'synonyms.json')))


def normalize(text: str) -> str:
    return (text or "").strip().lower()


def generate_response(user_input: str) -> dict:
    query = normalize(user_input)
    if not query:
        return {"response": "Please type a question or pick a suggested topic below.", "matched": None}

    if m := difflib.get_close_matches(query, GREETINGS.keys(), n=1, cutoff=0.8):
        return {"response": GREETINGS[m[0]], "matched": m[0]}
    if m := difflib.get_close_matches(query, SMALL_TALK.keys(), n=1, cutoff=0.8):
        return {"response": SMALL_TALK[m[0]], "matched": m[0]}

    for key, patterns in QUESTION_PATTERNS.items():
        for pat in patterns:
            if pat in query:
                return {"response": COLLEGE_INFO.get(key, ""), "matched": key}

    if m := difflib.get_close_matches(query, COLLEGE_INFO.keys(), n=1, cutoff=0.7):
        key = m[0]
        return {"response": COLLEGE_INFO[key], "matched": key}

    suggestions = ", ".join(sorted(list(COLLEGE_INFO.keys()))[:6])
    return {"response": f"Sorry, I don't have information on that yet. Try asking about: {suggestions}.", "matched": None}


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


FOLLOW_UP = {
    "admissions": ["Eligibility criteria?", "Important dates?", "How to apply?"],
    "library": ["Borrowing rules?", "Late fine?", "Digital resources?"],
    "hostel": ["Hostel fees?", "Visitor policy?", "Mess timings?"],
    "placements": ["Upcoming drives?", "Average package?", "Training schedule?"],
}


@app.get('/suggestions')
def suggestions():
    topic = request.args.get('topic', '')
    items = FOLLOW_UP.get(topic, list(COLLEGE_INFO.keys())[:5])
    return jsonify({"suggestions": items})


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
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', '5000'))
    debug = os.environ.get('FLASK_DEBUG', 'true').lower() == 'true'
    app.run(host=host, port=port, debug=debug)
