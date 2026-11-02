# Lead Tracker

Find businesses with 2+ branches (Google Places), grab a contact email from their website, track outreach status, export CSV/Excel/PDF.

## Setup (Ubuntu)

```bash
pipx install pipenv
pipenv install --dev            # installs from Pipfile.lock
cp .env.example .env            # then edit values
pipenv run flask --app app run --debug
```

````
Open http://127.0.0.1:5000

## Tests
```bash
pytest -q
````

## Notes

- Only collect business contact details; keep a `do_not_contact` status and honour opt-outs (Kenya DPA 2019).
- Email lookup respects robots.txt and only reads the homepage/contact/about pages.
- Set a budget alert in Google Cloud before collecting at scale.
- Lead source is set by `LEAD_SOURCE` in `.env`: `osm` (default, free, no key) or `google` (needs `GOOGLE_API_KEY` and billing).
- Optional `OVERPASS_URL` overrides the Overpass server.
# leadtracker
