from bs4 import BeautifulSoup
import requests
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import re


def create_listing(page_url):
    """
    Creates a listing dictionary of linked residence.

    Args:
        page_url (string): Link of residence on housing feed
    
    Returns:
        listing (dict): Dictionary of listing info
    """
    page = requests.get(page_url)

    soup = BeautifulSoup(page.content, 'html.parser')

    with open("debug/page_debug.html", "w", encoding="utf-8") as f:
        f.write(soup.prettify())

    address_tag = soup.find("h2", class_="street-address")
    address = address_tag.get_text(strip=True) if address_tag else None

    price_tag = soup.find("span", class_="price")
    price = price_tag.get_text(strip=True) if price_tag else None
    if price:
        price_int = int(re.sub(r"[^\d]", "", price))
    else:
        price_int = None

    title_tag = soup.find("span", id="titletextonly")
    title = title_tag.get_text(strip=True) if title_tag else None

    bedbath_sqft = soup.find_all("span", class_="attr important")
    bedbath = bedbath_sqft[0].get_text(strip=True) if len(bedbath_sqft) > 0 else None
    sqft = bedbath_sqft[1].get_text(strip=True) if len(bedbath_sqft) > 1 else None

    posted_tag = soup.find("time", class_="date timeago")
    posted_time = posted_tag.get_text(strip=True) if posted_tag else None

    #Distance calculation
    geolocator = Nominatim(user_agent="property_scraper")
    location = geolocator.geocode(address)

    rental_coords = (location.latitude, location.longitude)
    destination_coords = (36.991, -122.060)

    distance_miles = geodesic(rental_coords, destination_coords).miles
    rounded_distance = round(distance_miles, 2)

    listing = {
        "url": page_url,
        "address": address,
        "title": title,
        "price": price_int,
        "bedbath": bedbath,
        "sqft": sqft,
        "distance": rounded_distance,
        "posted": posted_time
    }

    return listing

page_url = 'https://sfbay.craigslist.org/scz/apa/d/santa-cruz-two-bedroom-house-for-rent/7885624254.html'

listing = create_listing(page_url)
print(listing)
