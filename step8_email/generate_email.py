import os
import urllib.parse
from groq import Groq

# ========== CONFIG ==========
GROQ_API_KEY = "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"
MODEL = "llama-3.1-8b-instant"

TRANSCRIPTS_DIR = r"D:\meetsnap\transcripts"
# ============================


def get_latest_transcript():
    files = [
        os.path.join(TRANSCRIPTS_DIR, f)
        for f in os.listdir(TRANSCRIPTS_DIR)
        if f.endswith(".txt")
    ]
    return max(files, key=os.path.getmtime)


def read_transcript(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def generate_email(transcript):
    client = Groq(api_key=GROQ_API_KEY)

    prompt = f"""
You are an assistant that writes professional follow-up emails.

TASK:
Write a concise post-meeting follow-up email.

RULES:
- Professional tone
- Friendly
- No markdown
- No explanations

FORMAT EXACTLY LIKE THIS:

SUBJECT:
<subject line>

BODY:
<email body>

Transcript:
{transcript}
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=500
    )

    return response.choices[0].message.content.strip()


def open_email(subject, body, to=""):
    subject = urllib.parse.quote(subject)
    body = urllib.parse.quote(body)

    mailto = f"mailto:{to}?subject={subject}&body={body}"
    os.startfile(mailto)


def main():
    transcript_path = get_latest_transcript()
    transcript = read_transcript(transcript_path)

    email_text = generate_email(transcript)

    subject = email_text.split("SUBJECT:")[1].split("BODY:")[0].strip()
    body = email_text.split("BODY:")[1].strip()

    open_email(subject, body)

    print("✅ Email draft opened in mail app")


if __name__ == "__main__":
    main()
