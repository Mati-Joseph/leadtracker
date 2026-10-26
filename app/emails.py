"""Find a contact email on a business website (respects robots.txt)."""
import re
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
import requests
from bs4 import BeautifulSoup

UA = "LeadTrackerBot/0.1 (contact research)"
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
BAD_TLDS = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".css", ".js")
PATHS = ["", "/contact", "/contact-us", "/about"]
PREFERRED = ("info", "contact", "hello", "support", "admin", "enquiries", "bookings")


def allowed(url):
    p = urlparse(url)
    rp = RobotFileParser(f"{p.scheme}://{p.netloc}/robots.txt")
    try:
        rp.read()
    except Exception:
        return True
    return rp.can_fetch(UA, url)


def extract_emails(html):
    soup = BeautifulSoup(html, "html.parser")
    found = set(EMAIL_RE.findall(soup.get_text(" ")))
    for a in soup.select('a[href^="mailto:"]'):
        found.update(EMAIL_RE.findall(a["href"].split("?")[0]))
    return {e.lower() for e in found if not e.lower().endswith(BAD_TLDS)}


def pick_best(emails, site_domain):
    if not emails:
        return None
    same = [e for e in emails if e.split("@")[1].endswith(site_domain)] or list(emails)
    same.sort(key=lambda e: (e.split("@")[0] not in PREFERRED, e))
    return same[0]


def find_email(website):
    if not website:
        return None
    base = website if "//" in website else "https://" + website
    domain = urlparse(base).netloc.lower().removeprefix("www.")
    emails = set()
    for path in PATHS:
        url = urljoin(base, path)
        if not allowed(url):
            continue
        try:
            r = requests.get(url, headers={"User-Agent": UA}, timeout=10)
            if r.ok:
                emails |= extract_emails(r.text)
        except requests.RequestException:
            continue
    return pick_best(emails, domain)
