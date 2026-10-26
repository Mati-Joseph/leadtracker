from app.emails import extract_emails, pick_best

HTML = """<p>Mail info@abc.co.ke or bob@gmail.com</p>
<a href="mailto:sales@abc.co.ke?subject=Hi">x</a><img src="logo@2x.png">"""


def test_extract_emails():
    assert extract_emails(HTML) == {"info@abc.co.ke", "bob@gmail.com", "sales@abc.co.ke"}


def test_pick_best_prefers_same_domain_and_generic_inbox():
    emails = extract_emails(HTML)
    assert pick_best(emails, "abc.co.ke") == "info@abc.co.ke"
    assert pick_best(set(), "abc.co.ke") is None
