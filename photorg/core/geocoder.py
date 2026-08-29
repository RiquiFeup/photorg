"""
Geocoding utilities for Photorg.

Provides reverse geocoding to translate GPS coordinates (latitude, longitude)
into human-readable place names or monuments.
Uses the free Nominatim (OpenStreetMap) API.
"""
from __future__ import annotations

import json
import time
import urllib.request
import urllib.error
import urllib.parse
from functools import lru_cache
from typing import Optional


# Rate limiting per Nominatim usage policy (max 1 request per second)
_LAST_REQUEST_TIME = 0.0

@lru_cache(maxsize=1024)
def reverse_geocode(lat: float, lon: float) -> Optional[str]:
    """Reverse geocode coordinates into a famous place, monument, or location name.

    Results are cached in memory.

    Args:
        lat: Latitude as a float.
        lon: Longitude as a float.

    Returns:
        A string representing the place name (e.g. "Eiffel Tower",
        "Copacabana"), or None if no suitable name is found or
        if the request fails.
    """
    global _LAST_REQUEST_TIME

    # Respect Nominatim's 1 request per second policy
    now = time.time()
    elapsed = now - _LAST_REQUEST_TIME
    if elapsed < 1.0:
        time.sleep(1.0 - elapsed)
    
    _LAST_REQUEST_TIME = time.time()

    url = (
        f"https://nominatim.openstreetmap.org/reverse"
        f"?lat={lat}&lon={lon}&format=jsonv2&zoom=18"
    )

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "PhotorgApp/1.0 (Contact: local-user@localhost)"}
    )

    try:
        with urllib.request.urlopen(req, timeout=5.0) as response:
            if response.status != 200:
                return None
            
            data = json.loads(response.read().decode("utf-8"))
            
            if "error" in data:
                return None

            # Look for specific high-value location types first
            address = data.get("address", {})
            
            # Prioritize specific types of places over general regions
            for key in ["tourism", "historic", "amenity", "leisure", "building", "natural", "beach", "park", "museum"]:
                if key in address:
                    return address[key]
            
            # Fallback to more general areas if specific spots aren't named
            for key in ["village", "town", "city_district", "suburb", "city"]:
                if key in address:
                    return address[key]

            return data.get("name") or data.get("display_name")
            
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError, OSError):
        return None
