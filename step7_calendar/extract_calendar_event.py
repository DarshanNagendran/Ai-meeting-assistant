import os
import json
from groq import Groq
from datetime import datetime, timedelta, timezone
import uuid

# ================= CONFIG =================
GROQ_API_KEY = "API KEY"
MODEL = "llama-3.1-8b-instant"

TRANSCRIPTS_DIR = r"D:\meetsnap\transcripts"
OUTPUT_ICS = r"D:\meetsnap\step7_calendar\meeting_event.ics"

DEFAULT_DURATION_MIN = 60
# =========================================


def get_latest_transcript():
    files = [
        os.path.join(TRANSCRIPTS_DIR, f)
        for f in os.listdir(TRANSCRIPTS_DIR)
        if f.endswith(".txt")
    ]
    if not files:
        raise FileNotFoundError("No transcript found")
    return max(files, key=os.path.getmtime)


def read_transcript(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def extract_event_with_ai(transcript):
    client = Groq(api_key=GROQ_API_KEY)

    today = datetime.now().strftime("%Y-%m-%d")

    prompt = f"""
    You are a strict JSON generator.

    TODAY'S DATE: {today}

    TASK:
    From the meeting transcript, detect if a meeting or appointment is being scheduled.

    OUTPUT RULES (VERY IMPORTANT):
    - Return ONLY valid JSON
    - Do NOT include explanations
    - Do NOT include markdown
    - Do NOT include any text outside JSON
    - Do NOT include comments or notes

    If a meeting exists, return EXACTLY this format:

    {{
      "title": "Meeting title",
      "date": "YYYY-MM-DD",
      "time": "HH:MM",
      "duration": 60,
      "location": "Location or Not mentioned"
    }}

    If NO meeting exists, return exactly:
    NO_EVENT

    Transcript:
    {transcript}
    """

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You extract calendar events."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=400
    )

    content = response.choices[0].message.content.strip()
    return content


def generate_ics(event):
    start_dt = datetime.strptime(
        f"{event['date']} {event['time']}",
        "%Y-%m-%d %H:%M"
    ).replace(tzinfo=timezone.utc)

    end_dt = start_dt + timedelta(minutes=event["duration"])

    uid = f"{uuid.uuid4()}@meetsnap.ai"
    now_utc = datetime.now(timezone.utc)

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//MeetSnap//Smart Calendar//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",

        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{now_utc.strftime('%Y%m%dT%H%M%SZ')}",
        f"DTSTART:{start_dt.strftime('%Y%m%dT%H%M%SZ')}",
        f"DTEND:{end_dt.strftime('%Y%m%dT%H%M%SZ')}",
        f"SUMMARY:{event['title']}",
        f"DESCRIPTION:Meeting scheduled via MeetSnap",
        f"LOCATION:{event['location']}",
        "STATUS:CONFIRMED",
        "SEQUENCE:0",
        "TRANSP:OPAQUE",
        # --- Outlook-friendly additions ---
        "ORGANIZER;CN=MeetSnap:mailto:meetsnap@ai.app",
        "ATTENDEE;CN=You;RSVP=TRUE:mailto:you@example.com",
        "END:VEVENT",


        "END:VCALENDAR"
    ]

    # Outlook requires CRLF + final newline
    return "\r\n".join(lines) + "\r\n"

def main():
    transcript_path = get_latest_transcript()
    print(f"📄 Using transcript: {transcript_path}")

    transcript = read_transcript(transcript_path)

    ai_result = extract_event_with_ai(transcript)

    if ai_result == "NO_EVENT":
        print("⚠️ No calendar event detected")
        return

    try:
        event = json.loads(ai_result)
    except json.JSONDecodeError:
        print("❌ AI output not valid JSON")
        print(ai_result)
        return

    os.makedirs(os.path.dirname(OUTPUT_ICS), exist_ok=True)

    ics_content = generate_ics(event)

    with open(OUTPUT_ICS, "w", encoding="utf-8") as f:
        f.write(ics_content)

    print(f"📅 Calendar event created: {OUTPUT_ICS}")

    open_calendar_file(OUTPUT_ICS)



import os
import sys
import subprocess

def open_calendar_file(path):
    try:
        if sys.platform.startswith("win"):
            os.startfile(path)          # ✅ Windows (Outlook)
        elif sys.platform.startswith("darwin"):
            subprocess.call(["open", path])   # macOS
        else:
            subprocess.call(["xdg-open", path])  # Linux
    except Exception as e:
        print("⚠️ Could not auto-open calendar:", e)




if __name__ == "__main__":
    main()

