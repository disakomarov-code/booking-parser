import os
import sys

# Ensure src is on path when running without installation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from booking_parser.normalize import parse_date_string, parse_price_string, normalize_booking
from booking_parser.models import BookingRaw


def test_parse_date_string_variants():
    assert parse_date_string("2024-01-12").isoformat() == "2024-01-12"
    assert parse_date_string("12 Jan 2024").isoformat() == "2024-01-12"
    assert parse_date_string("Jan 12, 2024").isoformat() == "2024-01-12"


def test_parse_price_string_us_and_eu():
    p1 = parse_price_string("$1,234.56")
    assert float(p1.value) == 1234.56 and p1.currency == "USD"

    p2 = parse_price_string("€ 1.234,56")
    assert float(p2.value) == 1234.56 and p2.currency == "EUR"

    p3 = parse_price_string("Total: 999 CHF")
    assert float(p3.value) == 999.0 and p3.currency == "CHF"


def test_normalize_booking_basic():
    raw = BookingRaw(
        hotel_name="Nice Hotel",
        address_text="123 St, Paris, France",
        city_text=None,
        country_text=None,
        start_date_text="2024-05-10",
        end_date_text="2024-05-12",
        total_price_text="Total EUR 250.00",
    )
    norm = normalize_booking(raw)
    assert norm.city == "Paris" and norm.country == "France"
    assert norm.start_date.isoformat() == "2024-05-10"
    assert norm.end_date.isoformat() == "2024-05-12"
    assert float(norm.total_price.value) == 250.0 and norm.total_price.currency == "EUR"