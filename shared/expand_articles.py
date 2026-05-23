"""Expand short articles via DeepSeek API. Runs on Hengchuang server overnight."""
import os
import re
import json
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

ROOT = Path(__file__).resolve().parent.parent
API_URL = "https://api.deepseek.com/anthropic/v1/messages"
API_TOKEN = os.environ.get("DEEPSEEK_API_KEY", "")

SHORT_ARTICLES = [
    "sub-healthy/article-2.html",
    "sub-healthy/article-3.html",
    "sub-healthy/article-6.html",
]

SYSTEM_PROMPT = """You are a professional English content writer for SEO-optimized pet/health websites.
Your task: expand a short article to 1000-1500 words total.

RULES:
1. Keep ALL existing HTML structure intact - every tag, class, attribute, script, meta tag, schema JSON-LD, navigation, footer - everything outside the article content area stays EXACTLY as-is.
2. Only expand the text content between paragraphs (<p>...</p>), list items (<li>...</li>), and blockquotes within the article-content div.
3. Keep ALL existing <h2> headings exactly as they are - preserve their text and order.
4. You may add new <h3> sub-headings under existing <h2> sections to better organize expanded content.
5. You may add additional <p> paragraphs, <ul>/<ol> lists, and <blockquote> callouts to expand each section.
6. Writing style: professional, authoritative, practical. Use specific data, examples, and actionable advice. No fluff.
7. Format: Output the COMPLETE article HTML file - from <!DOCTYPE html> to </html>. Do not truncate.
8. Target: 1000-1500 words for the article body content."""

def call_api(full_html, article_path):
    user_msg = f"""Article file: {article_path}

COMPLETE HTML FILE:
{full_html}

Please expand the article body content to 1000-1500 words. Keep everything else identical. Output the complete HTML file."""

    payload = {
        "model": "deepseek-v4-pro",
        "max_tokens": 16384,
        "temperature": 0.7,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": user_msg}],
    }

    req = Request(
        API_URL,
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_TOKEN}",
        },
    )

    for attempt in range(3):
        try:
            resp = urlopen(req, timeout=180)
            data = json.loads(resp.read().decode())
            # DeepSeek uses Anthropic-compatible format: content is array of blocks
            text_blocks = [b["text"] for b in data["content"] if b["type"] == "text"]
            content = "\n".join(text_blocks)
            # Extract just the HTML part if wrapped in markdown
            if content.startswith("```html"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            # Find <!DOCTYPE html> start
            doctype_idx = content.find("<!DOCTYPE html>")
            if doctype_idx > 0:
                content = content[doctype_idx:]
            # Find </html> end
            html_end = content.rfind("</html>")
            if html_end > 0:
                content = content[:html_end + 7]
            return content
        except (URLError, HTTPError) as e:
            print(f"  Attempt {attempt+1} failed: {e}")
            time.sleep(5)
    return None

def count_words(html):
    start = re.search(r'class="[^"]*article-content[^"]*"[^>]*>', html)
    if not start:
        return 0
    pos = start.end()
    depth = 1
    while depth > 0 and pos < len(html):
        next_open = html.find('<div', pos)
        next_close = html.find('</div>', pos)
        if next_close == -1:
            break
        if next_open != -1 and next_open < next_close:
            depth += 1
            pos = next_open + 4
        else:
            depth -= 1
            if depth == 0:
                inner = html[start.end():next_close]
                text = re.sub(r'<[^>]+>', ' ', inner)
                text = re.sub(r'\s+', ' ', text).strip()
                return len(text.split())
            pos = next_close + 6
    return 0

def log(msg):
    print(msg, flush=True)

def main():
    results = {"expanded": [], "failed": [], "skipped": []}

    for art in SHORT_ARTICLES:
        filepath = ROOT / art
        if not filepath.exists():
            log(f"SKIP {art}: file not found")
            results["skipped"].append(art)
            continue

        original = filepath.read_text(encoding="utf-8")
        wc_before = count_words(original)

        if wc_before >= 800:
            log(f"SKIP {art}: already {wc_before} words (>= 800)")
            results["skipped"].append(art)
            continue

        log(f"EXPANDING {art}: {wc_before} words → target 1000+")
        expanded = call_api(original, art)

        if not expanded:
            log(f"FAIL {art}: API call failed after 3 attempts")
            results["failed"].append(art)
            continue

        # Validate
        if not expanded.startswith("<!DOCTYPE html>") or not expanded.strip().endswith("</html>"):
            log(f"FAIL {art}: output doesn't start/end with proper HTML")
            results["failed"].append(art)
            continue

        wc_after = count_words(expanded)
        if wc_after < 800:
            log(f"FAIL {art}: expanded only to {wc_after} words (still < 800)")
            results["failed"].append(art)
            continue

        filepath.write_text(expanded, encoding="utf-8")
        log(f"OK {art}: {wc_before} → {wc_after} words")
        results["expanded"].append(art)

        # Rate limit
        time.sleep(2)

    log(f"\n=== SUMMARY ===")
    log(f"Expanded: {len(results['expanded'])}")
    log(f"Failed: {len(results['failed'])}")
    log(f"Skipped: {len(results['skipped'])}")

    if results["failed"]:
        log(f"Failed articles: {results['failed']}")

    # Auto commit + push if any expanded
    if results["expanded"]:
        log("\n=== AUDIT ===")
        import subprocess
        audit = subprocess.run(
            ["python3", str(ROOT / "shared" / "pre_commit_audit.py")],
            capture_output=True, text=True, cwd=str(ROOT)
        )
        log(audit.stdout)
        if audit.stderr:
            log(audit.stderr)

        if audit.returncode == 0:
            log("=== COMMIT + PUSH ===")
            for art in results["expanded"]:
                subprocess.run(["git", "add", art], cwd=str(ROOT), capture_output=True)
            msg = 'expand: {} articles to 1000+ words'.format(len(results['expanded']))
            subprocess.run(["git", "commit", "-m", msg],
                cwd=str(ROOT), capture_output=True)
            push = subprocess.run(["git", "push", "origin", "master"],
                cwd=str(ROOT), capture_output=True, text=True)
            log(push.stdout.strip())
            if push.stderr:
                log(push.stderr.strip())
            log("Done. GitHub Actions will auto-deploy.")
        else:
            log("Audit failed, skipping commit. Fix issues first.")

    return 0 if not results["failed"] else 1

if __name__ == "__main__":
    sys.exit(main())
