import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from difflib import SequenceMatcher

import funda_script
import pararius_script
from utils import save_listings

# ============================================================
#  EMAIL SETTINGS  (set via .env / environment variables)
# ============================================================

SMTP_SERVER    = 'smtp.gmail.com'
SMTP_PORT      = 587
EMAIL_FROM     = os.environ['EMAIL_FROM']
EMAIL_PASSWORD = os.environ['EMAIL_PASSWORD']
EMAIL_TO       = [addr.strip() for addr in os.environ['EMAIL_TO'].split(',')]

# ============================================================

def deduplicate(all_listings):
    merged = []
    used   = set()

    for i, a in enumerate(all_listings):
        if i in used:
            continue
        for j, b in enumerate(all_listings):
            if i == j or j in used:
                continue
            if a['source'] == b['source']:
                continue
            ratio = SequenceMatcher(None, a['title'].lower(), b['title'].lower()).ratio()
            if ratio > 0.8:
                a = dict(a)
                a['second_url']    = b['url']
                a['second_source'] = b['source']
                used.add(j)
                break
        merged.append(a)
        used.add(i)

    return merged

def send_email(all_listings, offering_type):
    total   = len(all_listings)
    label   = 'Koop' if offering_type == 'buy' else 'Huur'
    subject = f"{label} autoscript: {total} new listing(s)"

    lines = []

    dupes    = [l for l in all_listings if l.get('second_url')]
    funda    = [l for l in all_listings if l['source'] == 'Funda' and not l.get('second_url')]
    pararius = [l for l in all_listings if l['source'] == 'Pararius' and not l.get('second_url')]

    for group_label, group in [('Funda & Pararius', dupes), ('Funda', funda), ('Pararius', pararius)]:
        if not group:
            continue
        lines.append(f"── {group_label} ({len(group)}) ──────────────────────────")
        for l in group:
            details = ' | '.join(filter(None, [l['price'], l['area'], l['extra']]))
            lines.append(f"- {l['title']}")
            lines.append(f"  {details}")
            lines.append(f"  {l['url']}  ({l['source']})")
            if l.get('second_url'):
                lines.append(f"  {l['second_url']}  ({l['second_source']})")
            if l.get('maps_url'):
                lines.append(f"  📍 {l['maps_url']}")
            lines.append("")

    body = "\n".join(lines)

    msg = MIMEMultipart()
    msg['From']    = EMAIL_FROM
    msg['To']      = ", ".join(EMAIL_TO)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())

    print(f"Email sent: {subject}")

if __name__ == '__main__':
    # Usage: python main.py [buy|rent]  (defaults to buy)
    offering_type = sys.argv[1] if len(sys.argv) > 1 else 'buy'
    category      = 'koop' if offering_type == 'buy' else 'huur'

    if offering_type not in ('buy', 'rent'):
        print(f"Unknown offering type '{offering_type}'. Use 'buy' or 'rent'.")
        sys.exit(1)

    print(f"=== Running Funda script ({offering_type}) ===")
    try:
        funda_results = funda_script.get_new_listings(offering_type)
    except Exception as e:
        print(f"[Funda] ERROR: {e}")
        funda_results = []

    print(f"=== Running Pararius script ({offering_type}) ===")
    try:
        pararius_results = pararius_script.get_new_listings(offering_type)
    except Exception as e:
        print(f"[Pararius] ERROR: {e}")
        pararius_results = []

    all_listings = deduplicate(funda_results + pararius_results)

    if all_listings:
        save_listings(all_listings, category)
        send_email(all_listings, offering_type)
    else:
        print("No new listings found.")
