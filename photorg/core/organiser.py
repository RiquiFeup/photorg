"""
Day Organiser – core logic.
"""
from __future__ import annotations
from pathlib import Path
from collections import defaultdict
from typing import Callable

from photorg.core.exif import get_capture_date
from photorg.core.file_utils import find_images, safe_copy


class DayOrganiser:
    """Groups photos by capture date into sequential day folders."""

    def __init__(
        self,
        source: Path,
        destination: Path,
        folder_title: str,
    ) -> None:
        self.source = source
        self.destination = destination
        self.folder_title = folder_title
        
        # Callbacks for UI updates
        self.on_progress: Callable[[int, int, str], None] | None = None
        self.on_complete: Callable[[], None] | None = None
        self.on_error: Callable[[str], None] | None = None

    def run(self) -> None:
        """Execute the organisation process."""
        try:
            self._process()
        except Exception as e:
            if self.on_error:
                self.on_error(str(e))
            else:
                raise

    def _process(self) -> None:
        # 1. Gather all images
        images = list(find_images(self.source))
        if not images:
            if self.on_error:
                self.on_error("No valid images found in the source folder.")
            return

        # 2. Group by date (YYYY-MM-DD)
        date_groups: dict[str, list[Path]] = defaultdict(list)
        for img in images:
            dt = get_capture_date(img)
            date_str = dt.strftime("%Y-%m-%d") if dt else "Unknown Date"
            date_groups[date_str].append(img)

        # 3. Sort dates to determine 'Day NN' map
        valid_dates = sorted([d for d in date_groups.keys() if d != "Unknown Date"])
        day_mapping = {d: f"Day {i:02d}" for i, d in enumerate(valid_dates, start=1)}
        day_mapping["Unknown Date"] = "Unknown Date"

        # 4. Execute copies
        total = len(images)
        current = 0

        for date_str, imgs in date_groups.items():
            day_label = day_mapping[date_str]
            out_folder_name = f"{self.folder_title} - {day_label}"
            out_dir = self.destination / out_folder_name

            for img in imgs:
                current += 1
                if self.on_progress:
                    self.on_progress(current, total, f"Copying {img.name} to {day_label}...")
                
                dest_path = out_dir / img.name
                safe_copy(img, dest_path)

        if self.on_complete:
            self.on_complete()
