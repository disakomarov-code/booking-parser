from __future__ import annotations

import re
import time
from dataclasses import dataclass
from typing import Iterable, List, Optional

from rich.console import Console
from tenacity import retry, stop_after_attempt, wait_exponential_jitter
from playwright.sync_api import sync_playwright, Page, Locator

from .auth import TRIPS_URLS, ensure_logged_in
from .models import BookingRaw


console = Console()


@dataclass
class ScrapeOptions:
    headless: bool = True
    debug: bool = False
    throttle_secs_min: float = 0.5
    throttle_secs_max: float = 1.5


def _sleep_throttle(min_s: float, max_s: float) -> None:
    delay = min_s if min_s == max_s else (min_s + (max_s - min_s) * 0.6)
    # fixed 0.6 proportion to avoid importing random for now
    time.sleep(delay)


def _click_load_more_if_present(page: Page) -> bool:
    candidates = [
        page.get_by_role("button", name=re.compile("(Load|Show) more", re.I)),
        page.get_by_text(re.compile("(Load|Show) more", re.I)),
    ]
    for c in candidates:
        try:
            if c.count() > 0 and c.first.is_visible():
                c.first.click()
                page.wait_for_load_state("networkidle")
                return True
        except Exception:
            continue
    return False


def _find_booking_cards(page: Page) -> List[Locator]:
    strategies = [
        # Heuristics based on text markers
        page.locator("section:has-text('Check-in'):has-text('Check-out')"),
        page.locator("div:has-text('Check-in'):has-text('Check-out')"),
        # Data-testid guesses
        page.locator("[data-testid*='trip']"),
        page.locator("[data-testid*='reservation']"),
    ]
    for strat in strategies:
        try:
            count = strat.count()
            if count > 0:
                return [strat.nth(i) for i in range(count)]
        except Exception:
            continue
    return []


def _extract_text_safe(container: Locator, locator: Locator) -> Optional[str]:
    try:
        if locator.count() > 0:
            text = locator.first.inner_text().strip()
            if text:
                return text
    except Exception:
        return None
    return None


def _extract_booking_from_card(card: Locator) -> Optional[BookingRaw]:
    # Hotel name
    hotel_name = None
    name_candidates = [
        card.get_by_role("heading"),
        card.locator("[data-testid*='hotel-name']"),
        card.locator("[class*='hotel']"),
    ]
    for c in name_candidates:
        try:
            if c.count() > 0:
                hotel_name = c.first.inner_text().strip()
                if hotel_name:
                    break
        except Exception:
            continue

    if not hotel_name:
        return None

    # Address / location pieces
    address_text = None
    city_text = None
    country_text = None
    addr_candidates = [
        card.locator("[data-testid*='address']"),
        card.locator("[class*='address']"),
        card.get_by_text(re.compile(r",\s*[A-Za-z ]+$")),
    ]
    for c in addr_candidates:
        val = _extract_text_safe(card, c)
        if val:
            address_text = val
            break

    # Dates
    start_date_text = None
    end_date_text = None
    checkin_label = card.get_by_text(re.compile("Check-?in", re.I))
    if checkin_label.count() > 0:
        try:
            sibling = checkin_label.first.locator("xpath=following::*[1]")
            if sibling.count() > 0:
                start_date_text = sibling.first.inner_text().strip()
        except Exception:
            pass

    checkout_label = card.get_by_text(re.compile("Check-?out", re.I))
    if checkout_label.count() > 0:
        try:
            sibling = checkout_label.first.locator("xpath=following::*[1]")
            if sibling.count() > 0:
                end_date_text = sibling.first.inner_text().strip()
        except Exception:
            pass

    # Total price
    total_price_text = None
    price_candidates = [
        card.get_by_text(re.compile("Total", re.I)),
        card.get_by_text(re.compile("Price", re.I)),
        card.get_by_text(re.compile("Paid", re.I)),
        card.locator("[data-testid*='price']"),
    ]
    for c in price_candidates:
        val = _extract_text_safe(card, c)
        if val and re.search(r"\d", val):
            total_price_text = val
            break

    if not (start_date_text and end_date_text and total_price_text):
        return None

    return BookingRaw(
        hotel_name=hotel_name,
        address_text=address_text,
        city_text=city_text,
        country_text=country_text,
        start_date_text=start_date_text,
        end_date_text=end_date_text,
        total_price_text=total_price_text,
    )


@retry(wait=wait_exponential_jitter(initial=1, max=8), stop=stop_after_attempt(3))
def fetch_raw_bookings(email: str, password: str, *, headless: bool = True, debug: bool = False, storage_path: str = ".cache/session.json") -> List[BookingRaw]:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless, slow_mo=100 if debug else 0)
        context = ensure_logged_in(browser, email=email, password=password, storage_path=Path(storage_path), headless=headless)
        page = context.new_page()

        # Try multiple known trips URLs
        found_any = False
        for url in TRIPS_URLS:
            try:
                page.goto(url, wait_until="domcontentloaded")
                _sleep_throttle(0.8, 1.2)
                cards = _find_booking_cards(page)
                if cards:
                    found_any = True
                    break
            except Exception:
                continue

        if not found_any:
            # Stay on current page and attempt to find cards anyway
            cards = _find_booking_cards(page)

        all_cards = cards
        # If there's pagination or lazy-load, click load more a few times
        for _ in range(5):
            if not _click_load_more_if_present(page):
                break
            _sleep_throttle(0.5, 1.0)
            new_cards = _find_booking_cards(page)
            if new_cards:
                all_cards = new_cards

        raw_bookings: List[BookingRaw] = []
        for card in all_cards:
            raw = _extract_booking_from_card(card)
            if raw:
                raw_bookings.append(raw)

        context.close()
        browser.close()

        if not raw_bookings:
            console.print("[yellow]No bookings found. If you have bookings, try --no-headless to assist with human verification or UI changes.")

        return raw_bookings


# Test-only utility to enable snapshot tests without network/Playwright
_TEST_CARD_RE = re.compile(
    r"<div class=\"card\">\s*<h2>(?P<hotel>.*?)</h2>\s*<div class=\"addr\">(?P<addr>.*?)</div>\s*<div class=\"checkin\">Check-in[:\s]*(?P<in>.*?)</div>\s*<div class=\"checkout\">Check-out[:\s]*(?P<out>.*?)</div>\s*<div class=\"total\">Total[:\s]*(?P<total>.*?)</div>",
    re.I | re.S,
)


def extract_bookings_from_html(html: str) -> List[BookingRaw]:
    bookings: List[BookingRaw] = []
    for m in _TEST_CARD_RE.finditer(html):
        bookings.append(
            BookingRaw(
                hotel_name=m.group("hotel").strip(),
                address_text=m.group("addr").strip(),
                city_text=None,
                country_text=None,
                start_date_text=m.group("in").strip(),
                end_date_text=m.group("out").strip(),
                total_price_text=m.group("total").strip(),
            )
        )
    return bookings