from app import create_app


def test_index_loads(tmp_path):
    app = create_app(str(tmp_path / "listings.db"))
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert b"PropertyScraper" in response.data


def test_scrape_route_saves_mocked_listing(tmp_path, monkeypatch):
    app = create_app(str(tmp_path / "listings.db"))
    client = app.test_client()

    class Result:
        ok = True
        error = None
        listing = {
            "url": "https://sfbay.craigslist.org/scz/apa/example.html",
            "address": "123 Ocean St",
            "title": "Mock Listing",
            "price": 2100,
            "beds": 1.0,
            "baths": 1.0,
            "sqft": 600,
            "distance_miles": None,
            "posted": "today",
        }

    monkeypatch.setattr("app.scrape_listing", lambda url, include_distance=False: Result())

    response = client.post(
        "/scrape",
        data={"urls": "https://sfbay.craigslist.org/scz/apa/example.html"},
    )

    assert response.status_code == 200
    assert b"Mock Listing" in response.data
