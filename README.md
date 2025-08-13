# Olympedia Athlete Scraper

A modular Python scraper for collecting Olympic athlete data from Olympedia.org with proper rate limiting and respectful crawling practices.

## Structure

- `scraper.py` — CLI entrypoint with argument parsing and main execution loop
- `config.py` — Configuration constants including STOP_THRESHOLD and CSV field definitions
- `io_utils.py` — CSV file operations and progress persistence utilities
- `net.py` — HTTP client with retry logic and backoff mechanisms
- `parsers.py` — BeautifulSoup-based HTML parsing functions
- `scrape.py` — Core scraping logic and worker task implementation
- `start.sh` — Convenience launcher script (virtual environment + dependencies + execution)

## Quick Start (Recommended)

Use the provided start script which automatically sets up a virtual environment, installs dependencies, and runs the scraper:

```bash
chmod +x start.sh
./start.sh --start 1 --concurrency 10 --delay 0.4 --csv athletes.csv
```

Resume from the last saved progress:
```bash
RESUME=1 ./start.sh
```

Set defaults via environment variables (can be overridden by CLI arguments):
```bash
CONCURRENCY=8 DELAY=0.5 START=1000 CSV=athletes.csv ./start.sh
```

## Manual Setup

Install dependencies and run the CLI directly:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scraper.py --start 1 --concurrency 10 --delay 0.4 --csv athletes.csv
```

Resume from previous session:
```bash
python scraper.py --resume
```

## CLI Options

- `--start`: Starting athlete ID (default: 1)
- `--concurrency`: Number of concurrent threads (default: 10)
- `--delay`: Base delay between requests in seconds (default: 0.4)
- `--csv`: Output CSV file path (default: athletes.csv)
- `--resume`: Resume from last saved progress

## Features

- **Concurrent Processing**: Multi-threaded scraping with configurable concurrency
- **Automatic Resume**: Progress tracking with ability to resume interrupted sessions
- **Respectful Rate Limiting**: Built-in delays and backoff mechanisms
- **Error Handling**: Robust error recovery and logging
- **Smart Stopping**: Automatically stops after consecutive missing athletes (configurable threshold)
- **Progress Tracking**: Real-time progress updates and persistence

## Respectful Crawling Guidelines

**IMPORTANT**: Olympedia.org's robots.txt specifies a 10-second crawl delay. To be respectful:

- **Minimum delay**: Use `--delay 10` or higher (robots.txt requirement)
- **Low concurrency**: Keep `--concurrency` at 1-2 maximum to avoid overwhelming the server
- **Monitor your usage**: The scraper includes progress logging to track your impact

### Recommended respectful usage:
```bash
python scraper.py --start 1 --concurrency 1 --delay 10 --csv athletes.csv
```

## Technical Details

- Progress is automatically saved to `progress.json`
- The scraper stops after encountering a configurable number of consecutive missing athlete IDs
- CSV headers are automatically created and maintained
- HTTP requests include proper retry logic with exponential backoff
- Concurrent workers process athlete IDs in batches

## Output

The scraper generates a CSV file with comprehensive athlete data including personal information, Olympic participation history, and medal records.

## Error Handling

- Individual request failures don't stop the entire process
- Progress is saved regularly to prevent data loss
- Detailed error logging helps with troubleshooting
- Automatic retry mechanisms handle temporary network issues

## Notes

- Always respect the website's robots.txt and terms of service
- Monitor your network usage and be considerate of server resources
- The scraper is designed for research and educational purposes
- Consider reaching out to Olympedia if you need large-scale data access
