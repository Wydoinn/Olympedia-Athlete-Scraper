#!/usr/bin/env python3

"""
CLI entrypoint for the Olympedia athlete scraper.

This thin module parses CLI args and delegates to the core modules.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

from config import STOP_THRESHOLD
from io_utils import ensure_csv_header, load_progress, save_progress
from scrape import worker_task


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scrape Olympic athlete data from Olympedia.org",
        epilog="Example: python scraper.py --start 1 --concurrency 10 --delay 0.4",
    )
    parser.add_argument("--start", type=int, default=1, help="Starting athlete ID (default: 1)")
    parser.add_argument("--concurrency", type=int, default=10, help="Number of concurrent threads (default: 10)")
    parser.add_argument("--delay", type=float, default=0.4, help="Base delay between requests in seconds (default: 0.4)")
    parser.add_argument("--csv", type=str, default="athletes.csv", help="Output CSV file path (default: athletes.csv)")
    parser.add_argument("--resume", action="store_true", help="Resume from last saved progress")

    args = parser.parse_args()

    start_id = args.start
    csv_path = args.csv

    if args.resume:
        last_processed = load_progress()
        if last_processed >= start_id:
            start_id = last_processed + 1
            print(f"Resuming from athlete ID {start_id}")

    ensure_csv_header(csv_path)

    consecutive_missing = 0
    current_id = start_id

    print(f"Starting scraper with {args.concurrency} threads, {args.delay}s delay")
    print(f"Output file: {csv_path}")
    print(f"Will stop after {STOP_THRESHOLD} consecutive missing athletes")

    with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        while True:
            future_to_id = {
                executor.submit(worker_task, current_id + offset, csv_path, args.delay): current_id + offset
                for offset in range(args.concurrency)
            }

            for future in as_completed(future_to_id):
                athlete_id = future_to_id[future]
                try:
                    athlete_found = future.result()
                except Exception as e:
                    print(f"Error processing athlete {athlete_id}: {e}")
                    athlete_found = False

                if athlete_found:
                    consecutive_missing = 0
                    if athlete_id % 100 == 0:
                        print(f"Processed athlete ID {athlete_id}")
                else:
                    consecutive_missing += 1

                if consecutive_missing >= STOP_THRESHOLD:
                    print(
                        f"[{datetime.now(timezone.utc)}] "
                        f"{STOP_THRESHOLD} consecutive missing athletes reached. "
                        f"Stopping at ID {athlete_id}."
                    )
                    save_progress(athlete_id)
                    return

            current_id += args.concurrency


if __name__ == "__main__":
    main()
