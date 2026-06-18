from __future__ import annotations

import sqlite3
from io import BytesIO, StringIO
from pathlib import Path
from typing import Any

import pandas as pd


DEFAULT_DB_NAME = "listings.db"
LISTING_COLUMNS = [
    "url",
    "address",
    "title",
    "price",
    "beds",
    "baths",
    "sqft",
    "distance_miles",
    "posted",
]


def get_connection(db_name: str = DEFAULT_DB_NAME) -> sqlite3.Connection:
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    ensure_schema(conn)
    return conn


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE NOT NULL,
            address TEXT,
            title TEXT,
            price INTEGER,
            beds REAL,
            baths REAL,
            sqft INTEGER,
            distance_miles REAL,
            posted TEXT,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    existing_columns = {
        row["name"] for row in conn.execute("PRAGMA table_info(listings)").fetchall()
    }
    migrations = {
        "beds": "ALTER TABLE listings ADD COLUMN beds REAL",
        "baths": "ALTER TABLE listings ADD COLUMN baths REAL",
        "distance_miles": "ALTER TABLE listings ADD COLUMN distance_miles REAL",
        "updated_at": (
            "ALTER TABLE listings ADD COLUMN updated_at TEXT "
            "NOT NULL DEFAULT CURRENT_TIMESTAMP"
        ),
    }
    for column, statement in migrations.items():
        if column not in existing_columns:
            conn.execute(statement)

    conn.commit()


def save_to_sqlite(
    listings: list[dict[str, Any]],
    db_name: str = DEFAULT_DB_NAME,
) -> None:
    with get_connection(db_name) as conn:
        upsert_listings(conn, listings)


def upsert_listings(
    conn: sqlite3.Connection,
    listings: list[dict[str, Any]],
) -> None:
    for listing in listings:
        values = {column: listing.get(column) for column in LISTING_COLUMNS}
        conn.execute(
            """
            INSERT INTO listings
            (url, address, title, price, beds, baths, sqft, distance_miles, posted)
            VALUES
            (:url, :address, :title, :price, :beds, :baths, :sqft, :distance_miles, :posted)
            ON CONFLICT(url) DO UPDATE SET
                address = excluded.address,
                title = excluded.title,
                price = excluded.price,
                beds = excluded.beds,
                baths = excluded.baths,
                sqft = excluded.sqft,
                distance_miles = excluded.distance_miles,
                posted = excluded.posted,
                updated_at = CURRENT_TIMESTAMP
            """,
            values,
        )
    conn.commit()


def list_listings(db_name: str = DEFAULT_DB_NAME) -> list[dict[str, Any]]:
    with get_connection(db_name) as conn:
        rows = conn.execute(
            """
            SELECT url, address, title, price, beds, baths, sqft, distance_miles, posted
            FROM listings
            ORDER BY COALESCE(price, 999999999), title
            """
        ).fetchall()
    return [dict(row) for row in rows]


def save_to_csv(listings: list[dict[str, Any]], filename: str = "listings.csv") -> None:
    listings_dataframe(listings).to_csv(filename, index=False)


def save_to_excel(
    listings: list[dict[str, Any]],
    filename: str = "listings.xlsx",
) -> None:
    listings_dataframe(listings).to_excel(filename, index=False)


def listings_dataframe(listings: list[dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(listings, columns=LISTING_COLUMNS)


def export_listings(
    db_name: str,
    filename: str | Path,
    export_format: str,
) -> Path:
    path = Path(filename)
    listings = list_listings(db_name)

    if export_format == "csv":
        save_to_csv(listings, str(path))
    elif export_format == "xlsx":
        save_to_excel(listings, str(path))
    else:
        raise ValueError(f"Unsupported export format: {export_format}")

    return path


def export_listings_bytes(db_name: str, export_format: str) -> bytes:
    listings = list_listings(db_name)
    df = listings_dataframe(listings)

    if export_format == "csv":
        buffer = StringIO()
        df.to_csv(buffer, index=False)
        return buffer.getvalue().encode("utf-8")

    if export_format == "xlsx":
        buffer = BytesIO()
        df.to_excel(buffer, index=False)
        return buffer.getvalue()

    raise ValueError(f"Unsupported export format: {export_format}")
