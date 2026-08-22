# Photorg

> Auto-organise vacation photos into date-based folders, with optional AI scene grouping.

![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![PySide6](https://img.shields.io/badge/PySide6-6.8%2B-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## Features

| Mode | Description |
|---|---|
| **Day Organizer** | Reads EXIF `DateTimeOriginal` and sorts photos into `<Title> / Day 01 / ...` |
| **AI Organizer** | Uses a vision model to group photos by scene (beach, museum, park…) |
| **Output Preview** | Browse the generated folder structure inside the app |

---

## Quick start

```bash
# 1. Clone
git clone https://github.com/RiquiFeup/photorg.git
cd photorg

# 2. Create & activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1        # Windows PowerShell
# source venv/bin/activate         # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run
python -m photorg
```

---

## Install as a local package

```bash
pip install .
photorg          # launch from anywhere
```

---

## Build distributable executable

```bash
pip install ".[build]"
pyinstaller --onefile --windowed --name Photorg photorg/main.py
# Output: dist/Photorg.exe
```

---

## Project structure

```
photorg/
├── core/
│   ├── organiser.py       # Day organiser logic  (stub)
│   └── ai_classifier.py   # AI classifier logic  (stub)
└── ui/
    ├── theme.py            # Design tokens + QSS stylesheet
    ├── main_window.py      # App shell
    ├── top_bar.py
    ├── status_bar.py
    ├── widgets/
    │   ├── drop_zone.py
    │   ├── tag_input.py
    │   └── browse_row.py
    └── screens/
        ├── day_screen.py
        ├── ai_screen.py
        └── output_screen.py
```

---

## Tech stack

| Package | Role |
|---|---|
| `PySide6` | Qt 6 UI — layouts, signals, drag-and-drop, file dialogs |
| `Pillow` | EXIF metadata parsing, thumbnail generation |

---

## Roadmap

- [ ] EXIF date extraction and day grouping
- [ ] AI scene classification (Google Vision / CLIP)
- [ ] Progress bar during processing
- [ ] Undo / preview before writing
- [ ] Windows installer (NSIS)
