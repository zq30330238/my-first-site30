"""Fetch Douyin/TikTok video content using browser cookies."""
import requests, re, json, sys
from urllib.parse import unquote

COOKIE_FILE = "d:/AI网站文件夹/shared/.douyin_cookie"

def get_cookie():
    try:
        return open(COOKIE_FILE).read().strip()
    except FileNotFoundError:
        print("ERROR: Cookie file not found. Run save_cookie first.")
        sys.exit(1)

def save_cookie(cookie_str):
    open(COOKIE_FILE, "w").write(cookie_str)
    print("Cookie saved.")

def fetch_video_page(video_id):
    cookie = get_cookie()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Cookie": cookie,
        "Referer": "https://www.douyin.com/",
    }
    url = f"https://www.douyin.com/video/{video_id}"
    r = requests.get(url, headers=headers, timeout=15)
    r.raise_for_status()
    return r.text

def extract_video_info(html):
    info = {}

    # Title from page title
    title_m = re.search(r"<title>([^<]+)</title>", html)
    if title_m:
        title = title_m.group(1).replace(" - 抖音", "").strip()
        info["title"] = title

    # Description from meta
    desc_m = re.search(r'name="description"[^>]*content="([^"]+)"', html)
    if desc_m:
        info["description"] = desc_m.group(1)[:200]

    # Extract from RENDER_DATA
    scripts = re.findall(r'<script[^>]*id="RENDER_DATA"[^>]*>(.*?)</script>', html, re.DOTALL)
    if scripts:
        data_str = unquote(scripts[0])
        data = json.loads(data_str)
        # Search for video info recursively
        info.update(extract_from_data(data))

    # Try internal API directly
    video_id_match = re.search(r"video/(\d+)", html)
    if video_id_match:
        aweme_id = video_id_match.group(1)

    return info

def extract_from_data(data, depth=0):
    if depth > 6:
        return {}
    result = {}
    if isinstance(data, dict):
        for k, v in data.items():
            if k in ("desc", "nickname", "uniqueId", "commentCount",
                     "playCount", "shareCount", "collectCount", "likeCount"):
                result[k] = v
            elif isinstance(v, (dict, list)):
                result.update(extract_from_data(v, depth + 1))
    elif isinstance(data, list):
        for item in data:
            result.update(extract_from_data(item, depth + 1))
    return result

def fetch_video(video_id=None, url=None):
    if url:
        # Extract ID from URL
        m = re.search(r"video/(\d+)", url)
        if m:
            video_id = m.group(1)
        else:
            # Resolve short link
            r = requests.head(url, allow_redirects=True, timeout=15)
            m = re.search(r"video/(\d+)", r.url)
            if m:
                video_id = m.group(1)
    if not video_id:
        print("ERROR: Could not extract video ID")
        return {}

    html = fetch_video_page(video_id)
    info = extract_video_info(html)
    return info

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python douyin_fetch.py <video_id_or_url>")
        sys.exit(1)

    target = sys.argv[1]
    vid = target if target.isdigit() else None
    result = fetch_video(video_id=vid, url=None if vid else target)
    for k, v in result.items():
        print(f"{k}: {v}")
