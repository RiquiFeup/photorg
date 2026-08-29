# Photorg

> Auto-organise vacation photos and videos into date-based folders, with intelligent AI scene grouping, GPS reverse-geocoding, and burst-photo optimization.

![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![PySide6](https://img.shields.io/badge/PySide6-6.8%2B-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## 🚀 Features

| Feature | Description |
|---|---|
| **Day Organizer** | Accurately reads EXIF `DateTimeOriginal` to sort media into `<Title> / Day 01 / ...` |
| **AI Scene Organizer** | Uses a zero-shot AI vision model (CLIP) to group photos by scene based on custom tags (beach, museum, park…) |
| **Video Support** | Efficiently parses `.mov`, `.mp4` etc. Extracts a single frame without loading the full video to save RAM during AI classification. |
| **GPS Reverse Geocoding** | Reads GPS metadata. If a famous place is detected (e.g., "Eiffel Tower"), it names the folder accordingly and skips heavy AI processing. |
| **Burst Optimization** | Intelligently groups rapid-fire shots (within 60s) into bursts. Only runs AI on the first photo and applies the tag to the rest, saving ~80% processing time. |
| **Output Preview** | Browse the generated folder structure interactively inside the app before exploring in the OS. |

---

## 🛠️ Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/RiquiFeup/photorg.git
cd photorg

# 2. Create & activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1        # Windows PowerShell
# source venv/bin/activate         # macOS / Linux

# 3. Install dependencies (with CPU PyTorch to save space)
pip install "torch>=2.0.0" torchvision --extra-index-url https://download.pytorch.org/whl/cpu
pip install -e .

# 4. Run the application
python -m photorg
```

---

## 📦 Build Distributable Executable (For your friends)

To create a standalone `.exe` that your friend can run without installing Python, use the configured PyInstaller spec file. This correctly bundles all complex AI dependencies (`transformers`, `torch`) into the executable.

```bash
# 1. Install build tools
pip install ".[build]"

# 2. Run PyInstaller with the provided spec file
pyinstaller photorg.spec

# 3. Output
# Your friend's standalone executable will be ready at:
# dist/Photorg/Photorg.exe
```

---

## 📂 Project Structure

```text
photorg/
├── core/
│   ├── ai_classifier.py   # AI vision, Geocoding fallback, Burst optimization
│   ├── exif.py            # EXIF date and GPS metadata extraction
│   ├── file_utils.py      # File tree scanning and safe copying
│   ├── geocoder.py        # Nominatim OpenStreetMap API integration
│   ├── organiser.py       # Core day grouping logic
│   ├── scene_model.py     # Lazy-loaded CLIP transformers model
│   └── video_utils.py     # Video frame extraction (imageio)
└── ui/
    ├── theme.py           # Design tokens + Dark QSS stylesheet
    ├── main_window.py     # Central application router
    ├── widgets/           # TagInput, DropZone, etc.
    ├── screens/           # Day, AI, Output Views
    └── workers/           # Background QThreads to prevent UI freezing
```

---

## 💻 Tech Stack

| Package | Role |
|---|---|
| `PySide6` | Modern Qt 6 UI — asynchronous routing, styled widgets, file dialogs |
| `Pillow` & `pillow-heif` | EXIF metadata parsing and `.heic` iPhone photo support |
| `transformers` & `torch` | Heavy-lifting zero-shot image classification via OpenAI's CLIP |
| `imageio` | High-performance video frame extraction |
| `urllib` (Nominatim) | Free HTTP reverse geocoding to identify real-world landmarks |

---

## ✅ Roadmap

- [x] EXIF date extraction and day grouping
- [x] AI scene classification (OpenAI CLIP)
- [x] GPS Reverse Geocoding fallback
- [x] Video extension support (`.mov`, `.mp4`)
- [x] Burst photo optimization for performance
- [x] Asynchronous background workers / UI Progress Bars
- [x] Real-time Output Preview tree
- [x] Windows executable bundled with PyInstaller
