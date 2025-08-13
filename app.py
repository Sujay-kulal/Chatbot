from flask import Flask, render_template, request, jsonify
import json
import os
import re

# Resolve absolute project directory and configure Flask to serve templates/static from project root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(
    __name__,
    template_folder=BASE_DIR,
    static_folder=BASE_DIR,
    static_url_path="",
)

# Load data files from the `data` directory using absolute paths
def load_json_file(*path_segments):
    file_path = os.path.join(BASE_DIR, *path_segments)
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

college_info = load_json_file('data', 'college_info.json')
synonyms = load_json_file('data', 'synonyms.json')

# Load greetings and small talk from college_info.json
GREETINGS = college_info.get('responses', {}).get('greetings', {})
SMALL_TALK = college_info.get('responses', {}).get('small_talk', {})

def clean_text(text: str) -> str:
    """Lowercase, strip, collapse spaces, and remove punctuation for robust matching."""
    lowered = text.lower().strip()
    # Remove non-alphanumeric/punctuation except spaces
    cleaned = re.sub(r"[^a-z0-9\s]", "", lowered)
    # Collapse multiple spaces
    return re.sub(r"\s+", " ", cleaned)

def find_matching_topic(user_input):
    processed = clean_text(user_input)

    # Check direct topic key matches first
    if processed in college_info:
        return processed

    # Check synonyms first (higher priority) - prioritize longer matches
    best_match = None
    best_match_length = 0
    
    for topic, synonym_list in synonyms.items():
        for synonym in synonym_list:
            syn = clean_text(synonym)
            if syn:
                # Check for exact match first (highest priority)
                if syn == processed:
                    return topic
                # Then check if the synonym is contained in the processed input
                elif syn in processed:
                    # Prioritize longer, more specific matches
                    if len(syn) > best_match_length:
                        best_match = topic
                        best_match_length = len(syn)
    
    if best_match:
        return best_match

    # Heuristic: if message mentions multiple department names, treat as departments
    # But only if it doesn't contain HOD-related keywords
    hod_keywords = ['hod', 'head', 'department head', 'head of department']
    has_hod_keyword = any(keyword in processed for keyword in hod_keywords)
    
    if not has_hod_keyword:
        try:
            dept_list = college_info.get('departments', [])
            if isinstance(dept_list, list) and dept_list:
                matches = 0
                for dept in dept_list:
                    dept_clean = clean_text(dept)
                    # Use key identifiers from department names (e.g., 'computer science', 'mechanical')
                    # Match if at least two-word phrase is present or the whole cleaned name is present
                    if dept_clean and (dept_clean in processed):
                        matches += 1
                    else:
                        # Try partial tokens for stronger recall
                        tokens = [t for t in dept_clean.split() if len(t) > 2]
                        if any(t in processed for t in tokens):
                            matches += 1
                if matches >= 2:
                    return 'departments'
        except Exception:
            pass

    return None

def format_response(response_data, topic):
    # Special handling for departments when stored as a list
    if topic == "departments" and isinstance(response_data, list):
        lines = []
        lines.append("🎓 **Academic Programs at MIT Kundapura**")
        lines.append("")
        lines.append("We offer the following programs:")
        lines.append("")
        for dept in response_data:
            lines.append(f"- {dept}")
        lines.append("")
        lines.append("Each department is equipped with experienced faculty and modern facilities to ensure quality education!")
        return '\n'.join(lines)

    if isinstance(response_data, str):
        return response_data
    
    if isinstance(response_data, dict):
        lines = []
        
        if topic == "labs":
            lines.append("🔬 MIT Kundapura boasts state-of-the-art laboratory facilities:")
            lines.append("")
            for lab_name, lab_desc in response_data.items():
                lab_title = lab_name.replace('_', ' ').title()
                lines.append(f"🏭 **{lab_title}**")
                lines.append(f"   {lab_desc}")
                lines.append("")
            lines.append("These labs provide hands-on experience essential for your professional development!")
            
        elif topic == "placements":
            lines.append("🎯 **MIT Kundapura Placement Excellence**")
            lines.append("")
            lines.append(f"📊 {response_data.get('overview', '')}")
            
            if 'stats_2024_2025' in response_data:
                stats = response_data['stats_2024_2025']
                lines.append("")
                lines.append("📈 **2024-25 Placement Highlights:**")
                lines.append(f"✅ Placement Success Rate: **{stats.get('placement_rate', 'N/A')}**")
                lines.append(f"💰 Average Package: **{stats.get('average_package', 'N/A')}**")
                lines.append(f"🏆 Highest Package Offered: **{stats.get('highest_package', 'N/A')}**")
                if stats.get('top_recruiters'):
                    lines.append(f"🏢 Leading Recruiters: **{', '.join(stats['top_recruiters'])}**")
                lines.append("")
                lines.append("Our dedicated placement cell works tirelessly to connect students with top industry opportunities!")
                
        elif topic == "events":
            lines.append("🎉 **MIT Kundapura - Where Learning Meets Fun!**")
            lines.append("")
            lines.append("Our campus buzzes with exciting events throughout the year:")
            lines.append("")
            for event_type, event_list in response_data.items():
                events = ', '.join(event_list) if isinstance(event_list, list) else str(event_list)
                event_icon = "🎭" if "cultural" in event_type else "⚡" if "technical" in event_type else "🏆" if "sports" in event_type else "🎪"
                lines.append(f"{event_icon} **{event_type.title()}:** {events}")
            lines.append("")
            lines.append("Join us for an unforgettable college experience filled with learning, growth, and memories!")
            
        elif topic == "departments":
            # In case departments are represented as a dict with categories
            lines.append("🎓 **Academic Programs at MIT Kundapura**")
            lines.append("")
            for category, items in response_data.items():
                lines.append(f"**{category.replace('_',' ').title()}:**")
                if isinstance(items, list):
                    for item in items:
                        lines.append(f"- {item}")
                else:
                    lines.append(f"- {items}")
                lines.append("")
            lines.append("Each department is equipped with experienced faculty and modern facilities to ensure quality education!")
            
        elif topic == "contact_info":
            lines.append("📞 **Get in Touch with MIT Kundapura**")
            lines.append("")
            lines.append("We're here to help and answer all your questions:")
            lines.append("")
            lines.append(f"📧 **Email:** {response_data.get('email', 'N/A')}")
            lines.append(f"☎️ **Phone:** {response_data.get('phone', 'N/A')}")
            lines.append(f"📍 **Address:** {response_data.get('address', 'N/A')}")
            lines.append("")
            lines.append("Feel free to reach out anytime - we'd love to hear from you!")
            
        elif topic == "hod_cs":
            lines.append("👨‍🏫 **CSE Head of Department**")
            lines.append("")
            name = response_data.get('name') or response_data.get('info') or "Mr. Muralidhara B K"
            lines.append(f"• **Name:** {name}")
            if response_data.get('designation'):
                lines.append(f"• **Designation:** {response_data['designation']}")
            if response_data.get('department'):
                lines.append(f"• **Department:** {response_data['department']}")
            if response_data.get('note'):
                lines.append(f"• {response_data['note']}")
        else:
            lines.append(f"ℹ️ **Information about {topic.title()}:**")
            lines.append("")
            for key, value in response_data.items():
                title = key.replace('_', ' ').title()
                lines.append(f"• **{title}:** {value}")
        
        return '\n'.join(lines)
    
    return str(response_data)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_input = data.get('message', '').strip()
        
        if not user_input:
            return jsonify({
                'response': "I'm ready to help! 🤖 Please ask me anything about MIT Kundapura - admissions, placements, facilities, or any other topic you're curious about."
            })
        
        processed_input = clean_text(user_input)
        
        # Check greetings (robust matching for variants like "hi!", "hello there", etc.)
        greet_key = None
        if processed_input in GREETINGS:
            greet_key = processed_input
        else:
            tokens = processed_input.split()
            if len(tokens) <= 4:
                for token in tokens:
                    if token in GREETINGS:
                        greet_key = token
                        break
        if greet_key:
            return jsonify({'response': GREETINGS[greet_key]})
        
        # Check small talk (normalize keys before compare)
        for key, value in SMALL_TALK.items():
            if clean_text(key) == processed_input:
                return jsonify({'response': value})
        
        # Find matching topic
        matched_topic = find_matching_topic(processed_input)
        
        if matched_topic and matched_topic in college_info:
            response_data = college_info[matched_topic]
            formatted_response = format_response(response_data, matched_topic)
            return jsonify({
                'response': formatted_response,
                'matched': matched_topic
            })
        
        return jsonify({
            'response': "🤔 I didn't quite catch that, but I'm here to help! Try asking me about:\n\n" +
                       "🎓 **Academics:** Admissions, departments, courses\n" +
                       "💼 **Career:** Placements, internships, industry connections\n" +
                       "🏠 **Campus Life:** Hostels, events, facilities\n" +
                       "📚 **Resources:** Library, labs, research opportunities\n" +
                       "📞 **Contact:** Getting in touch with the college\n\n" +
                       "What would you like to explore first?"
        })
        
    except Exception as e:
        return jsonify({
            'response': "Oops! 😅 I encountered a technical hiccup. Please try asking your question again - I'm here and ready to help!"
        }), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
