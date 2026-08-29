"""
AI Organiser – core logic.

Groups media (photos **and** videos) first by EXIF/container capture
date (like DayOrganiser), then sub-groups each day folder by
AI-detected scene type using CLIP zero-shot classification.

For videos, only a single frame is extracted for classification
to keep RAM usage minimal.

Output structure::

    <destination>/<folder_title>/Day 01/Beach/photo_a.jpg
    <destination>/<folder_title>/Day 01/Beach/video_b.mov
    <destination>/<folder_title>/Day 01/Museum/photo_c.jpg
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from threading import Event
from typing import Callable, Literal, Optional

from photorg.core.exif import get_capture_date
from photorg.core.file_utils import find_media, safe_copy, safe_move, is_video
from photorg.core.scene_model import SceneClassifier


class AIOrganiser:
    """Classifies and groups media by date *and* AI-detected scene.

    Parameters
    ----------
    source:
        Directory containing the media files to organise.
    destination:
        Parent directory where the output structure will be created.
    folder_title:
        Human-readable name for the root output folder.
    places:
        Scene / place labels for classification.
    mode:
        ``"copy"`` preserves originals; ``"move"`` removes them.
    """

    def __init__(
        self,
        source: Path,
        destination: Path,
        folder_title: str,
        places: list[str],
        *,
        mode: Literal["copy", "move"] = "copy",
    ) -> None:
        self.source = source
        self.destination = destination
        self.folder_title = folder_title.strip()
        self.places = [p.strip().lower() for p in places if p.strip()]
        self.mode = mode

        self.on_progress: Optional[Callable[[int, int, str], None]] = None
        self.on_complete: Optional[Callable[[int], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None

        self._cancel = Event()

    def cancel(self) -> None:
        self._cancel.set()

    @property
    def is_cancelled(self) -> bool:
        return self._cancel.is_set()

    def run(self) -> None:
        try:
            self._process()
        except Exception as exc:
            if self.on_error:
                self.on_error(str(exc))
            else:
                raise

    def _process(self) -> None:
        media = list(find_media(self.source))
        if not media:
            if self.on_error:
                self.on_error("No valid images or videos found in the source folder.")
            return

        if not self.places:
            if self.on_error:
                self.on_error("No place tags provided for classification.")
            return

        classifier = SceneClassifier()

        # Group by capture date
        date_groups: dict[str, list[Path]] = defaultdict(list)
        for item in media:
            if is_video(item):
                from photorg.core.video_utils import get_video_date
                dt = get_video_date(item)
            else:
                dt = get_capture_date(item)
            key = dt.strftime("%Y-%m-%d") if dt else "Unknown Date"
            date_groups[key].append(item)

        valid_dates = sorted(d for d in date_groups if d != "Unknown Date")
        day_map = {d: f"Day {i:02d}" for i, d in enumerate(valid_dates, start=1)}
        day_map["Unknown Date"] = "Unknown Date"

        root = self.destination / self.folder_title
        transfer = safe_move if self.mode == "move" else safe_copy

        total = len(media)
        current = 0

        for date_str, items in date_groups.items():
            if self._cancel.is_set():
                return

            day_label = day_map[date_str]

            for item in items:
                if self._cancel.is_set():
                    return

                current += 1
                if self.on_progress:
                    self.on_progress(current, total, f"Classifying {item.name}…")

                # Classify: extract frame for videos, open image for photos
                if is_video(item):
                    from photorg.core.video_utils import extract_frame
                    frame = extract_frame(item)
                    if frame:
                        scene = classifier.classify_image(frame, self.places)
                    else:
                        scene = "Other"
                else:
                    scene = classifier.classify(item, self.places)

                out_dir = root / day_label / scene
                transfer(item, out_dir / item.name)

        if self.on_complete:
            self.on_complete(total)
