"""Vosk transcription daemon - keeps model loaded, transcribes audio on demand"""
import json, sys, os, time, http.server, socketserver

VOSK_MODEL = r"C:\Users\Administrator\AppData\Local\Temp\vosk-model-cn"
PORT = 9877

if not os.path.exists(VOSK_MODEL):
    print(f"Model not found: {VOSK_MODEL}")
    sys.exit(1)

import vosk
print("Loading Vosk model (once)...")
model = vosk.Model(VOSK_MODEL)
print(f"Model loaded. Listening on port {PORT}")


class Handler(http.server.BaseHTTPRequestHandler):
    # Long timeout for large audio files
    timeout = 600

    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "model": os.path.basename(VOSK_MODEL)}).encode())

    def do_POST(self):
        if self.path == "/transcribe":
            length = int(self.headers.get("Content-Length", 0))
            if length < 1000:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({"error": "audio too short"}).encode())
                return

            print(f"Transcribing {length/1000:.0f}KB audio...", file=sys.stderr, flush=True)
            t0 = time.time()
            audio_data = self.rfile.read(length)

            rec = vosk.KaldiRecognizer(model, 16000)
            chunk_size = 4000
            text = ""
            for i in range(0, len(audio_data), chunk_size):
                chunk = audio_data[i:i+chunk_size]
                if rec.AcceptWaveform(chunk):
                    r = json.loads(rec.Result())
                    text += r.get("text", "")
            final = json.loads(rec.FinalResult())
            text += final.get("text", "")
            text = text.strip()

            elapsed = time.time() - t0
            print(f"Done in {elapsed:.1f}s: {text[:80]}...", file=sys.stderr, flush=True)

            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({"text": text}, ensure_ascii=False).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    server = socketserver.ThreadingTCPServer(("127.0.0.1", PORT), Handler)
    server.socket.settimeout(600)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
