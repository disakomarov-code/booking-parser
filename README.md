# Booking.com Past Reservations Exporter

Exports your past Booking.com reservations to CSV with the exact columns:

- City
- Country
- Hotel name
- Start date
- End date
- Total price of booking

## Setup

1. Python 3.11+
2. Install dependencies:

```bash
python -m pip install -r requirements.txt
python -m playwright install  # one-time to install browser engines
```

3. Create `.env` from template and fill credentials:

```bash
cp .env.example .env
# edit .env to add BOOKING_EMAIL and BOOKING_PASSWORD
```

## Usage

```bash
# Run headless (default)
python -m booking_parser --out bookings.csv

# Visible browser to complete 2FA/CAPTCHA if needed
python -m booking_parser --no-headless --out bookings.csv

# Date range filter by check-in date
python -m booking_parser --from 2015-01-01 --to 2025-01-01 --out bookings.csv

# Clear cached session
python -m booking_parser --delete-cache
```

Notes:
- The tool stores session cookies locally in `.cache/session.json`.
- If the site presents human verification, re-run with `--no-headless` and complete the steps manually.
- Scraping is polite and throttled; do not run aggressively.

## Testing

```bash
pytest
```

## CSV Format Guarantee

Header is exactly:

```
City,Country,Hotel name,Start date,End date,Total price of booking
```

Each row contains ISO dates and a total price like `1234.56 USD` when currency is known.