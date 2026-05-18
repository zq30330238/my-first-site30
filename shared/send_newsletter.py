"""Generate and send niche newsletters to subscribers via Tencent Exmail SMTP.

Usage:
  py shared/send_newsletter.py [--site healthy] [--dry-run]

Requires: Tencent Exmail password (stored in SENDER_PASSWORD)
"""

import os
import re
import json
import sys
import smtplib
import argparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError

ROOT = Path(__file__).resolve().parent.parent
SUBSCRIBERS_FILE = ROOT / "shared" / "subscribers.json"

SENDER_EMAIL = "contact@jycsd.com"
SENDER_PASSWORD = os.environ.get("SENDER_EMAIL_PASSWORD", "")

DEEPSEEK_URL = "https://api.deepseek.com/anthropic/v1/messages"
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", "")

SITE_INFO = {
    "pets": {"brand": "PetCareHub", "domain": "pets.jycsd.com", "category": "Pet Care"},
    "healthy": {"brand": "HealthyEats", "domain": "healthy.jycsd.com", "category": "Healthy Eating"},
    "home": {"brand": "HomeJoy", "domain": "home.jycsd.com", "category": "Home & Garden"},
    "finance": {"brand": "MoneyWise", "domain": "finance.jycsd.com", "category": "Personal Finance"},
    "tech": {"brand": "TechPulse", "domain": "tech.jycsd.com", "category": "Technology"},
    "travel": {"brand": "TravelScope", "domain": "travel.jycsd.com", "category": "Travel"},
}


def load_subscribers():
    if SUBSCRIBERS_FILE.exists():
        return json.loads(SUBSCRIBERS_FILE.read_text())
    return []


def generate_newsletter(brand, category):
    """Generate a short newsletter for the niche via DeepSeek."""
    today = datetime.now().strftime("%B %d, %Y")
    prompt = f"""Write a concise, valuable newsletter for {brand} ({category} niche).

Format as JSON:
{{
  "subject": "Email subject line (50 chars max, engaging, no clickbait)",
  "body_html": "<h2>Main Tip/Insight Title</h2><p>2-3 sentences of actionable advice with specific data.</p><h3>Quick Tip</h3><p>One short actionable tip.</p><h3>From Our Blog</h3><ul><li>Link title 1</li><li>Link title 2</li></ul><p style='color:#888;font-size:12px'>You are receiving this because you subscribed at {brand}. <a href='mailto:contact@jycsd.com?subject=UNSUBSCRIBE'>Unsubscribe</a></p>"
}}

Rules: 200-300 words total. Actionable, specific, no AI fluff. US consumer audience. Output JSON only."""

    payload = {
        "model": "deepseek-v4-pro",
        "max_tokens": 2048,
        "temperature": 0.7,
        "messages": [{"role": "user", "content": prompt}],
    }

    try:
        req = Request(
            DEEPSEEK_URL,
            data=json.dumps(payload).encode(),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {DEEPSEEK_KEY}",
            },
        )
        resp = urlopen(req, timeout=120)
        data = json.loads(resp.read().decode())
        text = data["content"][0]["text"]
        if text.startswith("```"):
            text = text[text.find("\n") + 1:text.rfind("```")]
        brace = text.find("{")
        if brace > 0:
            text = text[brace:text.rfind("}") + 1]
        return json.loads(text)
    except Exception as e:
        print(f"  DeepSeek error: {e}")
        return None


def send_email(password, to_email, subject, body_html, brand):
    """Send one newsletter email via Tencent Exmail SMTP."""
    msg = MIMEMultipart("alternative")
    msg["From"] = f"{brand} <{SENDER_EMAIL}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg["Message-ID"] = f"<{datetime.now().strftime('%Y%m%d%H%M%S')}.{brand}@jycsd.com>"
    msg["List-Unsubscribe"] = f"<mailto:{SENDER_EMAIL}?subject=UNSUBSCRIBE>"

    msg.attach(MIMEText(body_html, "html"))

    try:
        server = smtplib.SMTP("smtp.exmail.qq.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, password)
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"  SMTP error sending to {to_email}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", help="Only send to subscribers of one site")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--password", help="Gmail App Password")
    args = parser.parse_args()

    password = args.password or SENDER_PASSWORD
    if not password:
        password = input("Tencent Exmail Password: ").strip()
    if not password:
        print("Password required.")
        return 1

    subscribers = load_subscribers()
    if not subscribers:
        print("No subscribers in list. Run subscriber_manager.py check first.")
        return 1

    if args.site:
        subscribers = [s for s in subscribers if s["site"] == args.site]
        if not subscribers:
            print(f"No subscribers for site: {args.site}")
            return 1

    sites = {}
    for s in subscribers:
        sites.setdefault(s["site"], []).append(s)

    total_sent = 0

    for site, subs in sites.items():
        info = SITE_INFO.get(site)
        if not info:
            continue

        print(f"\n{'='*50}")
        print(f"Site: {info['brand']} ({len(subs)} subscribers)")
        print(f"{'='*50}")

        # Generate one newsletter per site
        print("  Generating newsletter content...")
        content = generate_newsletter(info["brand"], info["category"])
        if not content:
            print("  FAILED to generate content")
            continue

        subject = content.get("subject", f"{info['brand']} Weekly Update")
        body = content.get("body_html", "")
        print(f"  Subject: {subject}")

        if args.dry_run:
            for s in subs:
                print(f"  [DRY RUN] Would send to {s['email']}")
            continue

        for s in subs:
            print(f"  Sending to {s['email']}...", end=" ", flush=True)
            ok = send_email(password, s["email"], subject, body, info["brand"])
            print("OK" if ok else "FAIL")
            if ok:
                total_sent += 1

    if args.dry_run:
        print(f"\n[DRY RUN] Would have sent {len(subscribers)} emails across {len(sites)} sites.")
    else:
        print(f"\nSent {total_sent} newsletter emails.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
