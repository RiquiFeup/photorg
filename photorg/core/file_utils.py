"""
File system operations for Photorg.
"""
import shutil
from pathlib import Path
from typing import Iterator

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".heic"}

def find_images(directory: Path) -> Iterator[Path]:
    """Yield all valid image files in a directory recursively."""
    if not directory.exists() or not directory.is_dir():
        return
    for file in directory.rglob("*"):
        if file.is_file() and file.suffix.lower() in VALID_EXTENSIONS:
            yield file

def safe_copy(src: Path, dest: Path) -> Path:
    """Copy file to dest, appending a number if the file already exists."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    final_dest = dest
    counter = 1
    while final_dest.exists():
        final_dest = dest.parent / f"{dest.stem}_{counter}{dest.suffix}"
        counter += 1
    shutil.copy2(src, final_dest)
    return final_dest
