from pathlib import Path

from storage import export_listings, list_listings, save_to_sqlite


def listing(url: str, title: str, price: int) -> dict:
    return {
        "url": url,
        "address": "123 Ocean St",
        "title": title,
        "price": price,
        "beds": 1.0,
        "baths": 1.0,
        "sqft": 600,
        "distance_miles": None,
        "posted": "today",
    }


def test_sqlite_insert_and_update(tmp_path: Path):
    db_path = tmp_path / "listings.db"
    url = "https://sfbay.craigslist.org/scz/apa/example.html"

    save_to_sqlite([listing(url, "Original", 2000)], str(db_path))
    save_to_sqlite([listing(url, "Updated", 2250)], str(db_path))

    listings = list_listings(str(db_path))
    assert len(listings) == 1
    assert listings[0]["title"] == "Updated"
    assert listings[0]["price"] == 2250


def test_export_csv_and_xlsx(tmp_path: Path):
    db_path = tmp_path / "listings.db"
    csv_path = tmp_path / "listings.csv"
    xlsx_path = tmp_path / "listings.xlsx"

    save_to_sqlite(
        [listing("https://sfbay.craigslist.org/scz/apa/example.html", "Export me", 2100)],
        str(db_path),
    )

    export_listings(str(db_path), csv_path, "csv")
    export_listings(str(db_path), xlsx_path, "xlsx")

    assert csv_path.exists()
    assert "Export me" in csv_path.read_text(encoding="utf-8")
    assert xlsx_path.exists()
    assert xlsx_path.stat().st_size > 0
