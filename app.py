from flask import Flask, request, jsonify, Response

app = Flask(__name__)

def create_ics_file(event_name, start_time, end_time, location, details):
    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
SUMMARY:{event_name}
DTSTART:{start_time}
DTEND:{end_time}
LOCATION:{location}
DESCRIPTION:{details}
END:VEVENT
END:VCALENDAR"""
    return ics_content

@app.route('/generate-calendar-link', methods=['GET'])
def generate_calendar_link():
    event = request.args.get('event', 'Meeting with Client')
    location = request.args.get('location', 'Office')
    details = request.args.get('details', 'Real estate meeting.')
    start_time = request.args.get('start_time', '20240301T140000Z')  # Example format
    end_time = request.args.get('end_time', '20240301T150000Z')

    # Google Calendar Link
    google_calendar_url = (
        f"https://calendar.google.com/calendar/render?action=TEMPLATE"
        f"&text={event.replace(' ', '+')}"
        f"&dates={start_time}/{end_time}"
        f"&details={details.replace(' ', '+')}"
        f"&location={location.replace(' ', '+')}"
    )

    # Apple Calendar (iCalendar .ics file)
    ics_url = f"https://your-railway-app.com/download-ics?event={event.replace(' ', '+')}"

    return jsonify({
        "google_calendar_url": google_calendar_url,
        "apple_calendar_url": ics_url
    })

@app.route('/download-ics', methods=['GET'])
def download_ics():
    event = request.args.get('event', 'Meeting with Client')
    location = request.args.get('location', 'Office')
    details = request.args.get('details', 'Real estate meeting.')
    start_time = request.args.get('start_time', '20240301T140000Z')
    end_time = request.args.get('end_time', '20240301T150000Z')

    ics_content = create_ics_file(event, start_time, end_time, location, details)
    
    response = Response(ics_content, mimetype="text/calendar")
    response.headers["Content-Disposition"] = "attachment; filename=event.ics"
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
