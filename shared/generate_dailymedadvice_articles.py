"""Generate 30 unique medical/health articles for dailymedadvice.com.

Uses a two-call approach: body HTML + metadata JSON (same pattern as rightsdaily).

Usage: python shared/generate_dailymedadvice_articles.py
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
    "Understanding High Blood Pressure: Causes, Symptoms, and Natural Management",
    "Complete Guide to Type 2 Diabetes: Prevention and Daily Management",
    "Natural Remedies for Anxiety and Stress Relief",
    "Everything You Need to Know About Vitamin D Deficiency",
    "How to Build a Balanced Diet for Optimal Health",
    "Understanding Cholesterol: Good vs Bad and How to Manage It",
    "The Complete Guide to Better Sleep Hygiene",
    "Common Cold vs Flu: How to Tell the Difference",
    "Natural Ways to Boost Your Immune System",
    "Understanding Mental Health: Depression Signs and Treatment Options",
    "The Benefits of Regular Exercise for Long-Term Health",
    "How to Manage Chronic Back Pain Without Surgery",
    "Complete Guide to Digestive Health and Gut Bacteria",
    "Understanding Allergies: Types, Triggers, and Treatments",
    "Heart Disease Prevention: Lifestyle Changes That Save Lives",
    "Natural Headache Remedies That Actually Work",
    "The Science Behind Intermittent Fasting and Weight Loss",
    "How to Lower Your Blood Sugar Naturally",
    "Understanding Thyroid Disorders: Hyperthyroidism and Hypothyroidism",
    "The Role of Omega-3 Fatty Acids in Brain Health",
    "How to Recognize Early Signs of Stroke",
    "Natural Remedies for Joint Pain and Arthritis",
    "The Complete Guide to Prenatal Nutrition",
    "Understanding Skin Conditions: Eczema, Psoriasis, and Acne",
    "How to Quit Smoking: Proven Strategies That Work",
    "The Health Benefits of Meditation and Mindfulness",
    "Understanding Kidney Health: Warning Signs You Shouldn't Ignore",
    "How to Read Nutrition Labels Like a Pro",
    "The Connection Between Gut Health and Mental Health",
    "Natural Ways to Lower Inflammation in Your Body",
]

SITE_DIR = "dailymedadvice"
cfg = SITE_CONFIG[SITE_DIR]


def generate_body(topic):
    """Step 1: Generate article body HTML."""
    prompt = (
        "Output the article body as HTML with <h2> and <p>/<ul>/<ol>/<blockquote> tags. "
        "800+ words, 4-6 sections. Include one <blockquote> with a key health stat or medical expert tip. "
        "No wrapper, no explanation - just the HTML starting with <h2>."
    )
    msg = (
        f'Write a medical/health article about "{topic}" for DailyMedAdvice.com. '
        "Tone: authoritative, science-backed, actionable. "
        "Only output the <h2>/<p>/<ul>/<blockquote> HTML, no wrapper, no explanation."
    )
    return reasonix_call(prompt, msg)


def generate_metadata(topic, today):
    """Step 2: Generate metadata as JSON."""
    prompt = (
        "Output ONLY valid JSON with these exact keys: "
        "title, h1_title, keywords, tag_spans, read_time, date_iso, date_display. "
        "No other text, no code fences."
    )
    msg = (
        f'Metadata for article "{topic}" on DailyMedAdvice. '
        f"Date: {today}. "
        "title: SEO title (max 60 chars, ends with - DailyMedAdvice). "
        "h1_title: article headline (no brand name). "
        "keywords: comma-separated list of 5-8 SEO keywords. "
        "tag_spans: comma-separated list of 5-6 category tags (e.g. 'health,wellness,nutrition,diet,exercise,sleep'). "
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
            "name": "DailyMedAdvice",
        },
        "publisher": {
            "@type": "Organization",
            "name": "DailyMedAdvice",
        },
    }
    return json.dumps(schema)


def build_cover_img():
    """Pick a random real Unsplash photo for the medical site."""
    import random
    pool = [
        "1559757175-2b61f9e6b8f5", "1571019113456-f7c5e2c2e7c9",
        "1506126619692-2c4c2a0bd6e8", "1544360367-6e8e3a7c34b9",
        "1551078809-3e5d7e3b79f7", "1505753248870-5d998a4d93f9",
        "1535914250713-e08eb8c5ba3f", "1559757175-2b61f9e6b8f5",
        "1576091160550-2173dba99911", "1511173195840-7d3c1b0b9f0a",
        "1544360367-6e8e3a7c34b9", "1535914250713-e08eb8c5ba3f",
    ]
    photo_id = random.choice(pool)
    return (
        f"<img src='https://images.unsplash.com/photo-{photo_id}?w=1200&h=630&fit=crop' "
        f"alt='Health and medical guide' class='rounded-2xl mb-10 w-full'>"
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
    print(f"Generating {len(TOPICS)} articles for dailymedadvice.com")
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
                "title": f"{topic} - DailyMedAdvice",
                "h1_title": topic,
                "description": f"Complete guide to {topic.lower()}. Learn science-backed health and wellness information.",
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
            description = f"Learn about {topic.lower()}. This comprehensive guide covers everything you need to know about your health and wellness."

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
            "title": meta.get("title", f"{topic} - DailyMedAdvice")[:60],
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
