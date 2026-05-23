"""Generate 30 unique legal articles for rightsdaily.com.

Uses a two-call approach: body HTML + metadata JSON (model doesn't follow
complex single-JSON schemas reliably for legal topics).

Usage: python shared/generate_rightsdaily_articles.py
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path

from reasonix_helper import reasonix_call_json, reasonix_call

from site_templates import (
    SITE_CONFIG, GLOBALS, get_content_generation_prompt,
    render_article_html, quick_validate,
)

from create_articles import (
    get_next_article_num, count_words,
    extract_title, fix_cover_image_url, insert_index_card,
    update_index_sidebar, update_sitemap, UNSPLASH_FAKE_RE, CATEGORY_PHOTOS,
)

ROOT = Path(__file__).resolve().parent.parent

TOPICS = [
    "Tenant Rights: How to Break a Lease Without Penalty",
    "What to Do Immediately After a Car Accident",
    "How to File for Divorce Without a Lawyer",
    "Creating a Legally Valid Will in 5 Simple Steps",
    "Workplace Discrimination: Know Your Legal Rights",
    "The Complete Guide to Small Claims Court",
    "How to Handle Debt Collection Lawsuits",
    "What Is a Power of Attorney and Do You Need One?",
    "Child Custody Laws Every Parent Should Understand",
    "How to Resolve Contractor Disputes Legally",
    "Starting an LLC: Step-by-Step Legal Guide",
    "Your Legal Rights During a Police Stop",
    "When and How to File a Medical Malpractice Claim",
    "What to Do If You Receive a Legal Summons",
    "Property Line and Fence Disputes with Neighbors",
    "How to Legally Evict a Tenant in Your State",
    "What Counts as Wrongful Termination",
    "How to File a Personal Injury Claim",
    "Copyright Basics Every Content Creator Must Know",
    "How to Get a Restraining Order",
    "What Happens When You File for Bankruptcy",
    "Landlord Rights: Legal Dos and Don'ts",
    "How to Modify a Child Support Order",
    "HOA Rules and Your Legal Rights as a Homeowner",
    "How to Fight a Traffic Ticket and Win",
    "Dying Without a Will: What Happens to Your Estate",
    "How to Negotiate a Severance Agreement",
    "Premises Liability: Who Is Responsible for Your Injury",
    "What to Do If You Are Being Sued",
    "How to Protect Your Intellectual Property Online",
]

SITE_DIR = "rightsdaily"
cfg = SITE_CONFIG[SITE_DIR]


def generate_body(topic):
    """Step 1: Generate article body HTML."""
    prompt = (
        "Output the article body as HTML with <h2> and <p>/<ul>/<ol>/<blockquote> tags. "
        "800+ words, 4-6 sections. Include one <blockquote> with a key stat or legal expert tip. "
        "No wrapper, no explanation - just the HTML starting with <h2>."
    )
    msg = (
        f'Write a legal article about "{topic}" for RightsDaily.com. '
        "Only output the <h2>/<p>/<ul>/<blockquote> HTML, no wrapper, no explanation."
    )
    return reasonix_call(prompt, msg)


def generate_metadata(topic, today):
    """Step 2: Generate metadata as JSON.

    NOTE: 'description' key is deliberately excluded from the prompt — testing
    revealed it causes the model to return empty JSON for this topic domain.
    description is generated in Python as a fallback.
    """
    prompt = (
        "Output ONLY valid JSON with these exact keys: "
        "title, h1_title, keywords, tag_spans, read_time, date_iso, date_display. "
        "No other text, no code fences."
    )
    msg = (
        f'Metadata for article "{topic}" on RightsDaily. '
        f"Date: {today}. "
        "title: SEO title (max 60 chars, ends with - RightsDaily). "
        "h1_title: article headline (no brand name). "
        "keywords: comma-separated list of 5-8 SEO keywords. "
        "tag_spans: comma-separated list of 5-6 category tags (e.g. 'tag1,tag2,tag3,tag4,tag5,tag6'). "
        "read_time: integer. "
        "date_iso: YYYY-MM-DD. "
        "date_display: Month DD, YYYY."
    )
    return reasonix_call_json(prompt, msg)


def build_tag_spans(tag_str):
    """Convert comma-separated tags to HTML span elements."""
    tags = [t.strip() for t in tag_str.split(",") if t.strip()]
    parts = []
    for t in tags[:6]:
        parts.append(
            f"<span class='px-3 py-1 bg-brand-50 text-brand-700 text-sm rounded-full'>{t}</span>"
        )
    return "".join(parts)


def build_json_ld(title, h1_title, description, article_url, date_iso):
    """Build a basic JSON-LD NewsArticle schema."""
    schema = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": h1_title,
        "description": description,
        "url": article_url,
        "datePublished": date_iso,
        "dateModified": date_iso,
        "author": {
            "@type": "Organization",
            "name": "RightsDaily",
        },
        "publisher": {
            "@type": "Organization",
            "name": "RightsDaily",
        },
    }
    return json.dumps(schema)


def build_cover_img():
    """Pick a random real Unsplash photo for rightsdaily."""
    import random
    # Use sub-pets as fallback pool (exists in CATEGORY_PHOTOS)
    pool = CATEGORY_PHOTOS.get(SITE_DIR, CATEGORY_PHOTOS["sub-pets"])
    photo_id = random.choice(pool)
    return (
        f"<img src='https://images.unsplash.com/photo-{photo_id}?w=1200&h=630&fit=crop' "
        f"alt='Legal rights guide' class='rounded-2xl mb-10 w-full'>"
    )


def call_body_with_retry(topic, retries=3):
    """Call body generation with retries."""
    for attempt in range(retries):
        try:
            body = generate_body(topic)
            if body and len(body) > 200:
                return body
        except Exception as e:
            print(f"  Body attempt {attempt+1} failed: {e}", flush=True)
            if attempt < retries - 1:
                time.sleep(1)
    return None


def call_metadata_with_retry(topic, today, retries=3):
    """Call metadata generation with retries."""
    for attempt in range(retries):
        try:
            meta = generate_metadata(topic, today)
            if isinstance(meta, dict) and "h1_title" in meta:
                return meta
        except Exception as e:
            print(f"  Meta attempt {attempt+1} failed: {e}", flush=True)
            if attempt < retries - 1:
                time.sleep(1)
    return None


def main():
    total_ok = 0
    results = []
    today = datetime.now().strftime("%Y-%m-%d")

    print(f"{'='*60}")
    print(f"Generating {len(TOPICS)} articles for rightsdaily.com")
    print(f"{'='*60}")

    for i, topic in enumerate(TOPICS, 1):
        article_num = get_next_article_num(SITE_DIR)
        print(f"\n[{i}/{len(TOPICS)}] article-{article_num}.html")
        print(f"  Topic: {topic}")

        # Step 1: Generate body HTML
        print(f"  Step 1: Generating body...", flush=True)
        body = call_body_with_retry(topic)
        if not body:
            print(f"  FAIL: Body generation failed after 3 attempts")
            results.append((article_num, topic, "FAILED", 0))
            continue

        wc = count_words(body)
        print(f"  Body: {wc} words", flush=True)

        if wc < 800:
            print(f"  WARNING: Body too short ({wc} words), retrying...", flush=True)
            body = call_body_with_retry(topic)
            if not body:
                print(f"  FAIL: Body still too short")
                results.append((article_num, topic, "FAILED", wc))
                continue
            wc = count_words(body)
            print(f"  Body retry: {wc} words", flush=True)

        # Step 2: Generate metadata
        print(f"  Step 2: Generating metadata...", flush=True)
        meta = call_metadata_with_retry(topic, today)
        if not meta:
            print(f"  FAIL: Metadata generation failed, using fallback")
            meta = {
                "title": f"{topic} - RightsDaily",
                "h1_title": topic,
                "description": f"Complete guide to {topic.lower()}. Learn your legal rights and options.",
                "keywords": topic.lower().replace(": ", ",").replace(" ", ","),
                "tag_spans": topic.split(":")[0].strip() if ":" in topic else topic.split(" ")[0],
                "read_time": "8",
                "date_iso": today,
                "date_display": datetime.now().strftime("%B %d, %Y"),
            }

        # Step 3: Build full content dict
        tag_str = meta.get("tag_spans", "")
        tag_spans = build_tag_spans(tag_str) if "," in tag_str else tag_str

        keywords = meta.get("keywords", "")
        if isinstance(keywords, list):
            keywords = ", ".join(keywords)

        read_time = meta.get("read_time", "8")
        if not isinstance(read_time, str):
            read_time = str(read_time)

        description = meta.get("description", "")
        if not description or len(description) < 50:
            description = f"Learn about {topic.lower()}. This comprehensive guide covers everything you need to know about your legal rights and options."

        article_url = f"https://{cfg['domain']}/article-{article_num}.html"

        # Clean body: strip HTML/JS wrappers if model added them
        body_clean = body.strip()
        if body_clean.startswith("```html"):
            body_clean = body_clean[7:]
        if body_clean.startswith("```"):
            body_clean = body_clean[3:]
        if body_clean.endswith("```"):
            body_clean = body_clean[:-3]
        body_clean = body_clean.strip()

        content = {
            "title": meta.get("title", f"{topic} - RightsDaily")[:60],
            "description": description[:160],
            "keywords": keywords[:200],
            "h1_title": meta.get("h1_title", topic),
            "breadcrumb": topic.split(":")[0].strip() if ":" in topic else meta.get("h1_title", topic),
            "cover_img_html": build_cover_img(),
            "article_body_html": body_clean,
            "tag_spans": tag_spans,
            "json_ld": build_json_ld(
                meta.get("title", topic),
                meta.get("h1_title", topic),
                description,
                article_url,
                meta.get("date_iso", today),
            ),
            "read_time": read_time,
            "date_iso": meta.get("date_iso", today),
            "date_display": meta.get("date_display", datetime.now().strftime("%B %d, %Y")),
            "article_url": article_url,
        }

        # Step 4: Fix cover image URL
        content = fix_cover_image_url(content, SITE_DIR)

        # Step 5: Render HTML
        html, _ = render_article_html(SITE_DIR, content)

        # Step 6: Validate
        issues = quick_validate(html, SITE_DIR)
        if wc < 800:
            issues.append(f"Word count too low: {wc} (need 800+)")

        for fake_m in UNSPLASH_FAKE_RE.finditer(html):
            fid = fake_m.group(1)
            if len(fid) <= 9:
                issues.append(f"Fake Unsplash photo ID: photo-{fid}")

        if issues:
            print(f"  FAIL: {'; '.join(issues)}")
            results.append((article_num, topic, "FAILED", wc))
            continue

        # Step 7: Save
        out_path = ROOT / SITE_DIR / f"article-{article_num}.html"
        out_path.write_text(html, encoding="utf-8")

        title = content.get("h1_title", extract_title(html))
        print(f"  OK: article-{article_num}.html — {wc} words — \"{title[:60]}\"")

        # Step 8: Update index + sidebar + sitemap
        insert_index_card(SITE_DIR, article_num, content)
        update_index_sidebar(SITE_DIR, article_num, title)
        update_sitemap(SITE_DIR, article_num)

        results.append((article_num, topic, title, wc))
        total_ok += 1

        # Sleep between articles
        time.sleep(3)

    # Summary
    fail_count = len(results) - total_ok
    print(f"\n{'='*60}")
    print(f"Summary: {total_ok} OK, {fail_count} FAIL out of {len(TOPICS)} topics")
    print(f"{'='*60}")
    for r in results:
        num, topic, title, wc = r
        status = "OK" if title != "FAILED" else "FAIL"
        print(f"  article-{num}.html [{status}] — {wc}w — {topic[:60]}")


if __name__ == "__main__":
    main()
