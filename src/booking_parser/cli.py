from __future__ import annotations

import argparse
import os
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, List, Optional

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from .export import write_csv
from .models import BookingNormalized, BookingRaw
from .normalize import normalize_booking
from .scrape import ScrapeOptions, fetch_raw_bookings

console = Console()


def _parse_date_opt(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    return datetime.fromisoformat(value).date()


def _filter_by_date(bookings: Iterable[BookingNormalized], start: Optional[date], end: Optional[date]) -> List[BookingNormalized]:
    result: List[BookingNormalized] = []
    for b in bookings:
        if start and b.start_date < start:
            continue
        if end and b.start_date > end:
            continue
        result.append(b)
    return result


def main(argv: Optional[List[str]] = None) -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(description="Export Booking.com past reservations to CSV")
    parser.add_argument("--from", dest="from_date", help="Filter bookings with check-in on/after YYYY-MM-DD")
    parser.add_argument("--to", dest="to_date", help="Filter bookings with check-in on/before YYYY-MM-DD")
    parser.add_argument("--out", dest="out_path", default="./bookings.csv", help="Output CSV path")
    parser.add_argument("--headless", dest="headless", action="store_true", help="Run browser headless (default)")
    parser.add_argument("--no-headless", dest="no_headless", action="store_true", help="Run browser visibly to assist with 2FA/CAPTCHA")
    parser.add_argument("--delete-cache", dest="delete_cache", action="store_true", help="Delete cached session and exit")
    parser.add_argument("--debug", dest="debug", action="store_true", help="Verbose logging and slower automation")
    parser.add_argument("--email-fallback", dest="email_fallback", help="Optional path to .mbox/.eml export of Booking.com confirmations")

    args = parser.parse_args(argv)

    out_path = args.out_path
    start_date_opt = _parse_date_opt(args.from_date)
    end_date_opt = _parse_date_opt(args.to_date)
    headless = not args.no_headless
    debug = args.debug

    cache_dir = Path(".cache")
    cache_dir.mkdir(exist_ok=True)
    storage_path = cache_dir / "session.json"

    if args.delete_cache:
        if storage_path.exists():
            storage_path.unlink()
        console.print("[green]Cache deleted")
        return

    email = os.getenv("BOOKING_EMAIL")
    password = os.getenv("BOOKING_PASSWORD")

    if not args.email_fallback and (not email or not password):
        console.print("[red]BOOKING_EMAIL and BOOKING_PASSWORD must be set in environment or .env.")
        raise SystemExit(2)

    raw_bookings: List[BookingRaw] = []

    if args.email_fallback:
        # Optional TODO: implement email parsing; for now, just notify
        console.print("[yellow]Email fallback parsing not implemented in this version.")
    else:
        console.print("[cyan]Logging in and scraping past bookings...")
        raw_bookings = fetch_raw_bookings(
            email=email or "",
            password=password or "",
            headless=headless,
            debug=debug,
            storage_path=str(storage_path),
        )

    normalized: List[BookingNormalized] = []
    for raw in raw_bookings:
        try:
            normalized.append(normalize_booking(raw))
        except Exception as exc:
            if debug:
                console.print(f"[yellow]Skipping booking due to normalization error: {exc}")

    if start_date_opt or end_date_opt:
        normalized = _filter_by_date(normalized, start_date_opt, end_date_opt)

    write_csv(normalized, out_path)

    console.print(f"[green]Wrote {len(normalized)} rows to {out_path}")


if __name__ == "__main__":
    main()