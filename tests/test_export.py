import os
import sys
from datetime import date
from decimal import Decimal

# Ensure src is on path when running without installation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from booking_parser.export import CSV_HEADER, write_csv
from booking_parser.models import BookingNormalized, Price


def test_write_csv_header_and_row(tmp_path):
    bookings = [
        BookingNormalized(
            city="Paris",
            country="France",
            hotel_name="Nice Hotel",
            start_date=date(2024, 5, 10),
            end_date=date(2024, 5, 12),
            total_price=Price(value=Decimal("250.00"), currency="EUR"),
        )
    ]

    out = tmp_path / "bookings.csv"
    write_csv(bookings, out)

    with out.open() as f:
        lines = [line.strip() for line in f.readlines()]

    assert lines[0] == ",".join(CSV_HEADER)
    assert lines[1] == "Paris,France,Nice Hotel,2024-05-10,2024-05-12,250.00 EUR"