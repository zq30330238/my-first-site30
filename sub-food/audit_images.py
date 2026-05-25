"""Batch audit sub-food article images: verify each matches its article title using Doubao vision API."""
import subprocess, sys, os, time, json, re
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import quote

BASE = Path(r"d:\AI网站文件夹\sub-food")
DOUBAO = Path(r"d:\AI网站文件夹\shared\doubao_vision.py")
TEMP_OUT = os.path.join(os.environ.get("TEMP", "/tmp"), "doubao_vision_output.txt")

# Extract dish name from title (remove subtitle after ": " or keep as-is)
def extract_dish(title):
    """Extract primary dish name from article title."""
    title = title.replace(" - FlavorFusion", "").strip()
    # Remove "New " prefix for searching
    return title

def get_title(n):
    """Extract <title> from article-N.html."""
    html_path = BASE / f"article-{n}.html"
    if not html_path.exists():
        return None, None
    text = html_path.read_text(encoding="utf-8")
    m = re.search(r'<title>\s*(.*?)\s*</title>', text, re.DOTALL)
    if not m:
        return None, None
    full_title = m.group(1).strip()
    # Remove suffix
    dish = full_title.replace(" - FlavorFusion", "").strip()
    return full_title, dish

def verify_image(n, dish):
    """Call doubao_vision to verify image shows the expected food."""
    img_path = BASE / "images" / f"article-{n}.jpg"
    if not img_path.exists():
        return "FILE_MISSING", ""

    prompt = f"Is this image primarily showing {dish}? Answer YES if the main subject matches this food, NO if it shows something else (person, animal, unrelated object, etc)."

    try:
        result = subprocess.run(
            [sys.executable, str(DOUBAO), str(img_path), prompt],
            capture_output=True, text=True, timeout=120
        )
        # Read the output file
        if os.path.exists(TEMP_OUT):
            text = Path(TEMP_OUT).read_text(encoding="utf-8").strip()
            # Clean up
            try:
                os.remove(TEMP_OUT)
            except:
                pass
            return "OK", text
        else:
            # Maybe output went to stdout
            text = result.stdout.strip()
            return "UNCLEAR", text[:200]
    except subprocess.TimeoutExpired:
        return "TIMEOUT", ""
    except Exception as e:
        return "ERROR", str(e)

def search_unsplash_food(dish):
    """Search Unsplash for a food image. Uses the direct photo approach."""
    # Try direct Unsplash photo search with food-related query
    # Build a search-friendly dish name
    query = dish.split(":")[0].strip()  # Take main part before colon
    # Also remove parentheticals
    query = re.sub(r'\([^)]*\)', '', query).strip()
    # Limit length
    query = query[:80]

    encoded_query = quote(query)

    # Use Unsplash search to find photos
    search_url = f"https://source.unsplash.com/800x600/?{encoded_query}&food"

    print(f"  Searching Unsplash for: {query}")
    return search_url

def download_image(url, path, max_retries=3):
    """Download image from URL to path. Returns True on success."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    for attempt in range(max_retries):
        try:
            req = Request(url, headers=headers)
            resp = urlopen(req, timeout=30)
            data = resp.read()
            if len(data) > 30000:
                path.write_bytes(data)
                print(f"  Downloaded {len(data)} bytes -> {path.name}")
                return True
            else:
                print(f"  Too small: {len(data)} bytes, retrying...")
        except Exception as e:
            print(f"  Attempt {attempt+1} failed: {e}")
            time.sleep(2)

    return False

def try_unsplash_alternatives(dish_name, path):
    """Try multiple Unsplash search variations for a dish."""
    variations = [
        dish_name,
        dish_name.split(":")[0].strip(),
        dish_name.split(",")[0].strip(),
    ]

    # Clean each variation
    cleaned = []
    for v in variations:
        v = re.sub(r'\([^)]*\)', '', v).strip()
        v = re.sub(r'["\'!]', '', v).strip()
        if v and v not in cleaned:
            cleaned.append(v)

    for query in cleaned:
        encoded = quote(query[:60])
        # Try different Unsplash endpoints
        urls = [
            f"https://images.unsplash.com/photo-1?w=800&q=85&query={encoded}",  # won't work, need real photo IDs
        ]

        # Better approach: use Unsplash search redirect
        for fmt in [
            f"https://source.unsplash.com/800x600/?{encoded}&food",
            f"https://source.unsplash.com/800x600/?{encoded}",
            f"https://source.unsplash.com/featured/800x600/?{encoded}",
        ]:
            if download_image(fmt, path):
                return True
            time.sleep(1)

    return False


# === MAIN ===
results = {"PASS": [], "FAIL": [], "SKIP": [], "ERROR": []}

print("=" * 70)
print("sub-food IMAGE AUDIT: Verifying all 53 article images match their content")
print("=" * 70)

# Pre-known failures (user confirmed)
pre_known_fail = {8}  # article-8 is a dog photo

batch_size = 5

all_articles = list(range(1, 54))

for i in range(0, len(all_articles), batch_size):
    batch = all_articles[i:i+batch_size]

    print(f"\n--- Batch {i//batch_size + 1}: articles {batch} ---")

    for n in batch:
        print(f"\n  [{n}] Checking article-{n}.jpg...")

        full_title, dish = get_title(n)
        if dish is None:
            print(f"  [{n}] SKIP - HTML file not found")
            results["SKIP"].append(n)
            continue

        print(f"       Title: {full_title}")
        print(f"       Dish: {dish}")

        if n in pre_known_fail:
            print(f"  [{n}] PRE-KNOWN FAIL (user confirmed)")
            results["FAIL"].append({"n": n, "dish": dish, "reason": "User confirmed: dog photo"})
            continue

        status, response = verify_image(n, dish)
        print(f"       Verdict: {status}")
        print(f"       Response: {response[:150]}")

        if status == "OK":
            # Check if response says YES or NO
            resp_lower = response.lower()
            if "yes" in resp_lower and "no" not in resp_lower[:resp_lower.find("yes")+5]:
                print(f"  [{n}] PASS - Image matches content")
                results["PASS"].append(n)
            elif "no" in resp_lower:
                desc = response[:200].replace("\n", " ")
                print(f"  [{n}] FAIL - Image does not match content. Response: {desc}")
                results["FAIL"].append({"n": n, "dish": dish, "reason": response[:200]})
            else:
                # Ambiguous - check if it described the correct food
                dish_keywords = dish.lower().split()[:3]
                matched = sum(1 for kw in dish_keywords if kw.lower() in resp_lower and len(kw) > 3)
                if matched >= 1:
                    print(f"  [{n}] AMBIGUOUS but mentions dish keywords -> PASS")
                    results["PASS"].append(n)
                else:
                    print(f"  [{n}] AMBIGUOUS - cannot determine, marking as SKIP (review manually)")
                    results["SKIP"].append({"n": n, "dish": dish, "response": response[:200]})
        else:
            print(f"  [{n}] ERROR: {status} - {response[:100]}")
            results["ERROR"].append({"n": n, "dish": dish, "error": response[:200]})

    # Wait between batches
    if i + batch_size < len(all_articles):
        print(f"\n  --- Waiting 2 seconds before next batch ---")
        time.sleep(2)

# === Report ===
print("\n\n" + "=" * 70)
print("FINAL AUDIT REPORT")
print("=" * 70)
print(f"\nPASS: {len(results['PASS'])} articles: {results['PASS']}")
print(f"FAIL: {len(results['FAIL'])} articles")
for f in results['FAIL']:
    print(f"  article-{f['n']}.jpg: {f['dish']} - {f['reason'][:100]}")
if results.get('SKIP'):
    print(f"SKIP: {len(results['SKIP'])} articles")
    for s in results['SKIP']:
        print(f"  {s}")
if results.get('ERROR'):
    print(f"ERROR: {len(results['ERROR'])} articles")
    for e in results['ERROR']:
        print(f"  article-{e['n']}.jpg: {e['error'][:100]}")

# === Replace Fails ===
if results["FAIL"]:
    print("\n" + "=" * 70)
    print("REPLACING FAILED IMAGES")
    print("=" * 70)

    for f in results["FAIL"]:
        n = f["n"]
        dish = f["dish"]
        img_path = BASE / "images" / f"article-{n}.jpg"

        print(f"\n  [{n}] Replacing article-{n}.jpg for: {dish}")
        if try_unsplash_alternatives(dish, img_path):
            print(f"  [{n}] SUCCESS: Replaced with Unsplash image")
        else:
            print(f"  [{n}] FAILED: Could not download replacement from Unsplash")

# === Final verification ===
print("\n\n" + "=" * 70)
print("FINAL FILE SIZE CHECK")
print("=" * 70)
for n in range(1, 54):
    path = BASE / "images" / f"article-{n}.jpg"
    if path.exists():
        size = path.stat().st_size
        status = "OK" if size > 10000 else "SUSPICIOUS"
        if size < 10000:
            print(f"  {status}: article-{n}.jpg ({size} bytes)")
    else:
        print(f"  MISSING: article-{n}.jpg")

print("\nDone.")
