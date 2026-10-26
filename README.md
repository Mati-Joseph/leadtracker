# Lead Tracker

Find businesses with 2+ branches (Google Places), grab a contact email from their website, track outreach status, export CSV/Excel/PDF.

## Setup (Ubuntu)
```bash
python3 -m venv .venv && source .venv/bin/activate   # fish: source .venv/bin/activate.fish
pip install -r requirements.txt
export GOOGLE_API_KEY=your_key                        # fish: set -x GOOGLE_API_KEY your_key
flask --app app run --debug
```
Open http://127.0.0.1:5000

## Tests
```bash
pytest -q
```

## Notes
- Only collect business contact details; keep a `do_not_contact` status and honour opt-outs (Kenya DPA 2019).
- Email lookup respects robots.txt and only reads the homepage/contact/about pages.
- Set a budget alert in Google Cloud before collecting at scale.
