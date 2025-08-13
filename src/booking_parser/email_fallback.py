from __future__ import annotations

import mailbox
from typing import List

from .models import BookingRaw


def parse_from_mbox(path: str) -> List[BookingRaw]:
    # Minimal placeholder; robust parsing of emails is out of scope for now
    mbox = mailbox.mbox(path)
    results: List[BookingRaw] = []
    for _ in mbox:
        # Future: parse confirmation emails to extract fields
        pass
    return results