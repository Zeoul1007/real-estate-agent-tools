import os
from flask import Flask, request, jsonify, Response
import requests
from flask_cors import CORS
from datetime import datetime, timedelta
import urllib.parse

app = Flask(__name__)
CORS(app)

# ✅ AI Assistant - Uses OpenAI API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

@app.route('/ask-gpt', methods=['POST'])
def ask_gpt():
    data = request.json
    user_input = data.get("query", "")

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4-turbo",
        "messages": [{"role": "user", "content": user_input}]
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    return response.json()

# ✅ Function to parse event details from user input
def parse_event_details(event_text):
    # Example input: "Meeting with Tom at 2PM tomorrow"
    event_title = event_text
    now = datetime.utcnow()

    # Basic logic to detect "tomorrow"
    if "tomorrow" in event_text.lower():
        event_date = now + timedelta(days=1)
    else:
        event_date = now  # Default to today if no date is found

    # Detect time (basic 12-hour detection)
    event_time = "1200"  # Default time: 12:00 PM UTC
    if "2pm" in event_text.lower():
        event_time = "1400"
    elif "3pm" in event_text.lower():
        event_time = "1500"
    elif "4pm" in event_text.lower():
        event_time = "1600"

    # Format time as YYYYMMDDTHHMMSSZ
    start_time = event_date.strftime(f"%Y%m%dT{event_time}00Z")
    end_time = event_date.strftime(f"%Y%m%dT{str(int(event_time)+100)}00Z")  # Assume 1-hour duration

    return event_title, start_time, end_time

# ✅ Google & Apple Calendar Event Generator
@app.route('/generate-calendar-link', methods=['GET'])
def generate_calendar_link():
    event_text = request.args.get('event', 'Meeting with Client')

    event_title, start_time, end_time = parse_event_details(event_text)

    # ✅ Google Calendar URL
    google_calendar_url = (
        f"https://calendar.google.com/calendar/render?action=TEMPLATE"
        f"&text={urllib.parse.quote(event_title)}"
        f"&dates={start_time}/{end_time}"
    )

    # ✅ Apple Calendar (.ics file)
    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
SUMMARY:{event_title}
DTSTART:{start_time}
DTEND:{end_time}
DESCRIPTION:Scheduled via Real Estate Agent Tools.
END:VEVENT
END:VCALENDAR"""

    response = Response(ics_content, mimetype="text/calendar")
    response.headers["Content-Disposition"] = "attachment; filename=event.ics"

    return jsonify({
        "google_calendar_url": google_calendar_url,
        "apple_calendar_url": "/download-ics?event=" + urllib.parse.quote(event_title)
    })

# ✅ Apple Calendar .ics File Download
@app.route('/download-ics', methods=['GET'])
def download_ics():
    event_text = request.args.get('event', 'Meeting with Client')
    event_title, start_time, end_time = parse_event_details(event_text)

    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
SUMMARY:{event_title}
DTSTART:{start_time}
DTEND:{end_time}
DESCRIPTION:Scheduled via Real Estate Agent Tools.
END:VEVENT
END:VCALENDAR"""

    response = Response(ics_content, mimetype="text/calendar")
    response.headers["Content-Disposition"] = "attachment; filename=event.ics"
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
