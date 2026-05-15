"""监听用户语音并触发 Claude 回复的监控脚本"""
import time, json, os, urllib.request

BRIDGE = "http://127.0.0.1:9876"
SPEECH_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user-speech.txt")
RESPONSE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "claude-response.txt")
PENDING_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pending.txt")

last_mtime = 0

print("Voice monitor started. Watching for speech...")

while True:
    try:
        if os.path.exists(SPEECH_FILE):
            mtime = os.path.getmtime(SPEECH_FILE)
            if mtime > last_mtime:
                last_mtime = mtime
                with open(SPEECH_FILE, "r", encoding="utf-8") as f:
                    text = f.read().strip()
                if text:
                    # Write pending query for Claude to process
                    with open(PENDING_FILE, "w", encoding="utf-8") as f:
                        f.write(text)
                    print(f"New speech: {text[:80]}...")
    except Exception as e:
        print(f"Monitor error: {e}")

    time.sleep(2)
