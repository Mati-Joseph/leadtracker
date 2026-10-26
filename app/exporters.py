import csv
import io
from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

COLUMNS = ["name", "branch_count", "support_phone", "email", "website", "status", "notes"]
HEADERS = ["Name", "Branches", "Phone", "Email", "Website", "Status", "Notes"]


def _rows(businesses):
    return [[b.get(c) or "" for c in COLUMNS] for b in businesses]


def to_csv(businesses):
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(HEADERS)
    w.writerows(_rows(businesses))
    return out.getvalue().encode("utf-8")


def to_xlsx(businesses):
    wb = Workbook()
    ws = wb.active
    ws.title = "Leads"
    ws.append(HEADERS)
    for r in _rows(businesses):
        ws.append(r)
    out = io.BytesIO()
    wb.save(out)
    return out.getvalue()


def to_pdf(businesses):
    out = io.BytesIO()
    doc = SimpleDocTemplate(out, pagesize=landscape(A4))
    data = [HEADERS] + [[str(c)[:40] for c in r] for r in _rows(businesses)]
    t = Table(data, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
    ]))
    doc.build([t])
    return out.getvalue()


EXPORTERS = {
    "csv": (to_csv, "text/csv"),
    "xlsx": (to_xlsx, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
    "pdf": (to_pdf, "application/pdf"),
}
