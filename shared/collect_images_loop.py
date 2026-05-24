#!/usr/bin/env python3
"""24/7 image collection pipeline for anime/game character PNGs.

Searches free PNG sites, verifies with Doubao vision API, saves to collected/.
Designed to run continuously on the server (Debian, Python 3.11).

Usage:
  python shared/collect_images_loop.py                    # normal run, resume from progress
  python shared/collect_images_loop.py --reset            # reset progress, start over
  python shared/collect_images_loop.py --gen-targets      # only generate targets.json

Directory structure:
  collected/<site>/<character_slug>.png      # verified images
  shared/logs/collect_images.log             # log file
  shared/collect_progress.json               # progress state (resume support)
  shared/collect_targets.json                # generated target list

Dependencies: requests (pip install requests)
"""

import sys, json, time, hashlib, signal, random, logging, re, io
from pathlib import Path
from typing import Optional
from datetime import datetime, date
from urllib.parse import quote, urljoin, urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

try:
    import cloudscraper
    HAS_CLOUDSCRAPER = True
except ImportError:
    HAS_CLOUDSCRAPER = False

try:
    from curl_cffi import requests as curl_requests
    HAS_CURL_CFFI = True
except ImportError:
    HAS_CURL_CFFI = False

try:
    from ddgs import DDGS
    HAS_DDG = True
except ImportError:
    HAS_DDG = False

# Per-source blocking state (avoids hammering CF-blocked sources)
_blocked_until = {}

def _is_blocked(src_name: str) -> bool:
    """Check if a source is in its blocked cooldown period."""
    return time.time() < _blocked_until.get(src_name, 0.0)

def _mark_blocked(src_name: str):
    """Mark a source as blocked for BLOCK_DURATION seconds."""
    expire = time.time() + BLOCK_DURATION
    _blocked_until[src_name] = expire
    log.warning("Source %s blocked until %s", src_name,
                datetime.fromtimestamp(expire).strftime("%H:%M:%S"))

sys.path.insert(0, str(Path(__file__).resolve().parent))
import doubao_vision

ROOT = Path(__file__).resolve().parent.parent
COLLECTED_DIR = ROOT / "collected"
LOGS_DIR = ROOT / "shared" / "logs"
PROGRESS_FILE = ROOT / "shared" / "collect_progress.json"
TARGETS_FILE = ROOT / "shared" / "collect_targets.json"
DATA_FILE = ROOT / "shared" / "anime_site_data.json"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)
DELAY_MIN = 3
DELAY_MAX = 5
MAX_CANDIDATES = 8
CHECKPOINT_INTERVAL = 10
DOWNLOAD_TIMEOUT = 30
SEARCH_TIMEOUT = 15
DETAIL_TIMEOUT = 10
BLOCK_DURATION = 300  # 5 min cooldown before retrying a blocked source

LOGS_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "collect_images.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)

shutdown_flag = False


def handle_signal(signum, frame):
    global shutdown_flag
    log.warning("Received signal %s, shutting down gracefully...", signum)
    shutdown_flag = True


signal.signal(signal.SIGTERM, handle_signal)
signal.signal(signal.SIGINT, handle_signal)


# ---------------------------------------------------------------------------
# HTTP session
# ---------------------------------------------------------------------------

def make_session():
    """Prefer curl_cffi > cloudscraper > requests for CF bypass capability."""
    if HAS_CURL_CFFI:
        try:
            s = curl_requests.Session()
            s.headers.update({"User-Agent": USER_AGENT})
            log.info("curl_cffi session created (built-in CF bypass, no extra retry wrapper)")
            return s
        except Exception as e:
            log.warning("curl_cffi init failed: %s", e)

    if HAS_CLOUDSCRAPER:
        try:
            s = cloudscraper.create_scraper(
                browser={"browser": "chrome", "platform": "windows", "mobile": False},
                delay=10,
            )
            log.info("cloudscraper session created")
            return _wrap_cf_retry(s)
        except Exception as e:
            log.warning("cloudscraper init failed: %s", e)

    s = requests.Session()
    retry = Retry(total=3, backoff_factor=1.5, status_forcelist=[429, 503, 502])
    adapter = HTTPAdapter(max_retries=retry)
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    s.headers.update({"User-Agent": USER_AGENT})
    log.info("requests session created")
    return _wrap_cf_retry(s)


def _is_cf_challenge(resp: requests.Response) -> bool:
    """Detect Cloudflare challenge/interstitial pages."""
    if resp.status_code not in (403, 503):
        return False
    text = resp.text[:3000].lower()
    return any(phrase in text for phrase in ["just a moment", "cf-browser-verify"])


def _wrap_cf_retry(session):
    """Monkey-patch session.get/post with CF challenge retry (3 attempts)."""
    _orig_get = session.get
    _orig_post = session.post

    def _retry(method, url, **kwargs):
        for attempt in range(3):
            resp = method(url, **kwargs)
            if not _is_cf_challenge(resp):
                return resp
            delay = 3 * (attempt + 1)
            log.debug("CF on %s, retry %d/2 in %ds ...", url, attempt + 1, delay)
            time.sleep(delay)
        return resp  # Last attempt — caller handles the CF response

    def _cf_get(url, **kwargs):
        return _retry(_orig_get, url, **kwargs)

    def _cf_post(url, **kwargs):
        return _retry(_orig_post, url, **kwargs)

    session.get = _cf_get
    session.post = _cf_post
    return session


# ---------------------------------------------------------------------------
# Source search functions
# ---------------------------------------------------------------------------

def _extract_png_urls(html: str, base_url: str, domain_pattern: str = None) -> list:
    """Extract PNG image URLs from HTML using multiple patterns."""
    urls = set()

    # Primary: full-text regex scan for raw PNG URLs matching the source domain
    if domain_pattern:
        full_text_pat = rf'(https?://{domain_pattern}/[^"\'<>\s]+\.png)'
        for m in re.finditer(full_text_pat, html, re.I):
            urls.add(m.group(1))

    # Secondary: attribute-based patterns
    patterns = [
        r'src="(https?://[^"]+\.png)"',
        r'src="(//[^"]+\.png)"',
        r'data-src="(https?://[^"]+\.png)"',
        r'data-src="(//[^"]+\.png)"',
        r'href="(https?://[^"]+\.png)"',
        r'href="(//[^"]+\.png)"',
        r'data-url="(https?://[^"]+\.png)"',
        r'data-image="(https?://[^"]+\.png)"',
    ]
    for pat in patterns:
        for m in re.finditer(pat, html):
            u = m.group(1)
            if u.startswith("//"):
                u = "https:" + u
            urls.add(u)

    # Filter out unwanted content
    exclude_keywords = (
        "thumbnail", "icon", "favicon", "logo", "avatar", "spacer",
        "search-bar", "search", "button", "banner", "background", "px.gif",
    )
    filtered = set()
    for u in urls:
        if not any(x in u.lower() for x in exclude_keywords):
            filtered.add(u)

    return list(filtered)


def search_pngegg(character: str, series: str, session: requests.Session) -> list:
    """Search pngegg.com — mostly full-body PNG renders."""
    if _is_blocked("pngegg"):
        return []
    query = quote(f"{character} {series}")
    results = []
    try:
        resp = session.get(
            f"https://www.pngegg.com/en/search?q={query}",
            timeout=SEARCH_TIMEOUT,
        )
        if _is_cf_challenge(resp):
            _mark_blocked("pngegg")
            return []
        if resp.status_code == 200:
            results = _extract_png_urls(resp.text, "https://www.pngegg.com", r'[a-z0-9]+\.pngegg\.com')
            # pngegg often wraps thumbnails in <a> linking to detail pages;
            # try to extract those detail page links and build direct image URLs
            for m in re.finditer(r'href="(/en/png-[^"]+)"', resp.text):
                detail_path = m.group(1)
                detail_url = f"https://www.pngegg.com{detail_path}"
                try:
                    dr = session.get(detail_url, timeout=DETAIL_TIMEOUT)
                    if dr.status_code == 200:
                        results.extend(_extract_png_urls(dr.text, detail_url, r'[a-z0-9]+\.pngegg\.com'))
                except requests.RequestException:
                    continue
    except requests.RequestException as e:
        log.warning("pngegg search error: %s", e)
    return results[:MAX_CANDIDATES]


def search_pngaaa(character: str, series: str, session: requests.Session) -> list:
    """Search pngaaa.com."""
    if _is_blocked("pngaaa"):
        return []
    query = quote(character)
    results = []
    search_urls = [
        f"https://pngaaa.com/search?q={query}",
        f"https://pngaaa.com/search/{query}",
    ]
    for search_url in search_urls:
        try:
            resp = session.get(search_url, timeout=SEARCH_TIMEOUT)
            if _is_cf_challenge(resp):
                _mark_blocked("pngaaa")
                return []
            if resp.status_code == 404:
                log.debug("pngaaa 404: %s", search_url)
                continue
            if resp.status_code != 200:
                continue
            results = _extract_png_urls(resp.text, search_url, r'[a-z0-9]+\.pngaaa\.com')
            # follow detail page links
            for m in re.finditer(r'href="(/[^"]+)"', resp.text):
                detail_url = urljoin("https://pngaaa.com", m.group(1))
                if detail_url == "https://pngaaa.com/":
                    continue
                try:
                    dr = session.get(detail_url, timeout=DETAIL_TIMEOUT)
                    if dr.status_code == 200:
                        results.extend(_extract_png_urls(dr.text, detail_url, r'[a-z0-9]+\.pngaaa\.com'))
                except requests.RequestException:
                    continue
            break  # stop after first successful search
        except requests.RequestException as e:
            log.warning("pngaaa search error on %s: %s", search_url, e)
    return results[:MAX_CANDIDATES]


def search_purepng(character: str, series: str, session: requests.Session) -> list:
    """Search purepng.com."""
    if _is_blocked("purepng"):
        return []
    query = quote(character)
    results = []
    try:
        resp = session.get(
            f"https://purepng.com/search?q={query}",
            timeout=SEARCH_TIMEOUT,
        )
        if _is_cf_challenge(resp):
            _mark_blocked("purepng")
            return []
        if resp.status_code == 200:
            results = _extract_png_urls(resp.text, "https://purepng.com", r'(?:[a-z0-9]+\.)?purepng\.com')
            for m in re.finditer(r'href="(/photo/[^"]+)"', resp.text):
                detail_url = f"https://purepng.com{m.group(1)}"
                try:
                    dr = session.get(detail_url, timeout=DETAIL_TIMEOUT)
                    if dr.status_code == 200:
                        results.extend(_extract_png_urls(dr.text, detail_url, r'(?:[a-z0-9]+\.)?purepng\.com'))
                except requests.RequestException:
                    continue
    except requests.RequestException as e:
        log.warning("purepng search error: %s", e)
    return results[:MAX_CANDIDATES]


def search_pngall(character: str, series: str, session: requests.Session) -> list:
    """Search pngall.com."""
    if _is_blocked("pngall"):
        return []
    query = quote(character)
    results = []
    try:
        resp = session.get(
            f"https://pngall.com/search?q={query}",
            timeout=SEARCH_TIMEOUT,
        )
        if _is_cf_challenge(resp):
            _mark_blocked("pngall")
            return []
        if resp.status_code == 200:
            results = _extract_png_urls(resp.text, "https://pngall.com", r'(?:www\.)?pngall\.com')
            for m in re.finditer(r'href="(/[^"]+)"', resp.text):
                detail_url = f"https://pngall.com{m.group(1)}"
                if "search" in detail_url:
                    continue
                try:
                    dr = session.get(detail_url, timeout=DETAIL_TIMEOUT)
                    if dr.status_code == 200:
                        results.extend(_extract_png_urls(dr.text, detail_url, r'(?:www\.)?pngall\.com'))
                except requests.RequestException:
                    continue
    except requests.RequestException as e:
        log.warning("pngall search error: %s", e)
    return results[:MAX_CANDIDATES]


def search_pngwing(character: str, series: str, session: requests.Session) -> list:
    """Search pngwing.com (backup — CF may block)."""
    if _is_blocked("pngwing"):
        return []
    query = quote(f"{character} PNG")
    results = []
    try:
        resp = session.get(
            f"https://pngwing.com/en/search?q={query}",
            timeout=SEARCH_TIMEOUT,
        )
        if _is_cf_challenge(resp):
            _mark_blocked("pngwing")
            return []
        if resp.status_code == 200:
            results = _extract_png_urls(resp.text, "https://pngwing.com", r'[a-z0-9]+\.pngwing\.com')
            for m in re.finditer(r'href="(/[^"]+\.html)"', resp.text):
                detail_url = f"https://pngwing.com{m.group(1)}"
                try:
                    dr = session.get(detail_url, timeout=DETAIL_TIMEOUT)
                    if dr.status_code == 200:
                        results.extend(_extract_png_urls(dr.text, detail_url, r'[a-z0-9]+\.pngwing\.com'))
                except requests.RequestException:
                    continue
    except requests.RequestException as e:
        log.warning("pngwing search error: %s", e)
    return results[:MAX_CANDIDATES]


def search_duckduckgo(character: str, series: str, session) -> list:
    """Search DuckDuckGo Images for character PNG renders. Reliable, no CF blocking."""
    if not HAS_DDG:
        return []
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.images(
                f"{character} {series} PNG render transparent",
                max_results=MAX_CANDIDATES,
            ):
                url = r.get("image", "")
                if url:
                    results.append(url)
    except Exception as e:
        log.warning("DuckDuckGo search error: %s", e)
    return results[:MAX_CANDIDATES]


def search_lol_ddragon(character: str, series: str, session: requests.Session) -> list:
    """Riot Data Dragon CDN for League of Legends champion splash arts (always available)."""
    series_lower = series.lower()
    if "league" not in series_lower and "lol" not in series_lower and "legend" not in series_lower:
        return []
    # Normalize champion name to Data Dragon filename format
    raw = character.lower().replace("'", "").replace(".", "").replace(" ", "")
    if not raw:
        return []
    champ = raw[0].upper() + raw[1:] if len(raw) > 1 else raw.upper()
    # Known naming quirks in Data Dragon
    overrides = {
        "khazix": "KhaZix",
        "velkoz": "VelKoz",
        "leblanc": "LeBlanc",
        "reksai": "RekSai",
        "chogath": "ChoGath",
        "kogmaw": "KogMaw",
        "malzahar": "Malzahar",
    }
    champ = overrides.get(raw, champ)
    return [
        f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{champ}_0.jpg",
        f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{champ}_1.jpg",
    ]


SOURCES = [
    ("ddg", search_duckduckgo),
    ("lolddragon", search_lol_ddragon),
    ("pngegg", search_pngegg),
    ("pngwing", search_pngwing),
]


# ---------------------------------------------------------------------------
# Download helpers
# ---------------------------------------------------------------------------

def download_candidate(url: str, session) -> Optional[bytes]:
    """Download image bytes. Accepts PNG, JPEG, WebP. Returns None if invalid."""
    try:
        resp = session.get(url, timeout=DOWNLOAD_TIMEOUT)
        if resp.status_code != 200:
            return None
        data = resp.content
        if len(data) < 15 * 1024:
            log.debug("  Too small: %d bytes", len(data))
            return None
        # Accept PNG, JPEG, WebP magic bytes
        valid = (
            data.startswith(b"\x89PNG") or
            data.startswith(b"\xff\xd8\xff") or
            (data.startswith(b"RIFF") and b"WEBP" in data[:12])
        )
        if not valid:
            log.debug("  Unknown format (first 4 bytes: %s)", data[:4].hex())
            return None
        return data
    except Exception as e:
        log.debug("  Download failed: %s", e)
        return None


def md5_bytes(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


# ---------------------------------------------------------------------------
# Doubao verification
# ---------------------------------------------------------------------------

def verify_with_doubao(image_bytes: bytes, character: str, series: str) -> bool:
    """Verify image with Doubao vision API. Returns True if it's a clean render."""
    tmp_dir = LOGS_DIR / ".verify_tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp_path = tmp_dir / f"verify_{int(time.time() * 1000)}_{random.randint(0, 999)}.png"
    try:
        tmp_path.write_bytes(image_bytes)
        prompt = (
            f"Is this a high-quality character image of {character} from {series}? "
            f"Answer YES only if ALL conditions are met: "
            f"(1) clearly shows {character} with correct design/colors, "
            f"(2) sharp/high-resolution, not blurry or pixelated, "
            f"(3) clean plain or transparent background, "
            f"(4) no text, watermarks, logos, or UI elements. "
            f"Answer NO if any of: screenshot, fan art, wrong character, "
            f"low resolution, murky/blurry, AI-generated look, messy background, "
            f"character too small in frame, or any text/watermark. Only answer YES or NO."
        )
        result = doubao_vision.analyze_image(str(tmp_path), prompt)
        if result:
            answer = result["text"].strip().upper()
            tokens = result["tokens"]["total"]
            log.info("  Doubao: %s  (%d tokens)", answer[:10], tokens)
            return answer.startswith("YES")
        return False
    except RuntimeError as e:
        err_msg = str(e)
        if "DOUBAO_FATAL" in err_msg or "Doubao API error" in err_msg:
            log.critical("  DOUBAO API FATAL - stopping image collection: %s", e)
            raise
        log.warning("  Doubao verify error: %s", e)
        return False
    except Exception as e:
        log.warning("  Doubao verify error: %s", e)
        return False
    finally:
        try:
            tmp_path.unlink(missing_ok=True)
        except PermissionError:
            pass


# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------

def save_image(image_bytes: bytes, site: str, slug: str) -> str:
    """Save verified image to collected/<site>/<slug>.png. Handles duplicates by suffixing."""
    dest_dir = COLLECTED_DIR / site
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / f"{slug}.png"
    new_md5 = md5_bytes(image_bytes)
    if dest_path.exists():
        existing_md5 = md5_bytes(dest_path.read_bytes())
        if existing_md5 == new_md5:
            return str(dest_path)
        counter = 1
        while dest_path.exists():
            dest_path = dest_dir / f"{slug}_{counter}.png"
            counter += 1
    dest_path.write_bytes(image_bytes)
    log.info("  Saved: %s", dest_path.name)
    return str(dest_path)


# ---------------------------------------------------------------------------
# Targets
# ---------------------------------------------------------------------------

def load_targets() -> list:
    """Load from collect_targets.json or generate from anime_site_data.json."""
    if TARGETS_FILE.exists():
        with open(TARGETS_FILE, encoding="utf-8") as f:
            return json.load(f)
    log.info("No targets file found — generating from anime_site_data.json ...")
    if not DATA_FILE.exists():
        log.error("anime_site_data.json not found at %s", DATA_FILE)
        sys.exit(1)
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)
    targets = []
    for site_key, site_data in data.items():
        series_raw = site_data.get("site_name", site_key)
        series = series_raw.replace(" Wiki", "").replace(" Database", "")
        for char in site_data.get("characters", []):
            name = char["name"]
            slug = (
                name.lower()
                .replace(" ", "-")
                .replace(".", "")
                .replace("'", "")
                .replace('"', "")
                .replace("(", "")
                .replace(")", "")
                .replace(":", "")
                .replace("!", "")
            )
            slug = re.sub(r"-+", "-", slug).strip("-")
            targets.append({
                "site": site_key,
                "character": name,
                "slug": slug,
                "series": series,
            })
    TARGETS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TARGETS_FILE, "w", encoding="utf-8") as f:
        json.dump(targets, f, indent=2, ensure_ascii=False)
    log.info("Generated %d targets from %d sites", len(targets), len(data))
    return targets


# ---------------------------------------------------------------------------
# Progress
# ---------------------------------------------------------------------------

def save_progress(index: int, stats: dict):
    data = {
        "current_index": index,
        "stats": stats,
        "updated": datetime.now().isoformat(),
    }
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_progress() -> dict:
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {
        "current_index": 0,
        "stats": {"success": 0, "failed": 0, "skipped": 0, "daily": {}},
    }


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def collect_one(target: dict, session: requests.Session, stats: dict) -> bool:
    """Process a single target. Returns True if image was collected."""
    site = target["site"]
    character = target["character"]
    slug = target["slug"]
    series = target["series"]

    log.info("  Searching sources for %s ...", character)
    all_candidates = []

    for src_name, src_fn in SOURCES:
        if shutdown_flag:
            return False
        try:
            urls = src_fn(character, series, session)
            for u in urls:
                all_candidates.append((u, src_name))
            if urls:
                log.info("    %s: %d candidate(s)", src_name, len(urls))
        except Exception as e:
            log.warning("    %s error: %s", src_name, e)
        time.sleep(random.uniform(1.0, 2.0))

    if not all_candidates:
        log.warning("  No candidates found from any source")
        stats["failed"] += 1
        return False

    # Deduplicate by URL
    seen_urls = set()
    unique_candidates = []
    for u, s in all_candidates:
        if u not in seen_urls:
            seen_urls.add(u)
            unique_candidates.append((u, s))

    for url, source in unique_candidates[:MAX_CANDIDATES]:
        if shutdown_flag:
            return False
        log.info("  Trying %s: %s ...", source, url[:100])
        # Quick keyword filter: skip URLs lacking character name tokens
        char_tokens = character.lower().replace("'", "").replace("-", " ").split()
        if not any(tok in url.lower() for tok in char_tokens if len(tok) > 2):
            log.debug("  URL lacks character keywords, skip download + doubao")
            continue
        data = download_candidate(url, session)
        if data is None:
            continue
        if verify_with_doubao(data, character, series):
            save_image(data, site, slug)
            stats["success"] += 1
            return True
        else:
            log.info("  %s: rejected by Doubao", source)
        time.sleep(random.uniform(1.0, 2.0))

    log.warning("  FAILED: %s — no valid image after all candidates", character)
    stats["failed"] += 1
    return False


def main():
    log.info("=" * 60)
    log.info("Image Collection Pipeline Starting")
    log.info("=" * 60)

    COLLECTED_DIR.mkdir(parents=True, exist_ok=True)
    targets = load_targets()
    log.info("Total targets: %d", len(targets))

    # Build set of already-collected images
    already_collected = set()
    if COLLECTED_DIR.exists():
        for site_dir in sorted(COLLECTED_DIR.iterdir()):
            if site_dir.is_dir():
                for f in site_dir.iterdir():
                    if f.suffix == ".png":
                        already_collected.add(f"{site_dir.name}/{f.stem}")
    log.info("Already collected: %d images", len(already_collected))

    progress = load_progress()
    stats = progress["stats"]
    start_idx = progress["current_index"]
    log.info("Starting from index %d", start_idx)

    session = make_session()

    for i, target in enumerate(targets):
        if i < start_idx:
            continue
        if shutdown_flag:
            log.warning("Shutdown requested — saving progress at index %d", i)
            save_progress(i, stats)
            return

        site = target["site"]
        slug = target["slug"]
        check_key = f"{site}/{slug}"

        if check_key in already_collected:
            stats["skipped"] += 1
            log.info(
                "[%d/%d] SKIP %s (%s) — already collected",
                i + 1, len(targets), target["character"], site,
            )
            continue

        log.info(
            "[%d/%d] %s from %s (%s)",
            i + 1, len(targets), target["character"], target["series"], site,
        )

        collect_one(target, session, stats)

        # Checkpoint
        if (i + 1) % CHECKPOINT_INTERVAL == 0:
            stats.setdefault("daily", {})
            stats["daily"][date.today().isoformat()] = stats["success"]
            save_progress(i + 1, stats)
            daily_total = stats["success"] + stats["failed"]
            log.info(
                "--- Checkpoint: %d/%d --- Today: %d success / %d total | "
                "All: S=%d F=%d Sk=%d ---",
                i + 1, len(targets),
                stats["daily"].get(date.today().isoformat(), 0),
                daily_total,
                stats["success"], stats["failed"], stats["skipped"],
            )

        if not shutdown_flag:
            delay = random.uniform(DELAY_MIN, DELAY_MAX)
            log.debug("Sleeping %.1fs ...", delay)
            time.sleep(delay)

    # Final
    stats.setdefault("daily", {})
    stats["daily"][date.today().isoformat()] = stats["success"]
    save_progress(len(targets), stats)
    log.info("=" * 60)
    log.info("ALL TARGETS PROCESSED")
    log.info(
        "Success=%d  Failed=%d  Skipped=%d",
        stats["success"], stats["failed"], stats["skipped"],
    )
    log.info("=" * 60)


if __name__ == "__main__":
    # --gen-targets: generate targets and exit
    if "--gen-targets" in sys.argv:
        load_targets()
        sys.exit(0)
    # --reset: delete progress file and start fresh
    if "--reset" in sys.argv:
        if PROGRESS_FILE.exists():
            PROGRESS_FILE.unlink()
            log.info("Progress file deleted — will start from beginning on next run")
        sys.exit(0)
    main()
