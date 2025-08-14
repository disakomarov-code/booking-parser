from __future__ import annotations

import json
import os
import time
import re
from pathlib import Path
from typing import Optional

from playwright.sync_api import Browser, BrowserContext, Page, TimeoutError as PlaywrightTimeoutError

LOGIN_URLS = [
    "https://account.booking.com/sign-in",
    "https://secure.booking.com/book.html?op=login",
]

HOME_URL = "https://www.booking.com/"
TRIPS_URLS = [
    "https://www.booking.com/trips",
    "https://secure.booking.com/myreservations.en-gb.html",
]


class LoginError(RuntimeError):
    pass


def _ensure_cache_dir(cache_path: Path) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)


def _looks_logged_in(page: Page) -> bool:
    # Heuristic: no "Sign in" link visible
    try:
        sign_in = page.get_by_role("link", name=lambda n: n and "sign in" in n.lower())
        if sign_in.is_visible():
            return False
    except Exception:
        pass

    # Another hint: user avatar/menu exists
    try:
        acc = page.get_by_role("button", name=lambda n: n and ("account" in n.lower() or "profile" in n.lower()))
        if acc.is_visible():
            return True
    except Exception:
        pass

    # Fallback: presence of trips page specific anchors
    try:
        page.wait_for_load_state("networkidle", timeout=2000)
    except Exception:
        pass
    content = page.content()
    return "trips" in content.lower() or "my reservations" in content.lower()


def open_context_with_storage(browser: Browser, storage_path: Optional[Path]) -> BrowserContext:
    if storage_path and storage_path.exists():
        return browser.new_context(storage_state=str(storage_path))
    return browser.new_context()


def perform_login(page: Page, email: str, password: str, headless: bool) -> None:
    # Two-step login flow: email then password
    page.goto(LOGIN_URLS[0], wait_until="domcontentloaded")

    # Email step
    email_field_candidates = [
        page.get_by_label("Email"),
        page.get_by_label("Email address"),
        page.get_by_placeholder("Email address"),
        page.locator("input[name=\"username\"]"),
        page.locator("input[type=email]")
    ]
    for locator in email_field_candidates:
        try:
            if locator.count() > 0:
                locator.first.fill(email)
                break
        except Exception:
            continue
    else:
        raise LoginError("Could not find email field on login page")

    # Continue or Next
    try:
        cont = page.get_by_role("button", name=lambda n: n and ("continue" in n.lower() or "next" in n.lower()))
        if cont.count() > 0:
            cont.first.click()
    except Exception:
        pass

    # Password step
    page.wait_for_timeout(500)
    pwd_candidates = [
        page.get_by_label("Password"),
        page.locator("input[name=\"password\"]"),
        page.locator("input[type=password]")
    ]
    for locator in pwd_candidates:
        try:
            if locator.count() > 0:
                locator.first.fill(password)
                break
        except Exception:
            continue
    else:
        raise LoginError("Could not find password field on login page")

    # Submit
    submit_candidates = [
        page.get_by_role("button", name=lambda n: n and ("sign in" in n.lower() or "log in" in n.lower() or "continue" in n.lower())),
        page.locator("button[type=submit]")
    ]
    for locator in submit_candidates:
        try:
            if locator.count() > 0:
                locator.first.click()
                break
        except Exception:
            continue

    # Wait and detect possible human verification
    try:
        page.wait_for_url(re.compile(r"booking\.com/(trips|home|index|my.*)"), timeout=15000)  # type: ignore
    except Exception:
        # If still on login, we might be blocked by CAPTCHA or 2FA
        if headless:
            raise LoginError(
                "Login may require CAPTCHA/2FA. Re-run with --no-headless to complete verification."
            )
        else:
            # Allow manual interaction
            page.wait_for_timeout(20000)

    # Give a moment for cookies to settle
    page.goto(HOME_URL, wait_until="domcontentloaded")


def ensure_logged_in(browser: Browser, email: str, password: str, storage_path: Path, headless: bool) -> BrowserContext:
    _ensure_cache_dir(storage_path)

    # Try existing session
    context = open_context_with_storage(browser, storage_path)
    page = context.new_page()
    try:
        page.goto(HOME_URL, wait_until="domcontentloaded")
        if _looks_logged_in(page):
            # Refresh storage state
            context.storage_state(path=str(storage_path))
            return context
    except Exception:
        pass
    finally:
        try:
            page.close()
        except Exception:
            pass
        try:
            context.close()
        except Exception:
            pass

    # Perform fresh login
    context = browser.new_context()
    page = context.new_page()
    perform_login(page, email=email, password=password, headless=headless)

    # Persist storage state
    context.storage_state(path=str(storage_path))
    return context