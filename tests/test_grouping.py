from app.grouping import domain_of, normalize_name, save_places
from app.models import Business


def P(pid, name, site, phone="0700"):
    return {"place_id": pid, "name": name, "address": "x " + pid, "phone": phone, "website": site}


def test_domain_of():
    assert domain_of("https://www.abc.co.ke/contact") == "abc.co.ke"
    assert domain_of("") == ""


def test_normalize_name():
    assert normalize_name("ABC Driving School Ltd") == "abc"


def test_groups_branches_by_domain_and_name(app):
    with app.app_context():
        n = save_places([
            P("1", "ABC Driving School Westlands", "https://abc.co.ke"),
            P("2", "ABC Driving School Thika", "https://www.abc.co.ke/thika"),
            P("3", "Solo Motors School", ""),
            P("1", "dup", "https://abc.co.ke"),  # duplicate place_id ignored
        ])
        assert n == 3
        abc = Business.query.filter_by(key="abc.co.ke").one()
        assert len(abc.branches) == 2
        assert Business.query.count() == 2
