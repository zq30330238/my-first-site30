---
name: video-analyzer
description: Analyzes a video file/URL with 豆包 (Doubao) multimodal API and returns a structured markdown report covering top-level summary, scene-by-scene breakdown, audio transcript, visual details, and key timestamped moments. Strong anti-hallucination guardrails.
argument-hint: <video_url_or_path> [--file] [--prompt "..."] [--model ...]
disable-model-invocation: true
allowed-tools: Bash, Read
---

# Analyze Video

Analyze a video with 豆包 (Doubao) multimodal API.

## Prerequisites

- Python 3.10+
- No external packages needed (uses stdlib `urllib`)
- 豆包 API key is hardcoded — no env var setup needed

## Usage

**Video URL (recommended):**
```bash
python d:/AI网站文件夹/.claude/skills/video-analyzer/scripts/analyze_video.py "https://example.com/video.mp4"
```

**Local file (uploads to 0x0.st first):**
```bash
python d:/AI网站文件夹/.claude/skills/video-analyzer/scripts/analyze_video.py --file "path/to/video.mp4"
```

**Custom prompt:**
```bash
python analyze_video.py "url" --prompt "Summarize this video in 3 bullet points"
```

## Steps

1. If the user provides a URL, pass it directly.
2. If the user provides a local file, use `--file` flag (uploads to 0x0.st for temp public access).
3. Run the script. Progress goes to stderr, report goes to stdout.
4. Present the markdown report to the user.

## Troubleshooting

- **Upload failed**: 0x0.st may be down — try uploading to a different temp host, or ask user for a public URL
- **API error**: Check the error message; video may be too large or format unsupported
- **Timeout**: Large videos take longer; the default timeout is 180s
- **Alternative**: Use `python shared/doubao_vision.py --video <url>` for quick analysis

## Output

A markdown report with:
- **Top-Level Summary** — 2-3 sentence overview
- **Scene-by-Scene Breakdown** — MM:SS timestamps
- **Audio** — transcript or "silent" note
- **Visual Details** — on-screen text, UI, branding
- **Key Moments** — 3-7 timestamped highlights
