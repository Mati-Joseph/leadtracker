from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

STATUSES = [
    "new", "contacted", "waiting_response", "replied",
    "meeting", "won", "rejected", "do_not_contact",
]


def _now():
    return datetime.now(timezone.utc)


class Business(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(255), unique=True, nullable=False)  # domain or normalized name
    name = db.Column(db.String(255), nullable=False)
    website = db.Column(db.String(500))
    email = db.Column(db.String(255))
    support_phone = db.Column(db.String(50))
    status = db.Column(db.String(30), default="new", nullable=False)
    notes = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=_now)
    updated_at = db.Column(db.DateTime, default=_now, onupdate=_now)
    branches = db.relationship("Branch", backref="business", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "website": self.website,
            "email": self.email, "support_phone": self.support_phone,
            "status": self.status, "notes": self.notes,
            "branch_count": len(self.branches),
            "branches": [b.address for b in self.branches],
        }


class Branch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey("business.id"))
    place_id = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(500))
    phone = db.Column(db.String(50))
    website = db.Column(db.String(500))
