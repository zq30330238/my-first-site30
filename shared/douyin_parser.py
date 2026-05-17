"""Douyin link parser — resolve short links, download video, analyze via Doubao Vision.

Full pipeline: 短链→重定向→提取视频ID→下载mp4→base64→豆包解析

Usage:
  python shared/douyin_parser.py <douyin_url> [prompt]
  python shared/douyin_parser.py --video-file <mp4_path> [prompt]  # 直接分析本地视频
"""

import sys, json, re, time, base64
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parent.parent
API_KEY = "ark-bc9c6af0-1813-4842-ae3f-0614d354c375-98727"
API_BASE = "https://ark.cn-beijing.volces.com/api/v3"
MODEL = "doubao-seed-2-0-mini-260428"


def resolve_short_link(short_url):
    """Follow v.douyin.com redirect to get video ID from landing URL."""
    req = Request(short_url, headers={
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
    })
    try:
        resp = urlopen(req, timeout=15)
        return resp.geturl()
    except HTTPError as e:
        if e.code in (301, 302):
            return e.headers.get("Location", "")
        raise


def extract_video_id(url):
    for p in [r'/video/(\d+)', r'modal_id=(\d+)', r'aweme_id=(\d+)', r'/note/(\d+)']:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None


def download_video_from_cdn(cdn_url, output_path):
    """Download video from Douyin CDN with proper Referer."""
    req = Request(cdn_url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.douyin.com/",
    })
    resp = urlopen(req, timeout=120)
    total = int(resp.headers.get("Content-Length", 0))
    downloaded = 0
    with open(output_path, "wb") as f:
        while True:
            chunk = resp.read(65536)
            if not chunk:
                break
            f.write(chunk)
            downloaded += len(chunk)
    return downloaded


def analyze_video_base64(video_path, prompt="详细解析这个视频的内容"):
    """Encode video as base64 data URL and send to Doubao Vision API."""
    with open(video_path, "rb") as f:
        video_b64 = base64.b64encode(f.read()).decode()

    data_url = f"data:video/mp4;base64,{video_b64}"

    payload = {
        "model": MODEL,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "video_url", "video_url": {"url": data_url}},
                {"type": "text", "text": prompt},
            ]
        }],
        "max_tokens": 2000,
    }

    req = Request(
        f"{API_BASE}/chat/completions",
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
        },
    )

    for attempt in range(3):
        try:
            resp = urlopen(req, timeout=300)
            data = json.loads(resp.read().decode())
            return {
                "text": data["choices"][0]["message"]["content"],
                "tokens": data.get("usage", {}),
            }
        except Exception as e:
            if attempt < 2:
                time.sleep(5)
            else:
                raise
    return None


def analyze_standalone(douyin_url, prompt=None):
    """Full pipeline as standalone script (best-effort)."""
    print("Step 1/3: Resolving Douyin link...", flush=True)
    resolved = resolve_short_link(douyin_url)
    vid = extract_video_id(resolved)
    if not vid:
        return {"error": f"Cannot extract video ID from: {resolved}"}
    print(f"  Video ID: {vid}", flush=True)
    print(f"  Page: https://www.douyin.com/video/{vid}", flush=True)

    print("\nStep 2/3: Getting video CDN URL...", flush=True)
    print("  (Requires Chrome DevTools MCP for cookie-based API access)", flush=True)
    print("  Open https://www.douyin.com/video/{vid} in Chrome,", flush=True)
    print("  then use DevTools to capture the aweme/detail API response.", flush=True)
    print("  Extract play_addr.url_list[0] as the CDN URL.", flush=True)
    print(f"\n  Or run: yt-dlp --cookies-from-browser chrome \"{douyin_url}\"", flush=True)

    return {
        "video_id": vid,
        "page_url": f"https://www.douyin.com/video/{vid}",
        "status": "manual_step_needed",
        "hint": "CDN URL requires browser cookies. Use Chrome DevTools or yt-dlp."
    }


def analyze_from_cdn_url(cdn_url, prompt=None):
    """Analyze video given a CDN URL (from Chrome DevTools interception)."""
    info = {"mp4_url": cdn_url}

    print("Downloading video from CDN...", flush=True)
    tmp_path = ROOT / "douyin_video_tmp.mp4"
    try:
        size = download_video_from_cdn(cdn_url, str(tmp_path))
        print(f"  Downloaded: {size/1024:.0f} KB", flush=True)
        info["size_kb"] = size // 1024
    except Exception as e:
        return {"error": f"Download failed: {e}"}

    if not prompt:
        prompt = "详细解析这个抖音视频的内容。请分析: 1.视频画面内容 2.旁白/话术 3.核心步骤/知识点"

    print("Analyzing via Doubao Vision...", flush=True)
    result = analyze_video_base64(str(tmp_path), prompt)
    tmp_path.unlink(missing_ok=True)

    if not result:
        return {"error": "Doubao Vision API failed"}

    return {
        "video_info": info,
        "analysis": result["text"],
        "tokens": result["tokens"],
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python douyin_parser.py <douyin_url> [prompt]")
        print("       python douyin_parser.py --video-file <mp4_path> [prompt]")
        print("       python douyin_parser.py --cdn <cdn_url> [prompt]")
        sys.exit(1)

    if sys.argv[1] == "--video-file":
        if len(sys.argv) < 3:
            print("Error: --video-file requires a path")
            sys.exit(1)
        video_path = sys.argv[2]
        prompt = sys.argv[3] if len(sys.argv) > 3 else None
        print(f"Analyzing local video: {video_path}", flush=True)
        result = analyze_video_base64(video_path, prompt)
        if result:
            print(f"[Tokens: {result['tokens'].get('total', '?')}]")
            print(result["text"])
        else:
            print("ERROR: Analysis failed")
            sys.exit(1)

    elif sys.argv[1] == "--cdn":
        if len(sys.argv) < 3:
            print("Error: --cdn requires a CDN URL")
            sys.exit(1)
        cdn_url = sys.argv[2]
        prompt = sys.argv[3] if len(sys.argv) > 3 else None
        result = analyze_from_cdn_url(cdn_url, prompt)
        if "error" in result:
            print(f"ERROR: {result['error']}")
            sys.exit(1)
        print(f"\n[Tokens: {result['tokens'].get('total', '?')}]")
        print("=" * 50)
        print(result["analysis"])
        print("=" * 50)
        out = {"source": cdn_url, "video_info": result["video_info"], "analysis": result["analysis"]}
        (ROOT / "douyin_analysis_result.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
        print("Saved to: douyin_analysis_result.json")

    else:
        douyin_url = sys.argv[1]
        prompt = sys.argv[2] if len(sys.argv) > 2 else None
        result = analyze_standalone(douyin_url, prompt)
        if "error" in result:
            print(f"ERROR: {result['error']}")
            sys.exit(1)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print(f"\nNext: open {result['page_url']} in Chrome, capture CDN URL from DevTools Network tab,")
        print(f"then run: python shared/douyin_parser.py --cdn <cdn_url>")
