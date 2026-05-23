"""Call Doubao multimodal model to analyze images/videos. Used by Claude to "see" screens/photos/videos.

Usage:
  python shared/doubao_vision.py <image_path> [prompt]
  python shared/doubao_vision.py -s [prompt]                 # screenshot + analyze
  python shared/doubao_vision.py --video <mp4_url> [prompt]  # analyze public video URL
  python shared/doubao_vision.py --model <alias> <image_path> [prompt]  # use specific model
  python shared/doubao_vision.py --model <alias> --video <mp4_url> [prompt]

Models: 2.0 (default seed-2.0-lite), 1.6 (seed-1.6-flash), 1.5 (1.5-vision-pro-32k)
"""

import sys, json, base64, time, os
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

API_KEY = os.environ.get("ARK_API_KEY") or "ark-bc9c6af0-1813-4842-ae3f-0614d354c375-98727"
API_BASE = "https://ark.cn-beijing.volces.com/api/v3"
MODEL = "doubao-seed-2-0-lite-260428"
MODEL_MAP = {
    "2.0": "doubao-seed-2-0-lite-260428",
    "2.0-mini": "doubao-seed-2-0-mini-260428",
    "2.0-pro": "doubao-seed-2-0-pro-260215",
    "1.6": "doubao-seed-1-6-flash-250715",
    "1.6-vision": "doubao-seed-1-6-vision-250815",
    "1.5": "doubao-1-5-vision-pro-32k-250115",
    "1.5-new": "doubao-1.5-vision-pro-250328",
}
ROOT = Path(__file__).resolve().parent.parent


def encode_image(path):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")
    ext = path.suffix.lower()
    mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "webp": "webp", "gif": "gif"}.get(ext, "jpeg")
    b64 = base64.b64encode(path.read_bytes()).decode()
    return f"data:image/{mime};base64,{b64}"


def analyze_image(image_path, prompt="详细描述这张图片的内容"):
    data_url = encode_image(image_path)

    payload = {
        "model": MODEL,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": data_url}},
                {"type": "text", "text": prompt},
            ]
        }],
        "max_tokens": 1000,
    }

    req = Request(
        f"{API_BASE}/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"},
    )

    for attempt in range(3):
        try:
            resp = urlopen(req, timeout=120)
            data = json.loads(resp.read().decode())
            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            return {
                "text": content,
                "tokens": {
                    "prompt": usage.get("prompt_tokens", 0),
                    "completion": usage.get("completion_tokens", 0),
                    "total": usage.get("total_tokens", 0),
                }
            }
        except HTTPError as e:
            body = e.read().decode()
            err = json.loads(body).get("error", {}).get("message", body[:200])
            if attempt < 2:
                time.sleep(3)
            else:
                raise RuntimeError(f"Doubao API error after 3 attempts: {err}")
        except Exception as e:
            if attempt < 2:
                time.sleep(3)
            else:
                raise

    return None


def analyze_video(video_url, prompt="详细描述这个视频的内容，包括画面、音频、步骤和话术"):
    models_to_try = [MODEL]
    if MODEL != "doubao-seed-1-8-251228":
        models_to_try.append("doubao-seed-1-8-251228")
    if MODEL != "doubao-seed-1-6-vision-250815":
        models_to_try.append("doubao-seed-1-6-vision-250815")
    last_err = None

    for m in models_to_try:
        payload = {
            "model": m,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "video_url", "video_url": {"url": video_url}},
                    {"type": "text", "text": prompt},
                ]
            }],
            "max_tokens": 3000,
            "temperature": 0.3,
        }

        req = Request(
            f"{API_BASE}/chat/completions",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"},
        )

        for attempt in range(2):
            try:
                resp = urlopen(req, timeout=180)
                data = json.loads(resp.read().decode())
                content = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {})
                if m != MODEL:
                    print(f"  [降级] 使用 {m}", flush=True)
                return {
                    "text": content,
                    "tokens": {
                        "prompt": usage.get("prompt_tokens", 0),
                        "completion": usage.get("completion_tokens", 0),
                        "total": usage.get("total_tokens", 0),
                    }
                }
            except HTTPError as e:
                body = e.read().decode()
                err = json.loads(body).get("error", {}).get("message", body[:200])
                last_err = err
                if attempt == 0:
                    time.sleep(3)
                continue
            except Exception as e:
                last_err = str(e)
                if attempt == 0:
                    time.sleep(3)
                continue

    raise RuntimeError(f"Doubao Video API failed after all fallbacks: {last_err}")


def screenshot_and_analyze(prompt="详细描述这张截图的内容"):
    import pyautogui
    tmp = ROOT / "temp_screenshot.png"
    pyautogui.screenshot().save(str(tmp))
    result = analyze_image(str(tmp), prompt)
    tmp.unlink(missing_ok=True)
    return result


if __name__ == "__main__":
    # Parse --model flag
    model_alias = None
    for i, arg in enumerate(sys.argv[1:], 1):
        if arg == "--model" and i + 1 < len(sys.argv):
            model_alias = sys.argv[i + 1]
            sys.argv.pop(i)
            sys.argv.pop(i)
            break

    if model_alias:
        if model_alias in MODEL_MAP:
            MODEL = MODEL_MAP[model_alias]
        else:
            print(f"Warning: Unknown model alias '{model_alias}', using default {MODEL}", flush=True)

    if len(sys.argv) < 2:
        print("Usage: python doubao_vision.py <image_path> [prompt]")
        print("       python doubao_vision.py -s [prompt]")
        print("       python doubao_vision.py --video <mp4_url> [prompt]")
        print("       python doubao_vision.py --model <alias> <image_path> [prompt]")
        print("       python doubao_vision.py --model <alias> --video <mp4_url> [prompt]")
        print("Models: 2.0 (default), 1.6 (seed-1.6-flash), 1.5 (1.5-vision-pro-32k)")
        sys.exit(1)

    if sys.argv[1] == "--video":
        if len(sys.argv) < 3:
            print("Error: --video requires a URL")
            sys.exit(1)
        video_url = sys.argv[2]
        prompt = sys.argv[3] if len(sys.argv) > 3 else "详细描述这个视频的内容，包括画面、音频、步骤和话术"
        print(f"Analyzing video: {video_url[:80]}...", flush=True)
        result = analyze_video(video_url, prompt)
    elif sys.argv[1] == "-s":
        prompt = sys.argv[2] if len(sys.argv) > 2 else "详细描述这张截图的内容"
        print("Taking screenshot and analyzing...", flush=True)
        result = screenshot_and_analyze(prompt)
    else:
        prompt = sys.argv[2] if len(sys.argv) > 2 else "详细描述这张图片的内容"
        result = analyze_image(sys.argv[1], prompt)

    if result:
        print(f"[Tokens: {result['tokens']['total']} (in:{result['tokens']['prompt']} out:{result['tokens']['completion']})]")
        import io, os
        tempdir = os.environ.get('TEMP', os.environ.get('TMP', '/tmp'))
        outfile = os.path.join(tempdir, 'doubao_vision_output.txt')
        with io.open(outfile, 'w', encoding='utf-8') as f:
            f.write(result["text"])
        print(f"Result written to: {outfile}")
