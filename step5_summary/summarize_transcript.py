import requests
import textwrap
import os

API_KEY = "NLP API KEY"

MODEL = "finetuned-llama-3-70b"  # if unavailable, use "bart-large-cnn"

TRANSCRIPTS_DIR = r"D:\meetsnap\transcripts"
SUMMARY_OUTPUT_PATH = r"D:\meetsnap\step5_summary\final_summary.txt"

MAX_CHARS = 3000

def get_latest_transcript():
    files = [
        os.path.join(TRANSCRIPTS_DIR, f)
        for f in os.listdir(TRANSCRIPTS_DIR)
        if f.endswith(".txt")
    ]

    if not files:
        raise FileNotFoundError("No transcript files found")

    return max(files, key=os.path.getmtime)

def read_transcript(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def split_text(text, max_chars):
    return textwrap.wrap(text, max_chars, break_long_words=False)


def summarize_chunk(chunk, idx, total):
    print(f"➡️ Summarizing chunk {idx}/{total}")

    payload = {
        "text": chunk,
        "min_length": 120,
        "max_length": 400,
        "do_sample": False
    }

    response = requests.post(
        f"https://api.nlpcloud.io/v1/gpu/{MODEL}/summarization",
        headers={
            "Authorization": f"Token {API_KEY}",
            "Content-Type": "application/json"
        },
        json=payload
    )

    response.raise_for_status()
    return response.json()["summary_text"]


def main():
    transcript_path = get_latest_transcript()
    print(f"📄 Using transcript: {transcript_path}")

    transcript = read_transcript(transcript_path)
    chunks = split_text(transcript, MAX_CHARS)

    print(f"📝 Summarizing {len(chunks)} chunks...\n")

    summaries = []
    for i, chunk in enumerate(chunks, start=1):
        summaries.append(summarize_chunk(chunk, i, len(chunks)))

    final_summary = "\n\n".join(summaries)

    print("\n🔹 FINAL SUMMARY:\n")
    print(final_summary)

    with open(SUMMARY_OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(final_summary)


if __name__ == "__main__":
    main()

