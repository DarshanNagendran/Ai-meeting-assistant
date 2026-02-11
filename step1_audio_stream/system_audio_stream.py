import sounddevice as sd
import numpy as np
import queue
import time

# ===============================
# CONFIG
# ===============================
SAMPLE_RATE = 44100
CHANNELS = 2
CHUNK_SECONDS = 3   # small real-time chunks

audio_queue = queue.Queue()

# ===============================
# AUDIO CALLBACK
# ===============================
def audio_callback(indata, frames, time_info, status):
    if status:
        print("⚠️", status)
    audio_queue.put(indata.copy())

# ===============================
# START STREAM
# ===============================
print("🎧 Starting live system audio stream...")
print("⏹ Press Ctrl+C to stop\n")

with sd.InputStream(
    samplerate=SAMPLE_RATE,
    channels=CHANNELS,
    callback=audio_callback
):
    try:
        chunk_count = 0
        start_time = time.time()

        while True:
            time.sleep(CHUNK_SECONDS)
            chunk_count += 1

            chunks = []
            while not audio_queue.empty():
                chunks.append(audio_queue.get())

            if chunks:
                audio_data = np.concatenate(chunks, axis=0)
                duration = audio_data.shape[0] / SAMPLE_RATE

                print(f"🔊 Chunk {chunk_count} | Duration: {duration:.2f}s")

    except KeyboardInterrupt:
        print("\n🛑 Audio stream stopped.")
