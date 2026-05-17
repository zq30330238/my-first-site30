"""Manage newsletter subscribers via Tencent Exmail inbox.

Reads subscription emails sent via mailto: links on the sites.
Extracts subscriber email + site, deduplicates, stores in subscribers.json.

Usage:
  py shared/subscriber_manager.py check    # Scan inbox for new SUBSCRIBE-* emails
  py shared/subscriber_manager.py list     # Show all subscribers
  py shared/subscriber_manager.py export   # Export as CSV
"""

import re
import json
import sys
import imaplib
import email
from email.header import decode_header
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUBSCRIBERS_FILE = ROOT / "shared" / "subscribers.json"

EXMAIL_USER = "contact@jycsd.com"
EXMAIL_PASSWORD = "3CGLkS88AcUUsrL6"

SITE_BRANDS = {
    "healthy": "HealthyEats",
    "home": "HomeJoy",
    "pets": "PetCareHub",
    "finance": "MoneyWise",
    "tech": "TechPulse",
    "travel": "TravelScope",
}


def load_subscribers():
    if SUBSCRIBERS_FILE.exists():
        return json.loads(SUBSCRIBERS_FILE.read_text())
    return []


def save_subscribers(data):
    SUBSCRIBERS_FILE.write_text(json.dumps(data, indent=2))


def check_inbox(password):
    """Scan Tencent Exmail for SUBSCRIBE-* emails and extract subscriber info."""
    mail = imaplib.IMAP4_SSL("imap.exmail.qq.com")
    mail.login(EXMAIL_USER, password)
    mail.select("INBOX")

    _, ids = mail.search(None, 'SUBJECT "SUBSCRIBE-"')
    msg_ids = ids[0].split()
    if not msg_ids:
        print("No new subscription emails found.")
        mail.logout()
        return 0

    subscribers = load_subscribers()
    new_count = 0

    for mid in msg_ids:
        _, data = mail.fetch(mid, "(RFC822)")
        msg = email.message_from_bytes(data[0][1])

        subject = decode_header(msg["Subject"])[0][0]
        if isinstance(subject, bytes):
            subject = subject.decode()

        m = re.search(r'SUBSCRIBE-(\w+)', subject)
        if not m:
            continue
        site = m.group(1)
        if site not in SITE_BRANDS:
            continue

        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode(errors="ignore")
                    break
        else:
            body = msg.get_payload(decode=True).decode(errors="ignore")

        addr_m = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', body)
        if not addr_m:
            addr_m = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', msg["From"])
        if not addr_m:
            continue

        subscriber_email = addr_m.group(0)
        if subscriber_email == EXMAIL_USER:
            continue

        exists = any(s["email"] == subscriber_email and s["site"] == site for s in subscribers)
        if not exists:
            subscribers.append({
                "email": subscriber_email,
                "site": site,
                "brand": SITE_BRANDS[site],
                "joined": email.utils.parsedate_to_datetime(msg["Date"]).strftime("%Y-%m-%d"),
            })
            new_count += 1
            print(f"  + {subscriber_email} → {SITE_BRANDS[site]} ({site})")

        mail.store(mid, "+FLAGS", "\\Seen")

    mail.logout()

    if new_count:
        save_subscribers(subscribers)
        print(f"\n{new_count} new subscriber(s) added. Total: {len(subscribers)}")
    else:
        print("No new subscribers (all already in list).")
    return new_count


def list_subscribers():
    subs = load_subscribers()
    if not subs:
        print("No subscribers yet.")
        return
    print(f"{'Email':<40} {'Site':<12} {'Brand':<15} {'Joined'}")
    print("-" * 85)
    for s in subs:
        print(f"{s['email']:<40} {s['site']:<12} {s['brand']:<15} {s['joined']}")


def export_csv():
    subs = load_subscribers()
    if not subs:
        print("No subscribers.")
        return
    csv_path = ROOT / "shared" / "subscribers.csv"
    with open(csv_path, "w") as f:
        f.write("email,site,brand,joined\n")
        for s in subs:
            f.write(f"{s['email']},{s['site']},{s['brand']},{s['joined']}\n")
    print(f"Exported to {csv_path}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]
    if cmd == "check":
        password = EXMAIL_PASSWORD or input("Tencent Exmail Password: ").strip()
        if not password:
            print("Password required.")
            return
        check_inbox(password)
    elif cmd == "list":
        list_subscribers()
    elif cmd == "export":
        export_csv()
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
