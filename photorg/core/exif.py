"""
EXIF extraction utilities.
"""
from pathlib import Path
from datetime import datetime
from PIL import Image

def get_capture_date(image_path: Path) -> datetime | None:
    """Extract DateTimeOriginal from EXIF, or None if missing."""
    try:
        with Image.open(image_path) as img:
            exif = img.getexif()
            if not exif:
                return None
            # 36867 is DateTimeOriginal
            date_str = exif.get(36867)
            if not date_str:
                return None
            # Format: 'YYYY:MM:DD HH:MM:SS'
            return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
    except Exception:
        return None
