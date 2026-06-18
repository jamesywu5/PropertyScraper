from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Any

import requests
from bs4 import BeautifulSoup
from geopy.distance import geodesic
from geopy.geocoders import Nominatim


DEFAULT_DESTINATION_COORDS = (36.991, -122.060)
DEFAULT_TIMEOUT_SECONDS = 12
REQUEST_HEADERS = {
    "User-Agent": (
        "PropertyScraper/1.0 "
        "(portfolio project; contact: local-development@example.com)"
    )
}


@dataclass
class ScrapeResult:
    url: str
    ok: bool
    listing: dict[str, Any] | None = None
    error: str | None = None


def fetch_html(url: str, timeout: int = DEFAULT_TIMEOUT_SECONDS) -> str:
    """Fetch a listing page and return its HTML."""
    response = requests.get(url, headers=REQUEST_HEADERS, timeout=timeout)
    response.raise_for_status()
    return response.text


def soup_from_html(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


def text_or_none(soup: BeautifulSoup, selector: str) -> str | None:
    tag = soup.select_one(selector)
    return tag.get_text(" ", strip=True) if tag else None


def parse_address(soup: BeautifulSoup) -> str | None:
    return text_or_none(soup, "h2.street-address")


def parse_price(soup: BeautifulSoup) -> int | None:
    price = text_or_none(soup, "span.price")
    if not price:
        return None

    digits = re.sub(r"[^\d]", "", price)
    return int(digits) if digits else None


def parse_title(soup: BeautifulSoup) -> str | None:
    return text_or_none(soup, "span#titletextonly")


def parse_beds_baths_sqft(
    soup: BeautifulSoup,
) -> tuple[float | None, float | None, int | None]:
    important_text = " ".join(
        tag.get_text(" ", strip=True) for tag in soup.select("span.attr.important")
    )

    beds = parse_number(important_text, r"(\d+(?:\.\d+)?)\s*br\b")
    baths = parse_number(important_text, r"(\d+(?:\.\d+)?)\s*ba\b")
    sqft = parse_integer(important_text, r"([\d,]+)\s*ft2\b")

    return beds, baths, sqft


def parse_number(text: str, pattern: str) -> float | None:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return float(match.group(1)) if match else None


def parse_integer(text: str, pattern: str) -> int | None:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return int(match.group(1).replace(",", "")) if match else None


def parse_posted_time(soup: BeautifulSoup) -> str | None:
    tag = soup.select_one("time.date.timeago")
    if not tag:
        return None
    return tag.get("datetime") or tag.get_text(" ", strip=True) or None


def parse_listing_html(html: str, page_url: str) -> dict[str, Any]:
    soup = soup_from_html(html)
    beds, baths, sqft = parse_beds_baths_sqft(soup)

    return {
        "url": page_url,
        "address": parse_address(soup),
        "title": parse_title(soup),
        "price": parse_price(soup),
        "beds": beds,
        "baths": baths,
        "sqft": sqft,
        "distance_miles": None,
        "posted": parse_posted_time(soup),
    }


def compute_distance(
    address: str | None,
    dest_coords: tuple[float, float] = DEFAULT_DESTINATION_COORDS,
) -> float | None:
    """Compute miles from an address to a destination, returning None on failure."""
    if not address:
        return None

    try:
        geolocator = Nominatim(user_agent="property_scraper")
        location = geolocator.geocode(address, timeout=DEFAULT_TIMEOUT_SECONDS)
    except Exception:
        return None

    if not location:
        return None

    rental_coords = (location.latitude, location.longitude)
    return round(geodesic(rental_coords, dest_coords).miles, 2)


def get_destination_coords() -> tuple[float, float]:
    lat = float(os.getenv("PROPERTY_DEST_LAT", DEFAULT_DESTINATION_COORDS[0]))
    lng = float(os.getenv("PROPERTY_DEST_LNG", DEFAULT_DESTINATION_COORDS[1]))
    return lat, lng


def create_listing(
    page_url: str,
    *,
    include_distance: bool = False,
    destination_coords: tuple[float, float] | None = None,
) -> dict[str, Any]:
    html = fetch_html(page_url)
    listing = parse_listing_html(html, page_url)

    if include_distance:
        listing["distance_miles"] = compute_distance(
            listing["address"],
            destination_coords or get_destination_coords(),
        )

    return listing


def scrape_listing(
    page_url: str,
    *,
    include_distance: bool = False,
    destination_coords: tuple[float, float] | None = None,
) -> ScrapeResult:
    try:
        listing = create_listing(
            page_url,
            include_distance=include_distance,
            destination_coords=destination_coords,
        )
    except requests.RequestException as exc:
        return ScrapeResult(url=page_url, ok=False, error=f"Request failed: {exc}")
    except Exception as exc:
        return ScrapeResult(url=page_url, ok=False, error=f"Parse failed: {exc}")

    return ScrapeResult(url=page_url, ok=True, listing=listing)
