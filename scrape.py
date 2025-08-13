"""Core scraping routines for single athlete and worker wrapper."""

from __future__ import annotations

import random
import time
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup

from config import BASE
from io_utils import append_rows, save_progress
from net import safe_get
from parsers import parse_competition_events, parse_personal_information


def scrape_single_athlete(athlete_id: int, session: requests.Session) -> Optional[List[Dict[str, str]]]:
    url = f"{BASE}/athletes/{athlete_id}"
    try:
        response = safe_get(session, url)
    except requests.RequestException:
        return None

    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    personal_info = parse_personal_information(soup)
    personal_info["athlete_id"] = str(athlete_id)

    events = parse_competition_events(soup)
    gold_count = silver_count = bronze_count = 0
    for event in events:
        medal = (event.get("medal") or "").lower()
        if "gold" in medal:
            gold_count += 1
        elif "silver" in medal:
            silver_count += 1
        elif "bronze" in medal:
            bronze_count += 1

    latest_event = events[-1] if events else {}
    personal_info.update({
        "games": latest_event.get("Games", ""),
        "year": latest_event.get("year", ""),
        "sport": latest_event.get("sport", ""),
        "gold_medal": str(gold_count),
        "silver_medal": str(silver_count),
        "bronze_medal": str(bronze_count),
    })

    return [personal_info]


def worker_task(athlete_id: int, csv_path: str, delay: float) -> bool:
    session = requests.Session()
    try:
        athlete_rows = scrape_single_athlete(athlete_id, session)
        if athlete_rows is None:
            return False
        append_rows(csv_path, athlete_rows)
        return True
    finally:
        save_progress(athlete_id)
        time.sleep(delay + random.random() * delay)
