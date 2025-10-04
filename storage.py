import pandas as pd
import sqlite3

def save_to_csv(listings: list[dict], filename: str = "listings.csv") -> None:
    df = pd.DataFrame(listings)
    df.to_csv(filename, index=False)

def save_to_excel(listings: list[dict], filename: str = "listings.xlsx") -> None:
    df = pd.DataFrame(listings)
    df.to_excel(filename, index=False)

def save_to_sqlite(listings: list[dict], db_name: str = "listings.db") -> None:
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            address TEXT,
            title TEXT,
            price INTEGER,
            bedbath TEXT,
            sqft TEXT,
            distance REAL,
            posted TEXT
        )
    """)

    for listing in listings:
        cur.execute("""
            INSERT OR IGNORE INTO listings
            (url, address, title, price, bedbath, sqft, distance, posted)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            listing["url"], listing["address"], listing["title"], listing["price"],
            listing["bedbath"], listing["sqft"], listing["distance"], listing["posted"]
        ))

    conn.commit()
    conn.close()


