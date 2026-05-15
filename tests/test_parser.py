from datetime import date
from nldate import parse

# Anchor date for all relative tests — Saturday, March 15, 2025
TODAY = date(2025, 3, 15)


# --- Absolute dates ---


def test_absolute_full():
    assert parse("December 1st, 2025") == date(2025, 12, 1)


def test_absolute_numeric_iso():
    assert parse("2025-07-04") == date(2025, 7, 4)


def test_absolute_numeric_slash():
    assert parse("07/04/2025") == date(2025, 7, 4)


def test_absolute_month_day_year():
    assert parse("March 5, 2024") == date(2024, 3, 5)


def test_absolute_ordinal_2nd():
    assert parse("January 2nd, 2026") == date(2026, 1, 2)


def test_absolute_ordinal_3rd():
    assert parse("February 3rd, 2026") == date(2026, 2, 3)


def test_absolute_ordinal_4th():
    assert parse("April 4th, 2025") == date(2025, 4, 4)


# --- Simple relative ---


def test_today():
    assert parse("today", today=TODAY) == date(2025, 3, 15)


def test_tomorrow():
    assert parse("tomorrow", today=TODAY) == date(2025, 3, 16)


def test_yesterday():
    assert parse("yesterday", today=TODAY) == date(2025, 3, 14)


# --- Relative days/weeks/months/years from today ---


def test_in_n_days():
    assert parse("in 3 days", today=TODAY) == date(2025, 3, 18)


def test_n_days_from_today():
    assert parse("5 days from today", today=TODAY) == date(2025, 3, 20)


def test_n_weeks_from_today():
    assert parse("2 weeks from today", today=TODAY) == date(2025, 3, 29)


def test_in_n_weeks():
    assert parse("in 1 week", today=TODAY) == date(2025, 3, 22)


def test_next_month():
    assert parse("next month", today=TODAY) == date(2025, 4, 15)


def test_in_n_months():
    assert parse("in 2 months", today=TODAY) == date(2025, 5, 15)


def test_next_year():
    assert parse("next year", today=TODAY) == date(2026, 3, 15)


# --- Weekday navigation ---


def test_next_tuesday():
    # Today is Saturday Mar 15; next Tuesday = Mar 18
    assert parse("next Tuesday", today=TODAY) == date(2025, 3, 18)


def test_next_friday():
    # Today is Saturday Mar 15; next Friday = Mar 21
    assert parse("next Friday", today=TODAY) == date(2025, 3, 21)


def test_last_monday():
    # Today is Saturday Mar 15; last Monday = Mar 10
    assert parse("last Monday", today=TODAY) == date(2025, 3, 10)


def test_last_wednesday():
    # Today is Saturday Mar 15; last Wednesday = Mar 12
    assert parse("last Wednesday", today=TODAY) == date(2025, 3, 12)


def test_this_sunday():
    # Today is Saturday Mar 15; this Sunday = Mar 16
    assert parse("this Sunday", today=TODAY) == date(2025, 3, 16)


# --- Relative to absolute dates ---


def test_days_before_absolute():
    assert parse("5 days before December 1st, 2025") == date(2025, 11, 26)


def test_days_after_absolute():
    assert parse("10 days after July 4th, 2025") == date(2025, 7, 14)


def test_weeks_before_absolute():
    assert parse("2 weeks before March 1st, 2025") == date(2025, 2, 15)


def test_weeks_after_absolute():
    assert parse("3 weeks after January 1st, 2025") == date(2025, 1, 22)


# --- Compound expressions ---


def test_year_and_months_after_yesterday():
    # yesterday = Mar 14, 2025; +1 year +2 months = May 14, 2026
    assert parse("1 year and 2 months after yesterday", today=TODAY) == date(
        2026, 5, 14
    )


def test_months_and_days_after_absolute():
    assert parse("1 month and 5 days after January 1st, 2025") == date(2025, 2, 6)


def test_years_and_days_from_today():
    assert parse("1 year and 10 days from today", today=TODAY) == date(2026, 3, 25)


# --- Edge cases ---


def test_month_boundary():
    # 20 days after March 20 = April 9
    assert parse("20 days after March 20th, 2025") == date(2025, 4, 9)


def test_leap_year():
    assert parse("February 29th, 2024") == date(2024, 2, 29)


def test_end_of_year():
    assert parse("December 31st, 2025") == date(2025, 12, 31)


def test_start_of_year():
    assert parse("January 1st, 2026") == date(2026, 1, 1)


def test_n_days_ago():
    assert parse("7 days ago", today=TODAY) == date(2025, 3, 8)


def test_n_weeks_ago():
    assert parse("2 weeks ago", today=TODAY) == date(2025, 3, 1)
