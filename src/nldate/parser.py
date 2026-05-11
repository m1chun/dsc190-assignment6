from __future__ import annotations

from datetime import date, timedelta
import re


WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def parse(s: str, today: date | None = None) -> date:
    if today is None:
        today = date.today()

    s = s.lower().strip()
    parts = s.split()

    # -----------------------
    # ISO variants: 2025/12/04
    # -----------------------
    try:
        if "/" in s:
            parts = s.split("/")
            if len(parts) == 3:
                y, m, d = map(int, parts)
                return date(y, m, d)
    except ValueError:
        pass

    # -----------------------
    # YYYY/MM/DD format
    # -----------------------
    if "/" in s:
        parts = s.split("/")
        if len(parts) == 3:
            y, m, d = map(int, parts)
            return date(int(y), int(m), int(d))

    # -----------------------
    # keywords
    # -----------------------
    if s == "today":
        return today
    if s == "tomorrow":
        return today + timedelta(days=1)
    if s == "yesterday":
        return today - timedelta(days=1)

    # -----------------------
    # relative days
    # -----------------------
    if "days" in s:
        n = int(parts[0])
        if "after" in s:
            return today + timedelta(days=n)
        if "before" in s:
            return today - timedelta(days=n)

    # -----------------------
    # relative weeks
    # -----------------------
    if "weeks" in s:
        n = int(parts[0])
        if "after" in s:
            return today + timedelta(weeks=n)
        if "before" in s:
            return today - timedelta(weeks=n)

    # -----------------------
    # years
    # -----------------------
    if "year" in s:
        n = int(parts[0])
        if "after" in s:
            return today.replace(year=today.year + n)
        if "before" in s:
            return today.replace(year=today.year - n)

    # -----------------------
    # months (approx)
    # -----------------------
    if "month" in s:
        n = int(parts[0])
        delta = n if "after" in s else -n

        month = today.month + delta
        year = today.year + (month - 1) // 12
        month = (month - 1) % 12 + 1

        day = min(today.day, 28)
        return date(year, month, day)

    # -----------------------
    # next weekday
    # -----------------------
    if s.startswith("next "):
        day_name = s.replace("next ", "")
        target = WEEKDAYS[day_name]

        delta = (target - today.weekday() + 7) % 7
        if delta == 0:
            delta = 7

        return today + timedelta(days=delta)

    # -----------------------
    # absolute format: "December 1st, 2025"
    # -----------------------
    def clean(text: str) -> str:
        return re.sub(r"(st|nd|rd|th)", "", text)

    try:
        return date.fromisoformat(s)
    except ValueError:
        pass

    try:
        from datetime import datetime

        return datetime.strptime(clean(s), "%B %d, %Y").date()
    except ValueError:
        pass

    # -----------------------
    # failure case
    # -----------------------
    raise ValueError(f"Cannot parse: {s}")
