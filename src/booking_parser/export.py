from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

from .models import BookingNormalized


CSV_HEADER = [
    "City",
    "Country",
    "Hotel name",
    "Start date",
    "End date",
    "Total price of booking",
]


def write_csv(bookings: Iterable[BookingNormalized], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADER)
        for booking in bookings:
            row = booking.to_csv_row()
            writer.writerow(row)

    return path