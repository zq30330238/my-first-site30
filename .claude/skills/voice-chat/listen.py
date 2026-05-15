"""Push-to-talk voice input - hold Ctrl to record, release to send"""
import sys, json, os, time, urllib.request, subprocess, tempfile, threading

import pyaudio
import vosk
from pynput import keyboard

MODEL_PATH = r"C:\Users\Administrator\AppData\Local\Temp\vosk-model-cn"
BRIDGE = "http://127.0.0.1:9876"
SAMPLE_RATE = 16000

def trigger_claude():
    """Send '.' + Enter to trigger Claude in current VS Code window"""
    try:
        ps = 'Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait(".{ENTER}")'
        subprocess.run(["powershell", "-Command", ps], capture_output=True, timeout=3)
    except Exception:
        pass

if not os.path.exists(MODEL_PATH):
    print(f"Model not found: {MODEL_PATH}")
    sys.exit(1)

model = vosk.Model(MODEL_PATH)

audio = pyaudio.PyAudio()
frames = []
recording = False
stream = None

def start_recording():
    global stream, frames, recording
    if recording:
        return
    frames = []
    recording = True
    stream = audio.open(format=pyaudio.paInt16, channels=1, rate=SAMPLE_RATE, input=True, frames_per_buffer=1024)
    print("\n>>> Recording... (release Ctrl to send)")
    sys.stdout.flush()

def stop_recording():
    global stream, frames, recording
    if not recording:
        return
    recording = False
    stream.stop_stream()
    stream.close()
    stream = None

    if len(frames) < 10:
        print(">>> Too short, ignored")
        return

    # Transcribe directly from memory (skip WAV file I/O)
    raw = b"".join(frames)
    rec = vosk.KaldiRecognizer(model, SAMPLE_RATE)

    text = ""
    chunk_size = 4000
    for i in range(0, len(raw), chunk_size):
        chunk = raw[i:i+chunk_size]
        if rec.AcceptWaveform(chunk):
            r = json.loads(rec.Result())
            text += r.get("text", "")

    final = json.loads(rec.FinalResult())
    text += final.get("text", "")
    text = text.strip()

    if text and len(text.replace(" ", "")) >= 2:
        print(f">>> Recognized: {text}")
        try:
            # Send to bridge
            req_data = json.dumps({"text": text}).encode()
            req = urllib.request.Request(BRIDGE + "/speech", data=req_data, headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req)
            print(">>> Sent. Triggering Claude...")
            time.sleep(0.2)
            trigger_claude()
        except Exception as e:
            print(f">>> Error: {e}")
    else:
        print(">>> No valid speech detected")

def record_loop():
    global frames, recording
    while True:
        if recording and stream:
            try:
                data = stream.read(1024, exception_on_overflow=False)
                frames.append(data)
            except Exception:
                pass
        else:
            time.sleep(0.05)

recorder_thread = threading.Thread(target=record_loop, daemon=True)
recorder_thread.start()

def on_press(key):
    if key == keyboard.Key.ctrl_l:
        start_recording()

def on_release(key):
    if key == keyboard.Key.ctrl_l:
        stop_recording()

print("=" * 50)
print("Push-to-Talk Voice Input")
print("HOLD LEFT CTRL to speak, RELEASE to send")
print("=" * 50)

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
