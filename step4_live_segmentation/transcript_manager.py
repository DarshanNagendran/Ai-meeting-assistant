import os
from datetime import datetime

class TranscriptManager:
    def __init__(self):
        self.entries = []

    def add_entry(self, text: str):
        if not text.strip():
            return

        timestamp = datetime.now().strftime("%H:%M:%S")
        self.entries.append(f"[{timestamp}] {text}")

    def save(self):
        if not self.entries:
            return

        os.makedirs("transcripts", exist_ok=True)

        filename = datetime.now().strftime(
            "transcripts/meeting_%Y-%m-%d_%H-%M.txt"
        )

        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(self.entries))

        print(f"\n📝 Transcript saved to: {filename}")
