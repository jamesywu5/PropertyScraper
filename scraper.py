from bs4 import BeautifulSoup
import requests
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import re


def fetch_page(url: str) -> BeautifulSoup:
    """Fetch a page and return a BeautifulSoup object."""
    page = requests.get(url)
    return BeautifulSoup(page.content, "html.parser")


def parse_address(soup: BeautifulSoup) -> str | None:
    tag = soup.find("h2", class_="street-address")
    return tag.get_text(strip=True) if tag else None


def parse_price(soup: BeautifulSoup) -> int | None:
    tag = soup.find("span", class_="price")
    if not tag:
        return None
    price = tag.get_text(strip=True)
    return int(re.sub(r"[^\d]", "", price))


def parse_title(soup: BeautifulSoup) -> str | None:
    tag = soup.find("span", id="titletextonly")
    return tag.get_text(strip=True) if tag else None


def parse_bedbath_sqft(soup: BeautifulSoup) -> tuple[str | None, str | None]:
    tags = soup.find_all("span", class_="attr important")
    bedbath = tags[0].get_text(strip=True) if len(tags) > 0 else None
    sqft = tags[1].get_text(strip=True) if len(tags) > 1 else None
    return bedbath, sqft


def parse_posted_time(soup: BeautifulSoup) -> str | None:
    tag = soup.find("time", class_="date timeago")
    return tag.get_text(strip=True) if tag else None


def compute_distance(address: str | None, dest_coords=(36.991, -122.060)) -> float | None:
    """Compute distance in miles from address to destination coordinates."""
    if not address:
        return None
    geolocator = Nominatim(user_agent="property_scraper")
    location = geolocator.geocode(address)
    if not location:
        return None
    rental_coords = (location.latitude, location.longitude)
    return round(geodesic(rental_coords, dest_coords).miles, 2)


def create_listing(page_url: str) -> dict:
    """
    Creates a listing dictionary of linked residence.

    Args:
        page_url (string): Link of residence on housing feed
    
    Returns:
        listing (dict): Dictionary of listing info
    """
    soup = fetch_page(page_url)

    address = parse_address(soup)
    price = parse_price(soup)
    title = parse_title(soup)
    bedbath, sqft = parse_bedbath_sqft(soup)
    posted_time = parse_posted_time(soup)
    distance = compute_distance(address)

    listing = {
        "url": page_url,
        "address": address,
        "title": title,
        "price": price,
        "bedbath": bedbath,
        "sqft": sqft,
        "distance": distance,
        "posted": posted_time,
    }

    return listing
