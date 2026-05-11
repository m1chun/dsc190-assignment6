from __future__ import annotations

from datetime import date, datetime, timedelta
import calendar
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


def add_months(d: date, months: int) -> date:
    month = d.month - 1 + months
    year = d.year + month // 12
    month = month % 12 + 1

    max_day = calendar.monthrange(year, month)[1]
    day = min(d.day, max_day)

    return date(year, month, day)


def clean(text: str) -> str:
    text = text.lower().strip()

    # remove ordinal suffixes
    text = re.sub(r"(\d)(st|nd|rd|th)", r"\1", text)

    # remove periods in month abbreviations
    text = text.replace(".", "")

    # normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text


def parse(s: str, today: date | None = None) -> date:
    if today is None:
        today = date.today()

    s = clean(s)

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
    # ISO-like formats
    # -----------------------
    if re.fullmatch(r"\d{4}[-/]\d{1,2}[-/]\d{1,2}", s):
        sep = "-" if "-" in s else "/"
        year, month, day = map(int, s.split(sep))
        return date(year, month, day)

    # -----------------------
    # absolute text dates
    # -----------------------
    date_formats = [
        "%b %d, %Y",
        "%B %d, %Y",
        "%b %d %Y",
        "%B %d %Y",
    ]

    for fmt in date_formats:
        try:
            return datetime.strptime(s.title(), fmt).date()
        except ValueError:
            pass

    # -----------------------
    # next weekday
    # -----------------------
    m = re.fullmatch(r"next (\w+)", s)

    if m:
        weekday_name = m.group(1)

        if weekday_name in WEEKDAYS:
            target = WEEKDAYS[weekday_name]

            delta_days = (target - today.weekday()) % 7

            if delta_days == 0:
                delta_days = 7

            return today + timedelta(days=delta_days)

    # -----------------------
    # relative expressions
    # examples:
    # 5 days after today
    # 2 weeks before today
    # in 5 days
    # 3 months ago
    # -----------------------

    # in 5 days
    m = re.fullmatch(
        r"in (\d+) (day|days|week|weeks|month|months|year|years)",
        s,
    )

    if m:
        amount = int(m.group(1))
        unit = m.group(2)

        direction = 1

    else:
        # 5 days after today
        m = re.fullmatch(
            r"(\d+) (day|days|week|weeks|month|months|year|years) "
            r"(after|before) today",
            s,
        )

        if m:
            amount = int(m.group(1))
            unit = m.group(2)
            direction = 1 if m.group(3) == "after" else -1

        else:
            # 5 days ago
            m = re.fullmatch(
                r"(\d+) (day|days|week|weeks|month|months|year|years) ago",
                s,
            )

            if m:
                amount = int(m.group(1))
                unit = m.group(2)
                direction = -1
            else:
                raise ValueError(f"Cannot parse: {s}")

    amount *= direction

    # apply unit
    if unit in {"day", "days"}:
        return today + timedelta(days=amount)

    if unit in {"week", "weeks"}:
        return today + timedelta(weeks=amount)

    if unit in {"month", "months"}:
        return add_months(today, amount)

    if unit in {"year", "years"}:
        try:
            return today.replace(year=today.year + amount)
        except ValueError:
            # Feb 29 handling
            return today.replace(
                year=today.year + amount,
                month=2,
                day=28,
            )

    raise ValueError(f"Cannot parse: {s}")
