"""语音桥接服务 - Edge TTS 云飏男声 + 抖音解析"""
import http.server, json, os, re, sys, time, threading, subprocess, tempfile, ctypes, urllib.parse

ROOT = os.path.dirname(os.path.abspath(__file__))
PYTHON = r"C:\Program Files\Python312\python.exe"
sys.path.insert(0, ROOT)
TTS_MP3 = os.path.join(tempfile.gettempdir(), "claude-voice-chat.mp3")
TTS_TXT = os.path.join(tempfile.gettempdir(), "claude-tts-chat.txt")

state = {
    "pending_speech": "",
    "speech_time": 0,
    "response": "",
    "response_time": 0,
    "lock": threading.Lock()
}

def speak_tts(text):
    text = text.replace("\n", " ").strip()
    if not text:
        return
    if os.path.exists(TTS_MP3):
        try:
            os.remove(TTS_MP3)
        except Exception:
            pass
    with open(TTS_TXT, "w", encoding="utf-8") as f:
        f.write(text)
    result = subprocess.run([
        PYTHON, "-m", "edge_tts",
        "--voice", "zh-CN-YunyangNeural",
        "--rate", "+15%",
        "-f", TTS_TXT,
        "--write-media", TTS_MP3
    ], capture_output=True, timeout=30)
    if result.returncode != 0 or not os.path.exists(TTS_MP3) or os.path.getsize(TTS_MP3) == 0:
        return
    ctypes.windll.winmm.mciSendStringW("close ttsaudio", None, 0, None)
    cmd = f'open "{TTS_MP3}" type mpegvideo alias ttsaudio'
    ctypes.windll.winmm.mciSendStringW(cmd, None, 0, None)
    ctypes.windll.winmm.mciSendStringW("play ttsaudio wait", None, 0, None)

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def _json(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def do_POST(self):
        if self.path == "/speech":
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length))
            text = data.get("text", "").strip()
            if text:
                with state["lock"]:
                    state["pending_speech"] = text
                    state["speech_time"] = time.time()
            self._json(200, {"ok": True})
        elif self.path == "/response":
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length))
            text = data.get("text", "").strip()
            if text:
                with state["lock"]:
                    state["response"] = text
                    state["response_time"] = time.time()
                threading.Thread(target=speak_tts, args=(text,), daemon=True).start()
            self._json(200, {"ok": True})
        else:
            self.send_error(404)

    def do_GET(self):
        if self.path == "/poll":
            with state["lock"]:
                resp = state["response"]
                resp_time = state["response_time"]
            if resp and (time.time() - resp_time) < 30:
                self._json(200, {"text": resp})
            else:
                self._json(204, {"text": ""})
        elif self.path == "/pending-speech":
            with state["lock"]:
                speech = state["pending_speech"]
                speech_time = state["speech_time"]
            if speech and (time.time() - speech_time) < 120:
                self._json(200, {"text": speech, "time": speech_time})
            else:
                self._json(204, {"text": ""})
        elif self.path == "/ack-speech":
            with state["lock"]:
                state["pending_speech"] = ""
                state["speech_time"] = 0
            self._json(200, {"ok": True})

        elif self.path.startswith("/parse-douyin"):
            qs = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(qs)
            url = params.get("url", [""])[0]
            if url:
                try:
                    from douyin_parser import parse_douyin
                    info = parse_douyin(url)
                    self._json(200, info)
                except Exception as e:
                    self._json(500, {"error": str(e)})
            else:
                self._json(400, {"error": "url required"})

        else:
            super().do_GET()

    def log_message(self, format, *args):
        pass

httpd = http.server.HTTPServer(("127.0.0.1", 9876), Handler)
httpd.serve_forever()
