import sounddevice as sd
import numpy as np
import whisper
import tempfile
import scipy.io.wavfile as wav
import time
import queue
import os

# ---------------- CONFIG ----------------
DEVICE_INDEX = 10          # Stereo Mix (Realtek)
DEVICE_SR = 48000
TARGET_SR = 16000
CHUNK_SEC = 2.0
ENERGY_THRESHOLD = 0.002
# ---------------------------------------

print("🧠 Loading Whisper model...")
model = whisper.load_model("base")
print("✅ Model loaded\n")

audio_q = queue.Queue()
buffer = []

def resample(audio, orig_sr, target_sr):
    return np.interp(
        np.linspace(0, len(audio), int(len(audio) * target_sr / orig_sr)),
        np.arange(len(audio)),
        audio
    )

def audio_callback(indata, frames, time_info, status):
    if status:
        print(status)
    mono = indata.mean(axis=1)
    audio_q.put(mono.copy())

print("🔊 Capturing SYSTEM AUDIO via Stereo Mix (callback mode)")
print("⏹ Press Ctrl+C to stop\n")

try:
    with sd.InputStream(
        device=DEVICE_INDEX,
        samplerate=DEVICE_SR,
        channels=2,
        callback=audio_callback,
        dtype="float32",
        blocksize=int(DEVICE_SR * CHUNK_SEC)
    ):
        while True:
            audio = audio_q.get()
            energy = np.abs(audio).mean()
            print(f"🔊 Energy: {energy:.5f}")

            if energy < ENERGY_THRESHOLD:
                continue

            buffer.append(audio)

            total_len = sum(len(b) for b in buffer)
            if total_len < DEVICE_SR * CHUNK_SEC:
                continue

            full_audio = np.concatenate(buffer)
            buffer.clear()

            # Resample to 16k
            full_audio = resample(full_audio, DEVICE_SR, TARGET_SR)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                wav.write(f.name, TARGET_SR, full_audio.astype(np.float32))
                path = f.name

            print("🧠 Transcribing...")
            result = model.transcribe(path, fp16=False)
            os.remove(path)

            text = result["text"].strip()
            if text:
                print(f"\n📝 {text}\n")

except KeyboardInterrupt:
    print("\n🛑 Live transcription stopped.")
