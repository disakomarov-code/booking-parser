from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Optional, Tuple

import dateparser
from dateutil import parser as dateutil_parser

from .models import BookingNormalized, BookingRaw, Price


_CURRENCY_SYMBOL_TO_CODE = {
    "$": "USD",
    "€": "EUR",
    "£": "GBP",
    "CHF": "CHF",
    "C$": "CAD",
    "CA$": "CAD",
    "A$": "AUD",
    "AU$": "AUD",
    "₺": "TRY",
    "₽": "RUB",
    "zł": "PLN",
    "R$": "BRL",
    "₹": "INR",
    "¥": "JPY",
    "₩": "KRW",
}

# Match values like "1,234.56" or "1.234,56" or "1234" possibly prefixed/suffixed with currency
_PRICE_NUMERIC_RE = re.compile(r"(?<!\d)(?:\d{1,3}(?:[.,]\d{3})+|\d+)(?:[.,]\d{2})?(?!\d)")


def _safe_strip(text: Optional[str]) -> str:
    return (text or "").strip()


def parse_date_string(text: str) -> date:
    cleaned = text.strip()
    # Try strict ISO first
    try:
        return datetime.fromisoformat(cleaned).date()
    except Exception:
        pass
    # Try dateutil for robustness
    try:
        return dateutil_parser.parse(cleaned, dayfirst=False, fuzzy=True).date()
    except Exception:
        pass
    # Try dateparser as a fallback
    parsed = dateparser.parse(cleaned)
    if not parsed:
        raise ValueError(f"Unable to parse date from: {text!r}")
    return parsed.date()


@dataclass
class ParsedPrice:
    value: Decimal
    currency: Optional[str]


def _normalize_decimal_string(num_str: str) -> str:
    # Decide decimal separator by last occurrence of ',' or '.' with two digits
    if "," in num_str and "." in num_str:
        # Assume thousand sep is the one that appears first
        if num_str.rfind(",") > num_str.rfind("."):
            # Example: 1.234,56 -> thousands '.' decimal ','
            tmp = num_str.replace(".", "").replace(",", ".")
        else:
            # Example: 1,234.56 -> thousands ',' decimal '.'
            tmp = num_str.replace(",", "")
    elif "," in num_str:
        # Could be 1.234 or 1,234; if there are exactly 3 digits after ',', treat as thousands
        parts = num_str.split(",")
        if len(parts[-1]) == 3 and all(p.isdigit() for p in parts):
            tmp = "".join(parts)
        else:
            tmp = num_str.replace(",", ".")
    else:
        tmp = num_str
    return tmp


def parse_price_string(text: str) -> ParsedPrice:
    if text is None:
        raise ValueError("Price text is None")
    cleaned = text.strip()

    # Identify explicit 3-letter currency codes
    currency_code = None
    code_match = re.search(r"\b([A-Z]{3})\b", cleaned)
    if code_match:
        currency_code = code_match.group(1)

    # Identify known symbols
    for symbol, code in _CURRENCY_SYMBOL_TO_CODE.items():
        if symbol in cleaned:
            currency_code = currency_code or code
            break

    num_match = _PRICE_NUMERIC_RE.search(cleaned)
    if not num_match:
        raise ValueError(f"Unable to extract numeric price from: {text!r}")

    numeric_raw = num_match.group(0)
    normalized = _normalize_decimal_string(numeric_raw)
    try:
        value = Decimal(normalized)
    except InvalidOperation as exc:
        raise ValueError(f"Invalid numeric price after normalization: {normalized!r}") from exc

    return ParsedPrice(value=value, currency=currency_code)


def extract_city_country_from_address(address_text: Optional[str], explicit_city: Optional[str], explicit_country: Optional[str]) -> Tuple[str, str]:
    if explicit_city and explicit_country:
        return explicit_city.strip(), explicit_country.strip()

    address = _safe_strip(address_text)
    if not address:
        # Fall back to provided pieces
        return _safe_strip(explicit_city) or "", _safe_strip(explicit_country) or ""

    # Heuristic: split by commas and pick last two non-empty tokens
    parts = [p.strip() for p in address.split(",") if p.strip()]
    if len(parts) >= 2:
        country = parts[-1]
        city = parts[-2]
        return city, country

    # Fallback: if only one component, treat as city; country unknown
    if len(parts) == 1:
        return parts[0], ""

    return _safe_strip(explicit_city) or "", _safe_strip(explicit_country) or ""


def normalize_booking(raw: BookingRaw) -> BookingNormalized:
    start_date = parse_date_string(raw.start_date_text)
    end_date = parse_date_string(raw.end_date_text)
    parsed_price = parse_price_string(raw.total_price_text)

    city, country = extract_city_country_from_address(
        address_text=raw.address_text,
        explicit_city=raw.city_text,
        explicit_country=raw.country_text,
    )

    return BookingNormalized(
        city=city,
        country=country,
        hotel_name=raw.hotel_name.strip(),
        start_date=start_date,
        end_date=end_date,
        total_price=Price(value=parsed_price.value, currency=parsed_price.currency),
    )