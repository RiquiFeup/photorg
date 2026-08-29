"""
AI Organiser – core logic.

Groups photos first by EXIF capture date (like DayOrganiser), then
sub-groups each day folder by AI-detected scene type using CLIP
zero-shot classification.

Output structure::

    <destination>/<folder_title>/Day 01/Beach/photo_a.jpg
    <destination>/<folder_title>/Day 01/Museum/photo_b.jpg
    <destination>/<folder_title>/Day 02/Park/photo_c.jpg
    <destination>/<folder_title>/Day 02/Other/photo_d.jpg
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from threading import Event
from typing import Callable, Literal, Optional

from photorg.core.exif import get_capture_date
from photorg.core.file_utils import find_images, safe_copy, safe_move
from photorg.core.scene_model import SceneClassifier


class AIOrganiser:
    """Classifies and groups photos by date *and* AI-detected scene.

    Parameters
    ----------
    source:
        Directory containing the photos to organise.
    destination:
        Parent directory where the output structure will be created.
    folder_title:
        Human-readable name for the root output folder.
    places:
        Scene / place labels for classification
        (e.g. ``["beach", "museum", "park"]``).
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

        # Callbacks
        self.on_progress: Optional[Callable[[int, int, str], None]] = None
        self.on_complete: Optional[Callable[[int], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None

        self._cancel = Event()

    # ── public API ──────────────────────────────────────────────────────

    def cancel(self) -> None:
        """Request cancellation of the current run."""
        self._cancel.set()

    @property
    def is_cancelled(self) -> bool:
        return self._cancel.is_set()

    def run(self) -> None:
        """Execute the AI organisation process."""
        try:
            self._process()
        except Exception as exc:
            if self.on_error:
                self.on_error(str(exc))
            else:
                raise

    # ── internal ────────────────────────────────────────────────────────

    def _process(self) -> None:
        images = list(find_images(self.source))
        if not images:
            if self.on_error:
                self.on_error("No valid images found in the source folder.")
            return

        if not self.places:
            if self.on_error:
                self.on_error("No place tags provided for classification.")
            return

        # Load the scene classifier (lazy – first call downloads model)
        classifier = SceneClassifier()

        # Group by capture date
        date_groups: dict[str, list[Path]] = defaultdict(list)
        for img in images:
            dt = get_capture_date(img)
            key = dt.strftime("%Y-%m-%d") if dt else "Unknown Date"
            date_groups[key].append(img)

        valid_dates = sorted(d for d in date_groups if d != "Unknown Date")
        day_map = {d: f"Day {i:02d}" for i, d in enumerate(valid_dates, start=1)}
        day_map["Unknown Date"] = "Unknown Date"

        root = self.destination / self.folder_title
        transfer = safe_move if self.mode == "move" else safe_copy

        total = len(images)
        current = 0

        for date_str, imgs in date_groups.items():
            if self._cancel.is_set():
                return

            day_label = day_map[date_str]

            for img in imgs:
                if self._cancel.is_set():
                    return

                current += 1
                if self.on_progress:
                    self.on_progress(
                        current, total,
                        f"Classifying {img.name}…",
                    )

                # Classify the scene
                scene = classifier.classify(img, self.places)
                out_dir = root / day_label / scene
                transfer(img, out_dir / img.name)

        if self.on_complete:
            self.on_complete(total)
