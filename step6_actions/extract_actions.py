import os
import textwrap
from groq import Groq

# 🔐 Groq API Key
GROQ_API_KEY = "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"

# 🤖 Model (FAST + FREE TIER)
MODEL = "llama-3.1-8b-instant"


TRANSCRIPTS_DIR = r"D:\meetsnap\transcripts"
OUTPUT_PATH = r"D:\meetsnap\step6_actions\actions.txt"

MAX_CHARS = 3000


def get_latest_transcript(directory):
    txt_files = [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.endswith(".txt")
    ]

    if not txt_files:
        raise FileNotFoundError("No transcript files found")

    return max(txt_files, key=os.path.getmtime)


def read_transcript(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def split_text(text, max_chars):
    return textwrap.wrap(text, max_chars, break_long_words=False)


def extract_actions_with_groq(chunk, idx, total, client):
    print(f"➡️ Processing chunk {idx}/{total}")

    prompt = f"""
You are a meeting assistant.

From the transcript below, extract:

1. ACTION ITEMS (task, owner if mentioned, deadline if mentioned)
2. DECISIONS made

Use STRICT format:

ACTION ITEMS:
- Task | Owner | Deadline

DECISIONS:
- Decision

If something is missing, write "Not mentioned".

Transcript:
{chunk}
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You extract structured meeting outcomes."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=500
    )

    return response.choices[0].message.content.strip()


def main():
    client = Groq(api_key=GROQ_API_KEY)

    latest_transcript = get_latest_transcript(TRANSCRIPTS_DIR)
    print(f"📄 Using transcript: {latest_transcript}")

    transcript = read_transcript(latest_transcript)
    chunks = split_text(transcript, MAX_CHARS)

    outputs = []

    for i, chunk in enumerate(chunks, start=1):
        result = extract_actions_with_groq(chunk, i, len(chunks), client)
        outputs.append(result)

    final_output = "\n\n".join(outputs)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(final_output)

    print("\n✅ Action items & decisions extracted successfully")


if __name__ == "__main__":
    main()
