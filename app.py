from __future__ import annotations

from urllib.parse import urlparse

from io import BytesIO

from flask import Flask, render_template, request, send_file, url_for

from scraper import scrape_listing
from storage import DEFAULT_DB_NAME, export_listings_bytes, list_listings, save_to_sqlite


def create_app(db_name: str = DEFAULT_DB_NAME) -> Flask:
    app = Flask(__name__)
    app.config["DB_NAME"] = db_name
    app.config["SECRET_KEY"] = "property-scraper-local-dev"

    @app.get("/")
    def index():
        return render_template(
            "index.html",
            listings=list_listings(app.config["DB_NAME"]),
            messages=[],
        )

    @app.get("/listings")
    def listings():
        return render_template(
            "index.html",
            listings=list_listings(app.config["DB_NAME"]),
            messages=[],
        )

    @app.post("/scrape")
    def scrape():
        urls = parse_urls(request.form.get("urls", ""))
        include_distance = request.form.get("include_distance") == "on"
        messages = []
        listings_to_save = []

        if not urls:
            messages.append(
                {
                    "status": "error",
                    "text": "Paste at least one Craigslist listing URL.",
                }
            )

        for url in urls:
            result = scrape_listing(url, include_distance=include_distance)
            if result.ok and result.listing:
                listings_to_save.append(result.listing)
                messages.append(
                    {
                        "status": "success",
                        "text": f"Saved {result.listing.get('title') or url}",
                    }
                )
            else:
                messages.append(
                    {
                        "status": "error",
                        "text": f"{url}: {result.error}",
                    }
                )

        if listings_to_save:
            save_to_sqlite(listings_to_save, app.config["DB_NAME"])

        return render_template(
            "index.html",
            listings=list_listings(app.config["DB_NAME"]),
            messages=messages,
        )

    @app.get("/export.csv")
    def export_csv():
        return send_export(app.config["DB_NAME"], "csv")

    @app.get("/export.xlsx")
    def export_xlsx():
        return send_export(app.config["DB_NAME"], "xlsx")

    return app


def parse_urls(raw_urls: str) -> list[str]:
    urls = []
    seen = set()

    for line in raw_urls.splitlines():
        candidate = line.strip()
        if not candidate or candidate in seen:
            continue

        parsed = urlparse(candidate)
        if parsed.scheme in {"http", "https"} and parsed.netloc:
            urls.append(candidate)
            seen.add(candidate)

    return urls


def send_export(db_name: str, export_format: str):
    suffix = f".{export_format}"
    download_name = f"property-listings{suffix}"
    mimetype = (
        "text/csv"
        if export_format == "csv"
        else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    return send_file(
        BytesIO(export_listings_bytes(db_name, export_format)),
        as_attachment=True,
        download_name=download_name,
        mimetype=mimetype,
    )


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
