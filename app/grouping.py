"""Save branches and group them into Business rows (key = website domain, else name)."""
import re
from urllib.parse import urlparse
from .models import db, Branch, Business

_SUFFIX = re.compile(r"\b(ltd|limited|school|schools|driving|branch|co|company)\b", re.I)


def domain_of(url):
    if not url:
        return ""
    host = urlparse(url if "//" in url else "//" + url).netloc.lower()
    return host[4:] if host.startswith("www.") else host


def normalize_name(name):
    name = _SUFFIX.sub("", name.lower())
    return re.sub(r"[^a-z0-9]+", " ", name).strip()


def business_key(name, website):
    return domain_of(website) or normalize_name(name)


def save_places(places):
    """Upsert branches, attach each to a Business. Returns count of new branches."""
    added = 0
    for p in places:
        if Branch.query.filter_by(place_id=p["place_id"]).first():
            continue
        key = business_key(p["name"], p.get("website"))
        if not key:
            continue
        biz = Business.query.filter_by(key=key).first()
        if not biz:
            biz = Business(key=key, name=p["name"], website=p.get("website") or None)
            db.session.add(biz)
        if not biz.support_phone and p.get("phone"):
            biz.support_phone = p["phone"]
        biz.branches.append(Branch(
            place_id=p["place_id"], name=p["name"], address=p.get("address"),
            phone=p.get("phone"), website=p.get("website"),
        ))
        added += 1
        db.session.flush()
    db.session.commit()
    return added
