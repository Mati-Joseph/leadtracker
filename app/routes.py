from pathlib import Path

from flask import (
    Blueprint,
    Response,
    current_app,
    jsonify,
    request,
    send_from_directory,
)

from .collector import search_places
from .collector_osm import search_osm
from .emails import find_email
from .exporters import EXPORTERS
from .grouping import save_places
from .models import STATUSES, Business, db

bp = Blueprint("api", __name__)
PUBLIC_DIR = Path(__file__).resolve().parent.parent / "public"


def _filtered():
    q = Business.query
    status = request.args.get("status")
    if status:
        q = q.filter(Business.status == status)
    term = request.args.get("q")
    if term:
        q = q.filter(Business.name.ilike(f"%{term}%"))
    min_b = request.args.get("min_branches", 1, type=int)
    items = [b.to_dict() for b in q.order_by(Business.name).all()]
    return [b for b in items if b["branch_count"] >= min_b]


@bp.get("/")
def index():
    return send_from_directory(PUBLIC_DIR, "index.html")


@bp.get("/api/statuses")
def statuses():
    return jsonify(STATUSES)


@bp.get("/api/businesses")
def list_businesses():
    return jsonify(_filtered())


@bp.patch("/api/businesses/<int:bid>")
def update_business(bid):
    biz = db.get_or_404(Business, bid)
    data = request.get_json(silent=True) or {}
    if "status" in data:
        if data["status"] not in STATUSES:
            return jsonify(error="invalid status"), 400
        biz.status = data["status"]
    if "notes" in data:
        biz.notes = data["notes"]
    db.session.commit()
    return jsonify(biz.to_dict())


@bp.post("/api/collect")
def collect():
    query = (request.get_json(silent=True) or {}).get("query", "").strip()
    if not query:
        return jsonify(error="query required"), 400
    try:
        if current_app.config["LEAD_SOURCE"] == "google":
            places = search_places(query, current_app.config["GOOGLE_API_KEY"])
        else:
            places = search_osm(query)
    except ValueError as e:
        return jsonify(error=str(e)), 400
    except Exception as e:
        return jsonify(error=f"Places API error: {e}"), 502
    return jsonify(fetched=len(places), new_branches=save_places(places))


@bp.post("/api/businesses/<int:bid>/find-email")
def email_lookup(bid):
    biz = db.get_or_404(Business, bid)
    biz.email = find_email(biz.website) or biz.email
    db.session.commit()
    return jsonify(biz.to_dict())


@bp.get("/api/export/<fmt>")
def export(fmt):
    if fmt not in EXPORTERS:
        return jsonify(error="use csv, xlsx or pdf"), 400
    func, mime = EXPORTERS[fmt]
    return Response(
        func(_filtered()),
        mimetype=mime,
        headers={"Content-Disposition": f"attachment; filename=leads.{fmt}"},
    )
