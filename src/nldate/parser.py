from __future__ import annotations

from datetime import date, datetime, timedelta
import calendar
import re


WEEKDAYS = {
    "monday": 0,
    "mon": 0,
    "tuesday": 1,
    "tue": 1,
    "tues": 1,
    "wednesday": 2,
    "wed": 2,
    "thursday": 3,
    "thu": 3,
    "thur": 3,
    "thurs": 3,
    "friday": 4,
    "fri": 4,
    "saturday": 5,
    "sat": 5,
    "sunday": 6,
    "sun": 6,
}


NUMBER_WORDS = {
    "a": 1,
    "an": 1,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
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

    # remove periods
    text = text.replace(".", "")

    # normalize commas
    text = re.sub(r"\s*,\s*", ", ", text)

    # normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def parse_number(word: str) -> int:
    if word.isdigit():
        return int(word)

    if word in NUMBER_WORDS:
        return NUMBER_WORDS[word]

    raise ValueError(f"Invalid number: {word}")


def apply_delta(base: date, n: int, unit: str, sign: int) -> date:
    amount = n * sign

    if unit in {"day", "days"}:
        return base + timedelta(days=amount)

    if unit in {"week", "weeks"}:
        return base + timedelta(weeks=amount)

    if unit in {"month", "months"}:
        return add_months(base, amount)

    if unit in {"year", "years"}:
        return add_months(base, amount * 12)

    raise ValueError(f"Invalid unit: {unit}")


def parse(s: str, today: date | None = None) -> date:
    if today is None:
        today = date.today()

    s = clean(s)

    # -----------------------
    # simple keywords
    # -----------------------
    if s == "today":
        return today

    if s == "tomorrow":
        return today + timedelta(days=1)

    if s == "yesterday":
        return today - timedelta(days=1)

    # -----------------------
    # ISO-like dates
    # -----------------------
    if re.fullmatch(r"\d{4}[-/]\d{1,2}[-/]\d{1,2}", s):
        sep = "-" if "-" in s else "/"
        year, month, day = map(int, s.split(sep))
        return date(year, month, day)

    # -----------------------
    # text month formats
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
    # last weekday
    # -----------------------
    m = re.fullmatch(r"last (\w+)", s)

    if m:
        weekday_name = m.group(1)

        if weekday_name in WEEKDAYS:
            target = WEEKDAYS[weekday_name]

            delta_days = (today.weekday() - target) % 7

            if delta_days == 0:
                delta_days = 7

            return today - timedelta(days=delta_days)

    # -----------------------
    # relative to another date
    # -----------------------
    m = re.fullmatch(
        r"(.+?)\s+"
        r"(day|days|week|weeks|month|months|year|years)\s+"
        r"(before|after)\s+(.+)",
        s,
    )

    if m:
        number_text = m.group(1)
        unit = m.group(2)
        direction = m.group(3)
        base_text = m.group(4)

        n = parse_number(number_text)

        base_date = parse(base_text, today)

        sign = 1 if direction == "after" else -1

        return apply_delta(base_date, n, unit, sign)

    # -----------------------
    # split expression parsing
    # -----------------------
    parts = s.split()

    # "in 5 days"
    if len(parts) == 3 and parts[0] == "in":
        n = parse_number(parts[1])
        unit = parts[2]

        return apply_delta(today, n, unit, 1)

    # "5 days ago"
    if len(parts) == 3 and parts[2] == "ago":
        n = parse_number(parts[0])
        unit = parts[1]

        return apply_delta(today, n, unit, -1)

    # "5 days after"
    # "5 days before"
    if len(parts) == 3:
        try:
            n = parse_number(parts[0])
            unit = parts[1]
            direction = parts[2]

            if direction == "after":
                return apply_delta(today, n, unit, 1)

            if direction == "before":
                return apply_delta(today, n, unit, -1)

        except ValueError:
            pass

    raise ValueError(f"Cannot parse: {s}")
