from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
import difflib
import os

app = Flask(__name__)
CORS(app)

COLLEGE_INFO = {
    "admissions": "Admissions open in June every year. Contact admissions@mitkundapura.edu.",
    "library timings": "The library is open from 8 AM to 8 PM, Monday to Saturday.",
    "head of cs dept": "Dr. S. R. Patil is the Head of the Computer Science Department.",
    "events": "The college hosts workshops, hackathons, and cultural events every semester.",
    "facilities": "We have labs, library, sports grounds, WiFi, and hostels available.",
}

GREETINGS = {
    "hi": "Hello! How can I help you?",
    "hello": "Hi there! How can I assist?",
    "hey": "Hey! Ask me anything about MITK.",
}

SMALL_TALK = {
    "how are you": "I'm just a bot, but I'm here to help you!",
    "what's your name": "I'm the MITK AI Assistant.",
    "thank you": "You're welcome!",
}

def get_close_response(query, data):
    possible = difflib.get_close_matches(query.lower(), data.keys(), n=1, cutoff=0.6)
    if possible:
        return data[possible[0]]
    return None

@app.route("/info")
def info():
    topic = request.args.get('topic', '').lower()
    for dataset in [GREETINGS, SMALL_TALK, COLLEGE_INFO]:
        resp = get_close_response(topic, dataset)
        if resp:
            return jsonify({'response': resp})
    return jsonify({'response': "Sorry, I didn't understand. Can you please rephrase?"})

@app.route("/")
def home():
    # Serve index.html from the root directory
    return send_from_directory(os.path.abspath("."), "index.html")

@app.route('/<path:filename>')
def root_files(filename):
    # Serve any root-level file (css, js, images, etc)
    return send_from_directory(os.path.abspath("."), filename)

if __name__ == "__main__":
    app.run(debug=True)
