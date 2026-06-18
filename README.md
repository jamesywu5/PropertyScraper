# PropertyScraper

PropertyScraper is a local Flask app for comparing rental listings. Paste Craigslist
listing URLs, scrape the important details, save them to SQLite, filter/sort the
table, and export results to CSV or Excel.

## Features

- Paste one or more individual Craigslist listing URLs
- Normalize title, price, beds, baths, square footage, address, posted date, and
  optional distance from a configured destination
- Save listings with SQLite upserts so repeated scrapes refresh existing rows
- Filter and sort saved listings in the browser
- Export saved listings as CSV or XLSX
- Test parsing with local HTML fixtures instead of live web requests

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run

```powershell
flask --app app run --debug
```

Then open http://127.0.0.1:5000.

## Configuration

Distance calculation is optional in the UI. It defaults to coordinates near Santa
Cruz:

```powershell
$env:PROPERTY_DEST_LAT="36.991"
$env:PROPERTY_DEST_LNG="-122.060"
```

## Test

```powershell
pytest
```


