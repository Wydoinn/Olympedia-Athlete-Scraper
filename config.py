"""
Central configuration and constants for the Olympedia scraper.

These values are imported by other modules. Keeping them in one place
avoids circular dependencies and makes tuning easier.
"""

import threading

# Base site URL
BASE = "https://www.olympedia.org"

# File to store scraping progress
PROGRESS_FILE = "progress.json"

# Thread lock for file operations and progress writes
LOCK = threading.Lock()

# Stop after this many consecutive missing athlete IDs
STOP_THRESHOLD = 1000

# CSV column definitions - must match the order used in DictWriter
CSV_FIELDS = [
    "athlete_id",      # Unique ID from Olympedia
    "name",            # Full athlete name
    "sex",             # M/F gender designation
    "height_cm",       # Height in centimeters
    "weight_kg",       # Weight in kilograms
    "born_date",       # Birth date string
    "died_date",       # Death date string (if applicable)
    "born_city",       # Birth city
    "born_region",     # Birth region/state/province
    "born_country",    # Birth country (NOC code preferred)
    "died_city",       # Death city
    "died_region",     # Death region/state/province
    "died_country",    # Death country (NOC code preferred)
    "noc",             # National Olympic Committee code
    "games",           # Most recent Olympic Games participated in
    "year",            # Year of most recent participation
    "sport",           # Primary sport discipline
    "gold_medal",      # Total gold medals won
    "silver_medal",    # Total silver medals won
    "bronze_medal",    # Total bronze medals won
]
