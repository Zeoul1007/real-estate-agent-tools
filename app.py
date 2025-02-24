import os
from flask import Flask, request, jsonify, Response
import requests

app = Flask(__name__)

# ✅ Get API Key securely from Railway environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ✅ Root URL - Confirms the API is running
@app.route('/')
def home():
    return "✅ API is running!"

# ✅ AI Assistant - Uses OpenAI API
@app.route('/ask-gpt', methods=['POST'])
def ask_gpt():
    data = request.json
    user_input = data.get("query", "")

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4-turbo",  # Change this if using a fine-tuned model
        "messages": [{"role": "user", "content": user_input}]
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    return response.json()

# ✅ Calendar Scheduling - Generates Google Calendar Links
@app.route('/generate-calendar-link', methods=['GET'])
def generate_calendar_link():
    event = request.args.get('event', 'Meeting with Client')
    google_calendar_url = (
        f"https://calendar.google.com/calendar/render?action=TEMPLATE"
        f"&text={event.replace(' ', '+')}"
    )

    return jsonify({
        "google_calendar_url": google_calendar_url
    })

# ✅ Apple Calendar Support - Generates .ics Files
@app.route('/download-ics', methods=['GET'])
def download_ics():
    event = request.args.get('event', 'Meeting with Client')
    location = request.args.get('location', 'Office')
    start_time = "20240301T140000Z"
    end_time = "20240301T150000Z"

    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
SUMMARY:{event}
DTSTART:{start_time}
DTEND:{end_time}
LOCATION:{location}
DESCRIPTION:Meeting scheduled via Real Estate Agent Tools.
END:VEVENT
END:VCALENDAR"""

    response = Response(ics_content, mimetype="text/calendar")
    response.headers["Content-Disposition"] = "attachment; filename=event.ics"
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
