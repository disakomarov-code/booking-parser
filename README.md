# Booking.com Past Reservations Exporter

Exports your past Booking.com reservations to CSV with the exact columns:

- City
- Country
- Hotel name
- Start date
- End date
- Total price of booking

## Java (current)

Prerequisites:
- Java 17+
- Maven 3.8+

Setup:
- Optional (for Playwright browsers):
```bash
mvn -q -Dplaywright.cli.install=true test
```

Run CLI (uses environment variables `BOOKING_EMAIL` and `BOOKING_PASSWORD`):
```bash
# Basic export (writes ./bookings.csv)
mvn -q exec:java -Dexec.mainClass=com.bookingparser.cli.Cli -Dexec.args="--out bookings.csv"

# Visible browser or 2FA/CAPTCHA handling to be added when scraping is implemented
# Date range filter by check-in date
mvn -q exec:java -Dexec.mainClass=com.bookingparser.cli.Cli -Dexec.args="--from 2015-01-01 --to 2025-01-01 --out bookings.csv"

# Clear cached session
mvn -q exec:java -Dexec.mainClass=com.bookingparser.cli.Cli -Dexec.args="--delete-cache"
```

Notes:
- Java CLI currently includes normalization and CSV export. Web scraping in Java is a WIP and not yet implemented; running without `--email-fallback` will produce an empty CSV unless raw bookings are provided by another path.
- Session cookies will be cached under `.cache/session.json` once scraping is implemented.
- Create `.env` to define environment variables (see below) or export them in your shell.

Build and tests:
```bash
mvn -q test
```

## Python version (legacy/dev)

You can also run the Python implementation (with Playwright-based scraping) if you prefer Python:

Setup:
1. Python 3.11+
2. Install dependencies:
```bash
python -m pip install -r requirements.txt
python -m playwright install
```
3. Create `.env` from template and fill credentials:
```bash
cp .env.example .env
# edit .env to add BOOKING_EMAIL and BOOKING_PASSWORD
```

Usage:
```bash
# Run headless (default)
PYTHONPATH=src python -m booking_parser --out bookings.csv

# Visible browser to complete 2FA/CAPTCHA if needed
PYTHONPATH=src python -m booking_parser --no-headless --out bookings.csv

# Date range filter by check-in date
PYTHONPATH=src python -m booking_parser --from 2015-01-01 --to 2025-01-01 --out bookings.csv

# Clear cached session
PYTHONPATH=src python -m booking_parser --delete-cache
```

## Environment

Copy `.env.example` to `.env` and fill in your credentials, or export them in your shell:
```
BOOKING_EMAIL=
BOOKING_PASSWORD=
```

## CSV Format Guarantee

Header is exactly:
```
City,Country,Hotel name,Start date,End date,Total price of booking
```

Each row contains ISO dates and a total price like `1234.56 USD` when currency is known.