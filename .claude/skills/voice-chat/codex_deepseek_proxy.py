"""Codex DeepSeek Proxy — OpenAI Responses API ↔ DeepSeek Chat API
Usage:
  1. set DEEPSEEK_API_KEY=sk-xxx
  2. py codex_deepseek_proxy.py          # Start proxy on port 4000
  3. codex --config model_provider.deepseek_proxy.base_url=http://localhost:4000/v1
"""
import json, http.server, socketserver, urllib.request, sys, os, re

PORT = 4000
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", "")

MODEL_MAP = {
    "gpt-4": "deepseek-chat",
    "gpt-3.5": "deepseek-chat",
    "codex": "deepseek-chat",
    "default": "deepseek-chat",
}


def extract_text(block):
    """Extract text from various input formats"""
    if isinstance(block, str):
        return block
    if isinstance(block, dict):
        if block.get("type") == "input_text":
            return block.get("text", "")
        if block.get("type") == "message":
            content = block.get("content", "")
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                return " ".join(extract_text(c) for c in content)
        if "text" in block:
            return block["text"]
    return ""


def translate_request(body):
    """Responses API → Chat Completions"""
    model = body.get("model", "default")
    model = MODEL_MAP.get(model, model)

    # Build messages from input
    messages = []
    instructions = body.get("instructions", "")
    if instructions:
        messages.append({"role": "system", "content": instructions})

    user_input = body.get("input", "")
    if isinstance(user_input, list):
        for item in user_input:
            role = item.get("role", "user") if isinstance(item, dict) else "user"
            content = extract_text(item)
            if content:
                messages.append({"role": role, "content": content})
    elif isinstance(user_input, str) and user_input:
        messages.append({"role": "user", "content": user_input})

    # Include conversation history if present
    for msg in body.get("previous_response", []):
        role = msg.get("role", "user") if isinstance(msg, dict) else "user"
        content = extract_text(msg)
        if content:
            messages.append({"role": role, "content": content})

    if not messages:
        messages.append({"role": "user", "content": "Hello"})

    return {
        "model": model,
        "messages": messages,
        "stream": False,
        "max_tokens": body.get("max_output_tokens", 8192),
        "temperature": body.get("temperature", 0.7),
    }


def translate_response(ds_resp, original_body):
    """Chat Completions → Responses API"""
    choice = ds_resp.get("choices", [{}])[0]
    msg = choice.get("message", {})
    usage = ds_resp.get("usage", {})

    return {
        "id": f"resp_{ds_resp.get('id', 'unknown')}",
        "object": "response",
        "model": original_body.get("model", "deepseek-chat"),
        "status": "completed",
        "output": [{
            "id": f"msg_{ds_resp.get('id', 'unknown')}",
            "type": "message",
            "role": "assistant",
            "content": [{"type": "output_text", "text": msg.get("content", "")}],
            "status": "completed"
        }],
        "usage": {
            "input_tokens": usage.get("prompt_tokens", 0),
            "output_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0)
        }
    }


class Handler(http.server.BaseHTTPRequestHandler):
    timeout = 300

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        print(f"[proxy] POST {self.path} model={body.get('model','?')}", file=sys.stderr, flush=True)

        try:
            ds_body = translate_request(body)
            req = urllib.request.Request(
                DEEPSEEK_URL,
                data=json.dumps(ds_body).encode(),
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_KEY}"}
            )
            resp = urllib.request.urlopen(req, timeout=300)
            ds_resp = json.loads(resp.read())
            result = translate_response(ds_resp, body)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            print(f"[proxy] OK tokens={result['usage']['total_tokens']}", file=sys.stderr, flush=True)
        except Exception as e:
            print(f"[proxy] ERROR: {e}", file=sys.stderr, flush=True)
            self.send_response(500)
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "deepseek_key": bool(DEEPSEEK_KEY)}).encode())

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    if not DEEPSEEK_KEY:
        print("ERROR: 请先设置环境变量 DEEPSEEK_API_KEY=sk-xxx", file=sys.stderr)
        print("然后在另一个终端运行: codex", file=sys.stderr)
        sys.exit(1)

    print(f"Codex DeepSeek Proxy running on http://127.0.0.1:{PORT}", file=sys.stderr)
    print(f"Codex config: --config model_provider.deepseek_proxy.base_url=http://localhost:{PORT}/v1", file=sys.stderr)
    server = socketserver.ThreadingTCPServer(("127.0.0.1", PORT), Handler)
    server.socket.settimeout(300)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
