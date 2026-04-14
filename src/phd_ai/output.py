from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value or "output"


def build_cover_letter_path(output_dir: Path, researcher: str, suffix: str = "cover-letter") -> Path:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    researcher_slug = slugify(researcher)
    filename = f"{timestamp}_{researcher_slug}_{suffix}.md"
    return output_dir / filename


def build_run_directory(base_dir: Path, researcher: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    researcher_slug = slugify(researcher)
    return base_dir / f"{timestamp}_{researcher_slug}"


def save_text_output(text: str, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")
    return path


def save_json_output(data: dict, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return path
