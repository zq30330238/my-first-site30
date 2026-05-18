"""Hot topic scout — RSS feeds -> DeepSeek scoring -> hot_topics.json
Called by nightly_worker.py or run standalone: py shared/trend_scout.py
"""
import json, os, sys, time, re
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FILE = ROOT / "shared" / "hot_topics.json"
API_URL = "https://api.deepseek.com/anthropic/v1/messages"
API_TOKEN = os.environ.get("DEEPSEEK_API_KEY", "")
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"

# Game-specific RSS feeds — items go directly to the mapped site
SITE_RSS_FEEDS = {
    "fortnite-site": [],
    "valorant-site": [],
    "lol-site": [],
    "minecraft-site": [],
    "eldenring-site": [],
}

# General gaming RSS feeds — keyword-matched to sites
GENERAL_RSS_FEEDS = [
    ("PC Gamer", "https://www.pcgamer.com/rss/"),
    ("Eurogamer", "https://www.eurogamer.net/feed"),
    ("Rock Paper Shotgun", "https://www.rockpapershotgun.com/feed"),
    ("VG247", "https://www.vg247.com/feed"),
    ("IGN", "https://feeds.feedburner.com/ign/all"),
]

SITE_NICHES = {
    "valorant-site": {
        "keywords": ["valorant", "agent", "map", "patch", "skin", "ranked", "aim", "lineup", "nerf", "buff", "vct", "champions", "bundle"],
        "context": "Valorant tactical FPS guides — agent ability breakdowns, map strategies, weapon stats, ranked climb tips, pro match analysis, patch notes coverage.",
        "categories": ["agents", "maps", "weapons", "ranked", "lineups"],
    },
    "fortnite-site": {
        "keywords": ["fortnite", "weapon", "map", "season", "skin", "building", "zero build", "battle pass", "poi", "meta", "chapter", "og", "nerf"],
        "context": "Fortnite battle royale guides — weapon tier lists, map drop spots, building techniques, season update breakdowns, battle pass rewards, limited-time modes.",
        "categories": ["weapons", "map", "building", "seasons"],
    },
    "lol-site": {
        "keywords": ["league", "champion", "rework", "patch", "item", "jungle", "lane", "ranked", "skin", "worlds", "msi", "esports", "nerf", "buff", "aram"],
        "context": "League of Legends MOBA guides — champion builds, item analysis, jungle pathing, lane matchups, patch note breakdowns, pro play meta analysis, ranked climb strategies.",
        "categories": ["champions", "items", "jungle", "laning", "teamfights"],
    },
    "minecraft-site": {
        "keywords": ["minecraft", "crafting", "build", "redstone", "mob", "biome", "enchant", "farm", "update", "snapshot", "nether", "end", "wither", "warden"],
        "context": "Minecraft sandbox guides — crafting recipes, building tutorials, redstone contraptions, mob farms, biome exploration, enchantment guides, update coverage.",
        "categories": ["crafting", "mobs", "building", "redstone", "enchanting", "biomes"],
    },
    "eldenring-site": {
        "keywords": ["elden ring", "boss", "build", "weapon", "quest", "dlc", "shadow", "erdtree", "talisman", "spirit ash", "pvp", "patch", "challenge run"],
        "context": "Elden Ring action RPG guides — boss strategies, build optimization, weapon locations, quest walkthroughs, DLC content, PvP meta, challenge run tips.",
        "categories": ["bosses", "builds", "weapons", "quests", "map"],
    },
    "dragonball-site": {
        "keywords": ["dragon ball", "goku", "vegeta", "daima", "super", "sparking zero", "kakarot", "xenoverse", "fighterz", "manga", "movie", "form", "fusion"],
        "context": "Dragon Ball franchise content — anime episode guides, game walkthroughs, character power scaling, movie reviews, manga chapter analysis, fighting game combos.",
        "categories": ["anime", "games", "characters", "movies", "manga"],
    },
    "onepiece-site": {
        "keywords": ["one piece", "luffy", "zoro", "gear", "manga", "episode", "pirate warriors", "bounty rush", "chapter", "devil fruit", "haki", "elbaf"],
        "context": "One Piece franchise content — anime episode recaps, manga chapter analysis, game guides, character backstories, theory discussions, power system explainers.",
        "categories": ["anime", "games", "characters", "manga", "theories"],
    },
    "naruto-site": {
        "keywords": ["naruto", "boruto", "sasuke", "shippuden", "jutsu", "ninja storm", "connections", "manga", "episode", "akatsuki", "clan", "shinobi striker"],
        "context": "Naruto/Boruto franchise content — episode guides, game walkthroughs, character analysis, jutsu explainers, clan histories, manga chapter coverage.",
        "categories": ["anime", "games", "characters", "manga", "world"],
    },
    "sub-healthy": {
        "keywords": ["nutrition", "diet", "recipe", "healthy", "weight loss", "vitamin", "protein", "meal plan", "supplement", "calorie", "fiber", "superfood", "metabolism"],
        "context": "Nutrition and healthy eating guides — meal plans, diet comparisons, supplement reviews, recipe collections, macro tracking advice, evidence-based food science.",
        "categories": ["meal-plans", "recipes", "supplements", "weight-loss", "nutrition-science"],
    },
    "sub-pets": {
        "keywords": ["dog", "cat", "pet", "breed", "training", "food", "health", "grooming", "puppy", "kitten", "vet", "adoption", "behavior", "toy"],
        "context": "Pet care guides — dog and cat breed profiles, training techniques, nutrition advice, health symptom checkers, grooming tutorials, product recommendations.",
        "categories": ["dogs", "cats", "health", "training", "nutrition"],
    },
    "sub-home": {
        "keywords": ["diy", "renovation", "garden", "plant", "repair", "remodel", "interior design", "furniture", "plumbing", "painting", "lawn", "vegetable", "landscape"],
        "context": "Home improvement and gardening guides — DIY tutorials, renovation planning, garden design, plant care, tool reviews, interior design tips, seasonal maintenance.",
        "categories": ["diy", "gardening", "interior", "repairs", "seasonal"],
    },
    "sub-finance": {
        "keywords": ["budget", "invest", "credit", "debt", "savings", "retirement", "tax", "mortgage", "loan", "401k", "stock", "etf", "crypto", "insurance", "frugal"],
        "context": "Personal finance guides — budgeting methods, investment strategies, credit score improvement, debt payoff plans, retirement planning, tax optimization, saving hacks.",
        "categories": ["budgeting", "investing", "debt", "retirement", "taxes"],
    },
    "sub-tech": {
        "keywords": ["ai", "smartphone", "laptop", "gadget", "app", "software", "apple", "android", "windows", "review", "security", "privacy", "chip", "robot"],
        "context": "Technology and gadgets guides — product reviews, software comparisons, AI tool roundups, phone and laptop buying guides, security tips, emerging tech explainers.",
        "categories": ["reviews", "ai", "mobile", "computing", "security"],
    },
    "sub-travel": {
        "keywords": ["destination", "flight", "hotel", "itinerary", "backpack", "budget travel", "road trip", "visa", "airbnb", "solo", "europe", "asia", "national park", "cruise"],
        "context": "Travel guides — destination itineraries, budget travel tips, flight deal alerts, hotel and Airbnb reviews, packing lists, visa requirement guides, road trip routes.",
        "categories": ["destinations", "budget-travel", "planning", "accommodation", "tips"],
    },
}


def fetch_rss(feed_url, source_name, limit=10):
    try:
        req = Request(feed_url, headers={"User-Agent": USER_AGENT})
        resp = urlopen(req, timeout=15)
        raw = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  [!] RSS {source_name}: {e}")
        return []
    items = []
    item_pattern = re.compile(r"<item>(.*?)</item>", re.DOTALL)
    title_pattern = re.compile(r"<title>(.*?)</title>", re.DOTALL)
    link_pattern = re.compile(r"<link>(.*?)</link>", re.DOTALL)
    for match in item_pattern.finditer(raw):
        if len(items) >= limit:
            break
        item_xml = match.group(1)
        title_m = title_pattern.search(item_xml)
        link_m = link_pattern.search(item_xml)
        if not title_m:
            continue
        title = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", title_m.group(1).strip())
        url = ""
        if link_m:
            url = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", link_m.group(1).strip())
        items.append({
            "title": title,
            "source": "rss",
            "subreddit": source_name,
            "url": url,
            "reddit_score": 0,
            "num_comments": 0,
        })
    return items


def _norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())[:70]


def deduplicate(items):
    seen = {}
    for item in items:
        key = _norm(item["title"])
        if key not in seen or item.get("reddit_score", 0) > seen[key].get("reddit_score", 0):
            seen[key] = item
    return list(seen.values())


def _call_deepseek(payload):
    req = Request(
        API_URL,
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_TOKEN}",
        },
    )
    for attempt in range(2):
        try:
            resp = urlopen(req, timeout=120)
            data = json.loads(resp.read().decode())
            text = "\n".join(b["text"] for b in data["content"] if b["type"] == "text")
            text = text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            return json.loads(text.strip())
        except Exception as e:
            if attempt == 1:
                print(f"  [!] DeepSeek API: {e}")
                return None
            time.sleep(2)
    return None


def score_with_deepseek(items, site_key):
    if not items:
        return []
    niche = SITE_NICHES.get(site_key)
    if not niche:
        return heuristic_score(items, site_key)
    if not API_TOKEN:
        print(f"  [!] No DEEPSEEK_API_KEY, using heuristic scores")
        return heuristic_score(items, site_key)

    all_scored = []
    for i in range(0, len(items), 5):
        batch = items[i:i + 5]
        batch_json = json.dumps([
            {"id": j, "title": t["title"], "source": t["source"]}
            for j, t in enumerate(batch)
        ], indent=2)

        system = """You are a content trend analyst for a gaming and lifestyle content network.
Output ONLY a JSON array. No markdown, no code fences, no extra text.
Score honestly: 50-70 for standard topics, 70-85 for strong matches, 85+ for breaking news with high content opportunity."""

        user = f"""Site: {site_key}
Niche: {niche['context']}
Categories: {', '.join(niche['categories'])}

Topics to score:
{batch_json}

For each topic return a JSON object with these keys:
- "id": integer matching the input topic id
- "heat": 0-100 (current internet buzz level)
- "fit": 0-100 (relevance to this site's niche)
- "competition": 0-100 (content saturation — 100 means fully covered, low = blue ocean)
- "category": best-fitting site category from the list above
- "angle": 1-sentence English article angle (actionable, specific)
- "keywords": array of 3-5 target SEO keywords

Output a JSON array with one object per topic. Nothing else."""

        payload = {
            "model": "deepseek-v4-flash",
            "max_tokens": 2048,
            "temperature": 0.4,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        }
        scores = _call_deepseek(payload)
        if scores is None:
            all_scored.extend(heuristic_score(batch, site_key))
            continue
        for s in scores:
            idx = s.get("id", -1)
            if idx < 0 or idx >= len(batch):
                continue
            t = batch[idx]
            heat = max(0, min(100, s.get("heat", 50)))
            fit = max(0, min(100, s.get("fit", 50)))
            comp = max(0, min(100, s.get("competition", 50)))
            composite = round(heat * 0.4 + fit * 0.4 + (100 - comp) * 0.2)
            all_scored.append({
                "title": t["title"],
                "source": t["source"],
                "subreddit": t.get("subreddit", ""),
                "url": t["url"],
                "score": composite,
                "site": site_key,
                "category": s.get("category", niche["categories"][0]),
                "angle": s.get("angle", ""),
                "keywords": s.get("keywords", []),
                "date_found": datetime.now().strftime("%Y-%m-%d"),
            })
        if i + 5 < len(items):
            time.sleep(1)
    return all_scored


def heuristic_score(items, site_key):
    niche = SITE_NICHES.get(site_key, {"keywords": [], "categories": ["general"], "context": ""})
    kw_list = [k.lower() for k in niche.get("keywords", [])]
    results = []
    for t in items:
        tl = t["title"].lower()
        kw_hits = sum(1 for k in kw_list if k in tl)
        base = min(45 + kw_hits * 8, 85)
        if t.get("reddit_score", 0) > 500:
            base += 10
        if t.get("num_comments", 0) > 30:
            base += 5
        results.append({
            "title": t["title"],
            "source": t["source"],
            "subreddit": t.get("subreddit", ""),
            "url": t["url"],
            "score": min(base, 95),
            "site": site_key,
            "category": niche["categories"][0],
            "angle": t["title"],
            "keywords": [k for k in kw_list if k in tl][:5],
            "date_found": datetime.now().strftime("%Y-%m-%d"),
        })
    return results


def _rss_site_match(title):
    """Quick keyword match: which game sites would a general RSS title fit?"""
    tl = title.lower()
    matches = []
    game_sites = [k for k in SITE_NICHES if k.endswith("-site")]
    for sk in game_sites:
        n = SITE_NICHES[sk]
        hits = sum(1 for k in n["keywords"] if len(k) >= 4 and k in tl)
        if hits >= 1:
            matches.append((sk, hits))
    matches.sort(key=lambda x: -x[1])
    return [m[0] for m in matches[:3]]


def save_topics(scored_items):
    existing = []
    if OUTPUT_FILE.exists():
        try:
            existing = json.loads(OUTPUT_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    seen = {_norm(i["title"]) for i in scored_items}
    merged = [i for i in existing if _norm(i.get("title", "")) not in seen]
    merged.extend(scored_items)
    merged.sort(key=lambda x: x.get("score", 0), reverse=True)
    merged = merged[:100]
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  Saved {len(merged)} topics to {OUTPUT_FILE}")


def main():
    print("=" * 50)
    print("Trend Scout — fetching hot topics")
    print("=" * 50)

    all_items = []

    # Phase 1: Game-specific RSS feeds (direct site mapping)
    for site_key, feeds in SITE_RSS_FEEDS.items():
        for name, url in feeds:
            print(f"RSS {name} -> {site_key}")
            items = fetch_rss(url, name, limit=10)
            for item in items:
                item["_site"] = site_key
            all_items.extend(items)
            print(f"  {len(items)} items")
            time.sleep(2)

    # Phase 2: General gaming RSS feeds (keyword matched)
    for name, url in GENERAL_RSS_FEEDS:
        print(f"RSS {name} (general)")
        items = fetch_rss(url, name, limit=10)
        for item in items:
            item["_rss"] = True
        all_items.extend(items)
        print(f"  {len(items)} items")
        time.sleep(2)

    # Phase 3: Dedup
    unique = deduplicate(all_items)
    print(f"\nAfter dedup: {len(unique)} unique (from {len(all_items)} raw)")

    # Phase 4: Score - direct-mapped items get baseline 75, keyword-matched go to DeepSeek
    direct_items = []
    keyword_items = []
    for item in unique:
        if item.get("_rss"):
            targets = _rss_site_match(item["title"])
            for sk in targets:
                keyword_items.append((sk, item))
        else:
            sk = item.get("_site", "")
            if sk in SITE_NICHES:
                direct_items.append((sk, item))

    all_scored = []
    total_worthy = 0

    # Direct-mapped: baseline score based on keyword relevance
    by_site_direct = {}
    for sk, item in direct_items:
        by_site_direct.setdefault(sk, []).append(item)
    for site_key, items in by_site_direct.items():
        niche = SITE_NICHES.get(site_key, {"categories": ["general"], "keywords": []})
        site_kw = [k for k in niche.get("keywords", []) if len(k) >= 4]
        for t in items:
            tl = t["title"].lower()
            kw_match = [k for k in site_kw if k in tl][:5]
            if kw_match:
                # Relevant: score based on keyword density
                score = 72 + min(len(kw_match) * 3, 15)
            else:
                # No keyword match: likely off-topic spam, low score
                score = 25
            all_scored.append({
                "title": t["title"],
                "source": t["source"],
                "subreddit": t.get("subreddit", ""),
                "url": t["url"],
                "score": score,
                "site": site_key,
                "category": niche["categories"][0],
                "angle": t["title"],
                "keywords": kw_match,
                "date_found": datetime.now().strftime("%Y-%m-%d"),
            })
            if score >= 65:
                total_worthy += 1
        worthy_count = sum(1 for t in items if any(
            k in t["title"].lower() for k in site_kw))
        print(f"  {site_key}: {len(items)} direct, {worthy_count} relevant")

    # Keyword-matched: DeepSeek scoring
    by_site_kw = {}
    for sk, item in keyword_items:
        by_site_kw.setdefault(sk, []).append(item)
    for site_key, items in by_site_kw.items():
        if not items:
            continue
        print(f"\nScoring {len(items)} items for {site_key} (LLM)...")
        scored = score_with_deepseek(items, site_key)
        worthy = [s for s in scored if s["score"] >= 65]
        all_scored.extend(scored)
        total_worthy += len(worthy)
        print(f"  {len(scored)} scored, {len(worthy)} worthy (score>=65)")

    # Phase 5: Save
    save_topics(all_scored)
    print(f"\nDone. {len(all_scored)} total scored, {total_worthy} above threshold")
    return 0


if __name__ == "__main__":
    sys.exit(main())
