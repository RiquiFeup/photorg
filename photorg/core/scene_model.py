"""
Scene classification model.

Uses CLIP (``openai/clip-vit-base-patch32``) for **zero-shot** image
classification against user-defined place / scene labels.  This lets
users type arbitrary tags like "beach", "museum", "park" and the model
will match photos to the closest label without any fine-tuning.

Falls back to ``"Other"`` if no label scores above the confidence
threshold.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from PIL import Image


class SceneClassifier:
    """Zero-shot scene classifier backed by CLIP.

    The model is **lazy-loaded** on the first call to :meth:`classify`
    to avoid paying startup cost if the feature is never used.

    Parameters
    ----------
    confidence_threshold:
        Minimum softmax probability for the best label.  Below this
        the image is classified as ``"Other"``.
    """

    def __init__(self, confidence_threshold: float = 0.15) -> None:
        self._model = None
        self._processor = None
        self._threshold = confidence_threshold

    # ── lazy loading ────────────────────────────────────────────────────

    def _ensure_model(self) -> None:
        """Load the CLIP model if it hasn't been loaded yet."""
        if self._model is not None:
            return
        try:
            from transformers import CLIPModel, CLIPProcessor
        except ImportError:
            raise RuntimeError(
                "AI classification requires the 'transformers' and "
                "'torch' packages.  Install with:\n"
                "  pip install transformers torch"
            )
        model_name = "openai/clip-vit-base-patch32"
        self._processor = CLIPProcessor.from_pretrained(model_name)
        self._model = CLIPModel.from_pretrained(model_name)

    # ── public API ──────────────────────────────────────────────────────

    def classify(self, image_path: Path, labels: list[str]) -> str:
        """Classify an image against user-defined scene labels.

        Args:
            image_path: Path to the image file.
            labels: Scene / place labels provided by the user
                    (e.g. ``["beach", "museum", "park"]``).

        Returns:
            The best-matching label (title-cased), or ``"Other"`` if
            confidence is below the threshold for every label.
        """
        image = Image.open(image_path).convert("RGB")
        return self.classify_image(image, labels)

    def classify_image(self, image: Image.Image, labels: list[str]) -> str:
        """Classify a PIL Image against user-defined scene labels.

        This is the core classification method.  :meth:`classify` is a
        convenience wrapper that opens a file from disk first.

        Args:
            image: A PIL Image (already loaded into memory).
            labels: Scene / place labels.

        Returns:
            The best-matching label (title-cased), or ``"Other"``.
        """
        self._ensure_model()
        import torch

        rgb = image.convert("RGB")
        prompts = [f"a photo of a {label}" for label in labels]

        inputs = self._processor(
            text=prompts, images=rgb, return_tensors="pt", padding=True,
        )
        with torch.no_grad():
            outputs = self._model(**inputs)

        logits = outputs.logits_per_image[0]
        probs = logits.softmax(dim=0)
        best_idx = probs.argmax().item()
        best_prob = probs[best_idx].item()

        if best_prob < self._threshold:
            return "Other"
        return labels[best_idx].strip().title()
