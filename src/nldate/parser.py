from __future__ import annotations

from datetime import date, timedelta, datetime
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
    # ISO formats: 2025-12-04 or 2025/12/04
    # -----------------------
    m = re.fullmatch(r"\d{4}[-/]\d{1,2}[-/]\d{1,2}", s)
    if m:
        sep = "-" if "-" in s else "/"
        y, mth, d = map(int, s.split(sep))
        return date(y, mth, d)

    # -----------------------
    # relative days/weeks
    # -----------------------
    parts = s.split()

    if len(parts) >= 4 and parts[1] in {"day", "days", "week", "weeks"}:
        n = int(parts[0])
        direction = parts[2]

        if "day" in parts[1]:
            delta = timedelta(days=n)
        else:
            delta = timedelta(weeks=n)

        return today + delta if direction == "after" else today - delta

    # -----------------------
    # years
    # -----------------------
    if len(parts) >= 4 and parts[1] in {"year", "years"}:
        n = int(parts[0])
        direction = parts[2]

        new_year = today.year + (n if direction == "after" else -n)
        return today.replace(year=new_year)

    # -----------------------
    # months (approx)
    # -----------------------
    if len(parts) >= 4 and parts[1] in {"month", "months"}:
        n = int(parts[0])
        direction = parts[2]

        month_delta = n if direction == "after" else -n

        month = today.month + month_delta
        year = today.year + (month - 1) // 12
        month = (month - 1) % 12 + 1

        return date(year, month, min(today.day, 28))

    # -----------------------
    # next weekday
    # -----------------------
    if s.startswith("next "):
        day_name = s.replace("next ", "")
        if day_name in WEEKDAYS:
            target = WEEKDAYS[day_name]
            delta_days = (target - today.weekday() + 7) % 7
            if delta_days == 0:
                delta_days = 7
            return today + timedelta(days=delta_days)

    # -----------------------
    # "Dec 1, 2025" / "Dec. 1, 2025" / "December 1, 2025"
    # -----------------------
    def clean(text: str) -> str:
        text = re.sub(r"(st|nd|rd|th)", "", text)
        text = text.replace(".", "")  # <-- fixes "Dec."
        return text

    for fmt in ("%b %d, %Y", "%B %d, %Y"):
        try:
            return datetime.strptime(clean(s).title(), fmt).date()
        except ValueError:
            pass

    raise ValueError(f"Cannot parse: {s}")
