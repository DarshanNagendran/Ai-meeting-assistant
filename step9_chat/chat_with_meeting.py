import os
from groq import Groq

GROQ_API_KEY = "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"
MODEL = "llama-3.1-8b-instant"

TRANSCRIPTS_DIR = r"D:\meetsnap\transcripts"


def get_latest_transcript():
    files = [
        os.path.join(TRANSCRIPTS_DIR, f)
        for f in os.listdir(TRANSCRIPTS_DIR)
        if f.endswith(".txt")
    ]

    if not files:
        raise FileNotFoundError("No transcripts found")

    return max(files, key=os.path.getmtime)


def load_transcript():
    path = get_latest_transcript()

    with open(path, "r", encoding="utf-8") as f:
        return f.read()


class MeetingChatBot:
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.transcript = load_transcript()

        self.system_prompt = f"""
You are MeetSnap AI assistant.

You can BOTH:
1. Chat normally with the user
2. Answer questions using the meeting transcript

Rules:

- If the user greets or chats casually, respond naturally.
- If the user asks about the meeting, use the transcript.
- If transcript doesn't contain the answer, say:
  "That information is not in the meeting."

Transcript:
{self.transcript}
"""

        self.messages = [
            {"role": "system", "content": self.system_prompt}
        ]

    def ask(self, question: str):

        self.messages.append(
            {"role": "user", "content": question}
        )

        response = self.client.chat.completions.create(
            model=MODEL,
            messages=self.messages,
            temperature=0.3,
            max_tokens=500
        )

        answer = response.choices[0].message.content.strip()

        self.messages.append(
            {"role": "assistant", "content": answer}
        )

        return answer
