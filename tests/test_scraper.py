from pathlib import Path

from scraper import parse_listing_html


FIXTURES = Path(__file__).parent / "fixtures"


def fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def test_parse_full_listing():
    listing = parse_listing_html(
        fixture("full_listing.html"),
        "https://sfbay.craigslist.org/scz/apa/full.html",
    )

    assert listing == {
        "url": "https://sfbay.craigslist.org/scz/apa/full.html",
        "address": "123 Ocean St, Santa Cruz, CA",
        "title": "Sunny Westside Studio",
        "price": 2450,
        "beds": 1.0,
        "baths": 1.0,
        "sqft": 620,
        "distance_miles": None,
        "posted": "2026-06-15T10:30:00-0700",
    }


def test_parse_missing_fields_as_none():
    listing = parse_listing_html(
        fixture("missing_fields.html"),
        "https://sfbay.craigslist.org/scz/apa/missing.html",
    )

    assert listing["address"] is None
    assert listing["price"] is None
    assert listing["beds"] is None
    assert listing["baths"] is None
    assert listing["sqft"] is None
    assert listing["posted"] == "today"


def test_parse_malformed_price_as_none():
    listing = parse_listing_html(
        fixture("malformed_price.html"),
        "https://sfbay.craigslist.org/scz/apa/malformed.html",
    )

    assert listing["price"] is None
    assert listing["beds"] == 2.0
    assert listing["baths"] == 1.5
    assert listing["sqft"] == 1100
