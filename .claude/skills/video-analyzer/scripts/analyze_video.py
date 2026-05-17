#!/usr/bin/env python3
"""Video Analyzer — route video through 豆包 (Doubao) multimodal API.

Usage:
    python analyze_video.py <video_url> [--prompt "..."]
    python analyze_video.py --file <local_path> [--prompt "..."]

For local files, upload to 0x0.st first (free, no auth needed).
For URLs, pass directly to 豆包.
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

API_KEY = "ark-bc9c6af0-1813-4842-ae3f-0614d354c375-98727"
API_BASE = "https://ark.cn-beijing.volces.com/api/v3"
MODEL = os.environ.get("DOUBAO_VISION_MODEL", "doubao-seed-2-0-mini-260428")

DEFAULT_PROMPT = """Analyze this video and return a structured markdown report.

ACCURACY RULES:
1. Only report what is ACTUALLY in the video. Do not infer or guess.
2. NEVER invent presenter names, voiceovers, or dialogue. If uncertain, say so.
3. If the audio track is silent or has no speech, say "No speech detected."
4. Label inferences with "(inferred)".

## Top-Level Summary
2-3 sentence overview of what actually happens.

## Scene-by-Scene Breakdown
MM:SS timestamps for each distinct scene. Describe on-screen content, actions, visible text.

## Audio
Report only what you actually hear. Valid: silent, ambient only, or verbatim transcript with timestamps.

## Visual Details
On-screen text, UI elements, branding, people (describe, don't name).

## Key Moments
3-7 timestamped highlights. Format: [MM:SS] Description."""


def upload_to_temp(url_path):
    """Upload a local file to 0x0.st for temporary public access."""
    path = Path(url_path).expanduser().resolve()
    if not path.exists():
        print(f"ERROR: File not found: {path}", file=sys.stderr)
        sys.exit(1)

    print(f"[info] Uploading {path.name} ({path.stat().st_size / 1024 / 1024:.1f} MB)...", file=sys.stderr)
    result = subprocess.run(
        ["curl", "-s", "-F", f"file=@{path}", "https://0x0.st"],
        capture_output=True, text=True, timeout=120
    )
    url = result.stdout.strip()
    if not url.startswith("http"):
        print(f"ERROR: Upload failed: {result.stderr or url}", file=sys.stderr)
        sys.exit(1)
    print(f"[info] Uploaded: {url}", file=sys.stderr)
    return url


def analyze(video_url, prompt, max_retries=3):
    payload = {
        "model": MODEL,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "video_url", "video_url": {"url": video_url}},
                {"type": "text", "text": prompt},
            ]
        }],
        "max_tokens": 2000,
    }

    req = Request(
        f"{API_BASE}/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"},
    )

    for attempt in range(max_retries):
        try:
            resp = urlopen(req, timeout=180)
            data = json.loads(resp.read().decode())
            return data["choices"][0]["message"]["content"]
        except HTTPError as e:
            body = e.read().decode()
            err = json.loads(body).get("error", {}).get("message", body[:200])
            if attempt < max_retries - 1:
                print(f"[warn] Retry {attempt+1}: {err}", file=sys.stderr)
                time.sleep(3)
            else:
                print(f"ERROR: {err}", file=sys.stderr)
                sys.exit(1)
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(3)
            else:
                raise


def main():
    parser = argparse.ArgumentParser(description="Analyze a video with 豆包 API.")
    parser.add_argument("input", help="Video URL or local file path (with --file)")
    parser.add_argument("--file", action="store_true", help="Input is a local file")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT, help="Custom analysis prompt")
    parser.add_argument("--model", default=MODEL, help="Model ID")
    args = parser.parse_args()

    global MODEL
    MODEL = args.model

    if args.file:
        video_url = upload_to_temp(args.input)
    elif args.input.startswith("http"):
        video_url = args.input
    else:
        print("ERROR: Input must be a URL or use --file for local files.", file=sys.stderr)
        sys.exit(1)

    print(f"[info] Analyzing with {MODEL}...", file=sys.stderr)
    result = analyze(video_url, args.prompt)
    print(result)


if __name__ == "__main__":
    main()
