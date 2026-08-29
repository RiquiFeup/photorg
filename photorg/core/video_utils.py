"""
Video utilities for Photorg.

Provides lightweight single-frame extraction from video files
for AI classification, and creation-date extraction from video
container metadata.

Only one frame is ever loaded into memory at a time to avoid
excessive RAM usage.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

from PIL import Image


def extract_frame(video_path: Path, timestamp_sec: float = 1.0) -> Optional[Image.Image]:
    """Extract a single frame from *video_path* at *timestamp_sec*.

    Uses ``imageio`` with the ffmpeg backend.  Only one frame is read
    and immediately converted to a PIL Image, keeping memory usage
    minimal regardless of video length or resolution.

    Returns ``None`` if the video cannot be read.
    """
    try:
        import imageio.v3 as iio

        # Read a single frame at the given timestamp
        # index=0 reads the first frame; for a specific timestamp
        # we use the plugin's seek capabilities
        frames = iio.imread(
            video_path,
            plugin="pyav",
            index=int(timestamp_sec * 30),  # approximate frame at ~30fps
        )
        return Image.fromarray(frames)
    except Exception:
        try:
            # Fallback: just read the very first frame
            import imageio.v3 as iio
            frame = iio.imread(video_path, plugin="pyav", index=0)
            return Image.fromarray(frame)
        except Exception:
            return None


def get_video_date(video_path: Path) -> Optional[datetime]:
    """Extract creation date from video container metadata.

    Tries to read the ``creation_time`` metadata tag from the
    video container using imageio/pyav.

    Falls back to file modification time if metadata is unavailable.
    """
    try:
        import imageio.v3 as iio

        meta = iio.immeta(video_path, plugin="pyav")
        creation_time = meta.get("creation_time") or meta.get("date")
        if creation_time:
            if isinstance(creation_time, datetime):
                return creation_time
            # Try to parse string format
            for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ",
                        "%Y-%m-%d %H:%M:%S", "%Y:%m:%d %H:%M:%S"):
                try:
                    return datetime.strptime(str(creation_time), fmt)
                except ValueError:
                    continue
    except Exception:
        pass

    # Fallback to file modification time
    try:
        import os
        mtime = os.path.getmtime(video_path)
        return datetime.fromtimestamp(mtime)
    except OSError:
        return None
