"""HTML parsing utilities for athlete personal info and competitions."""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple

from bs4 import BeautifulSoup


def text_or_empty(tag) -> str:
    return tag.get_text(" ", strip=True) if tag else ""


# ---------------- Location and date helpers ---------------- #

def parse_location(location_text: str) -> Tuple[str, str, str]:
    if not location_text:
        return "", "", ""

    text = location_text.strip()

    match = re.match(r"^(.*?),\s*(.*?)\s*\(([^)]+)\)$", text)
    if match:
        city, region, country = match.groups()
        return city.strip(), region.strip(), country.strip()

    match = re.match(r"^(.*?)\s*\(([^)]+)\)$", text)
    if match:
        region, country = match.groups()
        return "", region.strip(), country.strip()

    match = re.match(r"^(.*?),\s*(.*?)$", text)
    if match:
        city, country = match.groups()
        return city.strip(), "", country.strip()

    return text, "", ""


def split_date_and_location(value: str) -> Tuple[str, str]:
    if not value:
        return "", ""
    parts = value.split(" in ", 1)
    date_str = parts[0].strip()
    location_str = parts[1].strip() if len(parts) > 1 else ""
    return date_str, location_str


# ---------------- Biographical table parsing ---------------- #

def find_biographical_table(soup: BeautifulSoup) -> Optional[BeautifulSoup]:
    target_labels = {"sex", "born", "died", "measurements", "height", "weight", "noc"}

    best_table = None
    best_score = 0

    for table in soup.find_all("table"):
        score = 0
        for row in table.find_all("tr"):
            header = row.find("th")
            if not header:
                continue
            label = header.get_text(strip=True).lower()
            if "measurement" in label:
                label = "measurements"
            if label in target_labels:
                score += 1
        if score > best_score:
            best_table = table
            best_score = score

    return best_table


def parse_personal_information(soup: BeautifulSoup) -> Dict[str, str]:
    from config import CSV_FIELDS  # local import to avoid cycles in tooling

    info = {field: "" for field in CSV_FIELDS}

    title_element = soup.find("h1")
    if title_element:
        info["name"] = title_element.get_text(" ", strip=True)

    bio_table = find_biographical_table(soup)
    if not bio_table:
        return info

    for row in bio_table.find_all("tr"):
        header = row.find("th")
        data = row.find("td")
        if not header or not data:
            continue

        label = header.get_text(strip=True).lower()
        value = data.get_text(" ", strip=True)
        if "measurement" in label:
            label = "measurements"

        if label == "sex":
            info["sex"] = value
        elif label in ("measurements", "height", "weight"):
            _parse_measurements(label, value, info)
        elif label.startswith("born"):
            _parse_birth_info(value, info)
        elif label.startswith("died"):
            _parse_death_info(value, info)
        elif label == "noc":
            _parse_noc_info(data, info)

    return info


def _parse_measurements(label: str, value: str, info: Dict[str, str]) -> None:
    if label == "measurements":
        height_match = re.search(r"(\d{2,3})\s*cm", value)
        weight_match = re.search(r"(\d{2,3})\s*kg", value)
        if height_match:
            info["height_cm"] = height_match.group(1)
        if weight_match:
            info["weight_kg"] = weight_match.group(1)
    elif label == "height":
        height_match = re.search(r"(\d{2,3})\s*cm", value) or re.search(r"([0-9]+(?:\.[0-9]+)?)\s*m", value)
        if height_match:
            if "cm" in height_match.group(0).lower():
                info["height_cm"] = re.sub(r"\D", "", height_match.group(0))
            else:
                try:
                    meters = float(height_match.group(1))
                    info["height_cm"] = str(int(round(meters * 100)))
                except (ValueError, TypeError):
                    pass
    elif label == "weight":
        weight_match = re.search(r"(\d{2,3})\s*kg", value)
        if weight_match:
            info["weight_kg"] = weight_match.group(1)


def _parse_birth_info(value: str, info: Dict[str, str]) -> None:
    date_str, location_str = split_date_and_location(value)
    info["born_date"] = date_str
    if location_str:
        city, region, country = parse_location(location_str)
        info["born_city"] = city
        info["born_region"] = region
        info["born_country"] = country


def _parse_death_info(value: str, info: Dict[str, str]) -> None:
    date_str, location_str = split_date_and_location(value)
    info["died_date"] = date_str
    if location_str:
        city, region, country = parse_location(location_str)
        info["died_city"] = city
        info["died_region"] = region
        info["died_country"] = country


def _parse_noc_info(data_cell, info: Dict[str, str]) -> None:
    noc_link = data_cell.find("a", href=re.compile(r"^/countries/"))
    text = (noc_link.get_text(" ", strip=True) if noc_link else data_cell.get_text(" ", strip=True)).strip()
    code_match = re.search(r"\b[A-Z]{3}\b", text)
    info["noc"] = code_match.group(0) if code_match else text


# ---------------- Competition parsing ---------------- #

def parse_competition_events(soup: BeautifulSoup) -> List[Dict[str, str]]:
    events: List[Dict[str, str]] = []
    for table in soup.find_all("table"):
        headers = [th.get_text(" ", strip=True).lower() for th in table.find_all("th")]
        if not headers:
            continue
        has_games = "games" in headers
        has_sport = any("discipline" in h for h in headers) or any("sport" in h for h in headers)
        if not (has_games and has_sport):
            continue
        table_body = table.find("tbody") or table
        current_game = ""
        current_sport = ""
        current_noc = ""
        for row in table_body.find_all("tr"):
            cells = row.find_all("td")
            if not cells:
                continue
            first_cell_link = cells[0].find("a")
            if first_cell_link and "/editions/" in (first_cell_link.get("href", "") or ""):
                current_game = text_or_empty(cells[0])
                current_sport = text_or_empty(cells[1]) if len(cells) > 1 else ""
                current_noc = text_or_empty(cells[2]) if len(cells) > 2 else ""
                continue
            if len(cells) >= 5:
                medal_text = text_or_empty(cells[4])
                year_match = re.search(r"(\d{4})", current_game)
                events.append({
                    "Games": current_game,
                    "year": year_match.group(1) if year_match else "",
                    "sport": current_sport,
                    "medal": medal_text,
                    "NOC": current_noc,
                })
    return events
