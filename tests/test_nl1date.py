from datetime import date
from nldate import parse

TODAY = date(2025, 1, 1)


def test_today():
    assert parse("today", TODAY) == TODAY


def test_tomorrow():
    assert parse("tomorrow", TODAY) == date(2025, 1, 2)


def test_yesterday():
    assert parse("yesterday", TODAY) == date(2024, 12, 31)


def test_5_days_after():
    assert parse("5 days after today", TODAY) == date(2025, 1, 6)


def test_3_days_before():
    assert parse("3 days before today", TODAY) == date(2024, 12, 29)


def test_2_weeks_after():
    assert parse("2 weeks after today", TODAY) == date(2025, 1, 15)


def test_1_year_after():
    assert parse("1 year after today", TODAY) == date(2026, 1, 1)


def test_months_before():
    assert parse("2 months before today", TODAY) == date(2024, 11, 1)


def test_absolute_date():
    assert parse("December 1st, 2025", TODAY) == date(2025, 12, 1)


def test_next_tuesday():
    assert parse("next Tuesday", date(2025, 1, 1)) == date(2025, 1, 7)