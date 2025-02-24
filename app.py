import os
from flask import Flask, request, jsonify, Response
import requests
from flask_cors import CORS
from datetime import datetime, timedelta
import urllib.parse

app = Flask(__name__)
CORS(app)

# ✅ AI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ✅ Function to extract event details using OpenAI GPT
def parse_event_details(event_text):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
    Extract the details from this event description: "{event_text}".
    Return a JSON object with:
    - "title": The main event title.
    - "date": The event date in YYYY-MM-DD format.
    - "time": The event start time in HH:MM format (24-hour clock).
    - "location": The event location (if mentioned).
    """

    payload = {
        "model": "gpt-4-turbo",
        "messages": [{"role": "system", "content": prompt}]
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    ai_response = response.json()

    # Extract AI response
    event_data = ai_response["choices"][0]["message"]["content"]
    event_json = eval(event_data)  # Convert AI response from string to dictionary

    # Convert AI date & time to Google/Apple Calendar format
    event_date = datetime.strptime(event_json["date"], "%Y-%m-%d")
    start_time = event_date.strftime(f"%Y%m%dT{event_json['time'].replace(':', '')}00Z")
    end_time = event_date.strftime(f"%Y%m%dT{str(int(event_json['time'][:2]) + 1)}00Z")  # Assume 1-hour duration

    return event_json["title"], start_time, end_time, event_json["location"]

# ✅ Google & Apple Calendar Event Generator
@app.route('/generate-calendar-link', methods=['GET'])
def generate_calendar_link():
    event_text = request.args.get('event', 'Meeting with Client')

    event_title, start_time, end_time, location = parse_event_details(event_text)

    # ✅ Google Calendar URL
    google_calendar_url = (
        f"https://calendar.google.com/calendar/render?action=TEMPLATE"
        f"&text={urllib.parse.quote(event_title)}"
        f"&dates={start_time}/{end_time}"
        f"&location={urllib.parse.quote(location)}"
    )

    # ✅ Apple Calendar (.ics file)
    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
SUMMARY:{event_title}
DTSTART:{start_time}
DTEND:{end_time}
LOCATION:{location}
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
    event_title, start_time, end_time, location = parse_event_details(event_text)

    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
SUMMARY:{event_title}
DTSTART:{start_time}
DTEND:{end_time}
LOCATION:{location}
DESCRIPTION:Scheduled via Real Estate Agent Tools.
END:VEVENT
END:VCALENDAR"""

    response = Response(ics_content, mimetype="text/calendar")
    response.headers["Content-Disposition"] = "attachment; filename=event.ics"
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
