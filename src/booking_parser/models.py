from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class Price(BaseModel):
    value: Decimal = Field(..., description="Numeric total price value")
    currency: Optional[str] = Field(
        default=None, description="ISO currency code if available (e.g., 'USD')"
    )


class BookingRaw(BaseModel):
    hotel_name: str
    address_text: Optional[str] = None
    city_text: Optional[str] = None
    country_text: Optional[str] = None
    start_date_text: str
    end_date_text: str
    total_price_text: str


class BookingNormalized(BaseModel):
    city: str
    country: str
    hotel_name: str
    start_date: date
    end_date: date
    total_price: Price

    def to_csv_row(self) -> list[str]:
        price_str = (
            f"{self.total_price.value} {self.total_price.currency}".strip()
            if self.total_price.currency
            else f"{self.total_price.value}"
        )
        return [
            self.city,
            self.country,
            self.hotel_name,
            self.start_date.isoformat(),
            self.end_date.isoformat(),
            price_str,
        ]