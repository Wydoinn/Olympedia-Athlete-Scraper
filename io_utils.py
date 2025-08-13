"""I/O utilities: progress tracking and CSV writing."""

from __future__ import annotations

import csv
import json
import os
from datetime import datetime, timezone
from typing import Dict, List

from config import CSV_FIELDS, LOCK, PROGRESS_FILE


def save_progress(last_id: int) -> None:
    """
    Save the current scraping progress to a JSON file.

    This function is thread-safe and stores both the last processed athlete ID
    and a timestamp for tracking purposes.
    """
    with LOCK:
        progress_data = {
            "last_id": int(last_id),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump(progress_data, f, indent=2)


def load_progress() -> int:
    """
    Load the last processed athlete ID from the progress file.

    Returns the last processed athlete ID, or 0 if no progress file exists or
    if there's an error reading it.
    """
    if not os.path.exists(PROGRESS_FILE):
        return 0

    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            progress_data = json.load(f)
            return int(progress_data.get("last_id", 0))
    except (json.JSONDecodeError, ValueError, KeyError):
        return 0


def ensure_csv_header(file_path: str) -> None:
    """Create CSV file with headers if it doesn't exist."""
    if not os.path.exists(file_path):
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            writer.writeheader()


def append_rows(file_path: str, rows: List[Dict[str, str]]) -> None:
    """
    Thread-safely append athlete data rows to the CSV file. Ensures header and
    converts None values to empty strings.
    """
    if not rows:
        return

    with LOCK:
        ensure_csv_header(file_path)
        with open(file_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            for row in rows:
                clean_row = {field: (row.get(field) or "") for field in CSV_FIELDS}
                writer.writerow(clean_row)
