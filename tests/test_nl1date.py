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


def test_slash_date():
    assert parse("2025/12/04") == date(2025, 12, 4)


def test_short_month():
    assert parse("Dec 1, 2025") == date(2025, 12, 1)


def test_short_month_period():
    assert parse("Dec. 1, 2025") == date(2025, 12, 1)


def test_in_days():
    assert parse("in 5 days", date(2025, 1, 1)) == date(2025, 1, 6)


def test_days_ago():
    assert parse("5 days ago", date(2025, 1, 10)) == date(2025, 1, 5)


def test_a_week_ago():
    assert parse("a week ago", date(2025, 1, 10)) == date(2025, 1, 3)


def test_next_friday():
    assert parse("next friday", date(2025, 1, 1)) == date(2025, 1, 3)


def test_single_digit_date():
    assert parse("2025/12/3") == date(2025, 12, 3)
