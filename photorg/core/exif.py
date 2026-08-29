"""
EXIF extraction utilities.

Provides reliable capture-date extraction from image files with a
multi-level fallback chain:
  1. EXIF DateTimeOriginal  (tag 36867 in Exif sub-IFD 0x8769)
  2. EXIF DateTimeDigitized (tag 36868 in Exif sub-IFD 0x8769)
  3. EXIF DateTime          (tag 306 in root IFD)
  4. File modification timestamp (os.path.getmtime)
"""
from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from PIL import Image
from PIL.ExifTags import IFD


def get_capture_date(image_path: Path) -> Optional[datetime]:
    """Extract the capture date from an image file.

    Uses a fallback chain to maximise the chance of returning a
    meaningful date even when EXIF data is incomplete or absent.

    Args:
        image_path: Path to the image file.

    Returns:
        A ``datetime`` representing when the photo was taken, or
        ``None`` if no date could be determined at all.
    """
    try:
        with Image.open(image_path) as img:
            exif = img.getexif()
            if exif:
                # DateTimeOriginal / DateTimeDigitized live in the
                # Exif sub-IFD, NOT in the root IFD.
                exif_ifd = exif.get_ifd(IFD.Exif)
                date_str = exif_ifd.get(36867) or exif_ifd.get(36868)
                if not date_str:
                    # Fallback: root-IFD DateTime (tag 306)
                    date_str = exif.get(306)
                if date_str:
                    parsed = _parse_exif_datetime(date_str)
                    if parsed is not None:
                        return parsed
    except Exception:
        pass

    # Final fallback: file modification timestamp
    return _get_file_mtime(image_path)


def _parse_exif_datetime(date_str: str) -> Optional[datetime]:
    """Parse an EXIF datetime string, handling common format variations.

    Supported formats:
        - ``YYYY:MM:DD HH:MM:SS``     (standard EXIF)
        - ``YYYY-MM-DD HH:MM:SS``     (occasional variant)
        - ``YYYY:MM:DD HH:MM:SS.fff`` (sub-second precision)

    Returns ``None`` for unparseable or ``None`` input.
    """
    if date_str is None:
        return None
    for fmt in (
        "%Y:%m:%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y:%m:%d %H:%M:%S.%f",
    ):
        try:
            return datetime.strptime(str(date_str).strip(), fmt)
        except (ValueError, TypeError):
            continue
    return None


def _get_file_mtime(path: Path) -> Optional[datetime]:
    """Return file modification time as a datetime, or None on error."""
    try:
        mtime = os.path.getmtime(path)
        return datetime.fromtimestamp(mtime)
    except (OSError, ValueError):
        return None


def get_gps_coordinates(image_path: Path) -> Optional[tuple[float, float]]:
    """Extract GPS coordinates (latitude, longitude) from an image file.

    Returns:
        A tuple of (latitude, longitude) as floats, or ``None`` if GPS
        data is missing or invalid.
    """
    try:
        with Image.open(image_path) as img:
            exif = img.getexif()
            if not exif:
                return None

            gps_ifd = exif.get_ifd(IFD.GPSInfo)
            if not gps_ifd:
                return None

            # 1: GPSLatitudeRef, 2: GPSLatitude, 3: GPSLongitudeRef, 4: GPSLongitude
            lat_ref = gps_ifd.get(1)
            lat_dms = gps_ifd.get(2)
            lon_ref = gps_ifd.get(3)
            lon_dms = gps_ifd.get(4)

            if not all([lat_ref, lat_dms, lon_ref, lon_dms]):
                return None

            lat = _dms_to_decimal(lat_dms, lat_ref)
            lon = _dms_to_decimal(lon_dms, lon_ref)

            if lat is not None and lon is not None:
                return (lat, lon)
    except Exception:
        pass

    return None


def _dms_to_decimal(dms: tuple, ref: str) -> Optional[float]:
    """Convert degrees, minutes, seconds to decimal coordinates."""
    try:
        degrees = float(dms[0])
        minutes = float(dms[1])
        seconds = float(dms[2])

        decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
        
        ref = str(ref).strip().upper()
        if ref in ("S", "W"):
            decimal = -decimal
            
        return decimal
    except (IndexError, ValueError, TypeError):
        return None
