"""
Day Organiser – core logic.

Groups photos by EXIF capture date into sequential day folders.

Output structure::

    <destination>/<folder_title>/Day 01/photo_a.jpg
    <destination>/<folder_title>/Day 02/photo_b.jpg
    <destination>/<folder_title>/Unknown Date/photo_c.jpg
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from threading import Event
from typing import Callable, Literal, Optional

from photorg.core.exif import get_capture_date
from photorg.core.file_utils import find_media, safe_copy, safe_move, is_video


class DayOrganiser:
    """Groups photos by capture date into sequential day folders.

    Parameters
    ----------
    source:
        Directory containing the photos to organise.
    destination:
        Parent directory where the output structure will be created.
    folder_title:
        Human-readable name for the root output folder
        (e.g. "Italy Trip").
    mode:
        ``"copy"`` preserves originals; ``"move"`` removes them.
    """

    def __init__(
        self,
        source: Path,
        destination: Path,
        folder_title: str,
        *,
        mode: Literal["copy", "move"] = "copy",
    ) -> None:
        self.source = source
        self.destination = destination
        self.folder_title = folder_title.strip()
        self.mode = mode

        # Callbacks for UI updates
        self.on_progress: Optional[Callable[[int, int, str], None]] = None
        self.on_complete: Optional[Callable[[int], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None

        # Cancellation support
        self._cancel = Event()

    # ── public API ──────────────────────────────────────────────────────

    def cancel(self) -> None:
        """Request cancellation of the current run."""
        self._cancel.set()

    @property
    def is_cancelled(self) -> bool:
        return self._cancel.is_set()

    def run(self) -> None:
        """Execute the organisation process."""
        try:
            self._process()
        except Exception as exc:
            if self.on_error:
                self.on_error(str(exc))
            else:
                raise

    # ── internal ────────────────────────────────────────────────────────

    def _process(self) -> None:
        media = list(find_media(self.source))
        if not media:
            if self.on_error:
                self.on_error("No valid images or videos found in the source folder.")
            return

        # Group by date string
        date_groups: dict[str, list[Path]] = defaultdict(list)
        for item in media:
            if is_video(item):
                from photorg.core.video_utils import get_video_date
                dt = get_video_date(item)
            else:
                dt = get_capture_date(item)
            key = dt.strftime("%Y-%m-%d") if dt else "Unknown Date"
            date_groups[key].append(item)

        # Assign sequential Day labels
        valid_dates = sorted(d for d in date_groups if d != "Unknown Date")
        day_map = {d: f"Day {i:02d}" for i, d in enumerate(valid_dates, start=1)}
        day_map["Unknown Date"] = "Unknown Date"

        # Root output directory
        root = self.destination / self.folder_title
        transfer = safe_move if self.mode == "move" else safe_copy

        total = len(media)
        current = 0

        for date_str, imgs in date_groups.items():
            if self._cancel.is_set():
                return
            day_label = day_map[date_str]
            out_dir = root / day_label

            for img in imgs:
                if self._cancel.is_set():
                    return
                current += 1
                if self.on_progress:
                    self.on_progress(
                        current, total,
                        f"{'Moving' if self.mode == 'move' else 'Copying'} "
                        f"{img.name} → {day_label}",
                    )
                transfer(img, out_dir / img.name)

        if self.on_complete:
            self.on_complete(total)
