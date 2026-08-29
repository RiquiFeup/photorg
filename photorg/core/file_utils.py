"""
File system operations for Photorg.

Centralises image discovery and safe file-copying logic so that
both the Day Organiser and AI Organiser share the same behaviour.
"""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import Iterator

# Register HEIC/HEIF opener with Pillow (no-op if not installed)
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:
    pass

VALID_EXTENSIONS = frozenset({
    ".jpg", ".jpeg", ".png", ".heic", ".heif",
    ".webp", ".bmp", ".gif", ".tiff", ".tif",
})


def find_images(directory: Path) -> Iterator[Path]:
    """Yield all valid image files in *directory*, recursively.

    Silently returns nothing if the path does not exist or is not
    a directory.
    """
    if not directory.exists() or not directory.is_dir():
        return
    for file in directory.rglob("*"):
        if file.is_file() and file.suffix.lower() in VALID_EXTENSIONS:
            yield file


def safe_copy(src: Path, dest: Path) -> Path:
    """Copy *src* to *dest*, appending ``_N`` on filename collision.

    Parent directories are created automatically.  File metadata
    (timestamps, permissions) is preserved via ``shutil.copy2``.

    Returns the actual destination ``Path`` (which may differ from
    *dest* if a collision occurred).
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    final = dest
    counter = 1
    while final.exists():
        final = dest.parent / f"{dest.stem}_{counter}{dest.suffix}"
        counter += 1
    shutil.copy2(src, final)
    return final


def safe_move(src: Path, dest: Path) -> Path:
    """Move *src* to *dest*, appending ``_N`` on filename collision.

    Like :func:`safe_copy` but removes the source file after a
    successful transfer.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    final = dest
    counter = 1
    while final.exists():
        final = dest.parent / f"{dest.stem}_{counter}{dest.suffix}"
        counter += 1
    shutil.move(str(src), str(final))
    return final
