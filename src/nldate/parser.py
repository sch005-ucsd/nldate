import re
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

# Weekday name -> weekday number (Monday=0 ... Sunday=6)
_WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}

_MONTH_NAMES = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}


def _today(today: date | None) -> date:
    return today if today is not None else date.today()


def _parse_absolute(s: str) -> date | None:
    """Try to parse a string as an absolute date. Returns None on failure."""
    s = s.strip()

    # ISO format: 2025-07-04
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))

    # YYYY/MM/DD
    m = re.fullmatch(r"(\d{4})/(\d{1,2})/(\d{1,2})", s)
    if m:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))

    # MM/DD/YYYY
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", s)
    if m:
        return date(int(m.group(3)), int(m.group(1)), int(m.group(2)))

    # "Month Day, Year" — e.g. "December 1st, 2025", "March 5, 2024", or "Dec. 1, 2025"
    m = re.fullmatch(
        r"([A-Za-z]+\.?)\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})", s, re.IGNORECASE
    )
    if m:
        month = _MONTH_NAMES.get(m.group(1).lower().rstrip("."))
        if month:
            return date(int(m.group(3)), month, int(m.group(2)))

    return None


def _parse_relative_delta(s: str) -> relativedelta | None:
    """
    Parse a compound delta string like "1 year and 2 months" or "3 weeks and 5 days".
    Returns a relativedelta, or None if the string doesn't match.
    """
    s = s.strip().lower()
    delta = relativedelta()
    found = False

    pattern = re.compile(r"(a|an|\d+)\s+(year|month|week|day)s?")
    for m in pattern.finditer(s):
        n = 1 if m.group(1) in ("a", "an") else int(m.group(1))
        unit = m.group(2)
        found = True
        if unit == "year":
            delta += relativedelta(years=n)
        elif unit == "month":
            delta += relativedelta(months=n)
        elif unit == "week":
            delta += relativedelta(weeks=n)
        elif unit == "day":
            delta += relativedelta(days=n)

    return delta if found else None


def _next_weekday(base: date, wd: int) -> date:
    """Return the next occurrence of weekday `wd` strictly after `base`."""
    days_ahead = (wd - base.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    return base + timedelta(days=days_ahead)


def _last_weekday(base: date, wd: int) -> date:
    """Return the most recent occurrence of weekday `wd` strictly before `base`."""
    days_behind = (base.weekday() - wd) % 7
    if days_behind == 0:
        days_behind = 7
    return base - timedelta(days=days_behind)


def _this_weekday(base: date, wd: int) -> date:
    """
    Return the occurrence of weekday `wd` in the current or upcoming week.
    If today IS that weekday, return today; otherwise return next occurrence.
    """
    days_ahead = (wd - base.weekday()) % 7
    return base + timedelta(days=days_ahead)


def _resolve_anchor(s: str, base: date) -> date | None:
    """Resolve an anchor string that may be a keyword or an absolute date."""
    sl = s.strip().lower()
    if sl == "today":
        return base
    if sl == "tomorrow":
        return base + timedelta(days=1)
    if sl == "yesterday":
        return base - timedelta(days=1)

    result = _parse_absolute(sl.title().replace("'S", "'s"))
    if result:
        return result
    return _parse_absolute(sl)


def parse(s: str, today: date | None = None) -> date:
    """Parse a natural-language date string and return a date object."""
    raw = s.strip()
    lower = raw.lower()
    base = _today(today)

    # --- Simple keywords ---
    if lower == "today":
        return base
    if lower == "tomorrow":
        return base + timedelta(days=1)
    if lower == "yesterday":
        return base - timedelta(days=1)
    if lower == "next month":
        return base + relativedelta(months=1)
    if lower == "last month":
        return base - relativedelta(months=1)
    if lower == "next year":
        return base + relativedelta(years=1)
    if lower == "last year":
        return base - relativedelta(years=1)

    # --- "next/last/this Weekday" ---
    m = re.fullmatch(r"(next|last|this)\s+([a-z]+)", lower)
    if m:
        prefix, day_name = m.group(1), m.group(2)
        wd = _WEEKDAYS.get(day_name)
        if wd is not None:
            if prefix == "next":
                return _next_weekday(base, wd)
            elif prefix == "last":
                return _last_weekday(base, wd)
            else:
                return _this_weekday(base, wd)

    # --- "N units ago" ---
    m = re.fullmatch(r"(.+?)\s+ago", lower)
    if m:
        delta = _parse_relative_delta(m.group(1))
        if delta is not None:
            return base - delta

    # --- "in N units" ---
    m = re.fullmatch(r"in\s+(.+)", lower)
    if m:
        delta = _parse_relative_delta(m.group(1))
        if delta is not None:
            return base + delta

    # --- "N units from today" ---
    m = re.fullmatch(r"(.+?)\s+from\s+today", lower)
    if m:
        delta = _parse_relative_delta(m.group(1))
        if delta is not None:
            return base + delta

    # --- "N units after/before <anchor>" ---
    m = re.search(r"^(.+?)\s+(after|before)\s+(.+)$", lower)
    if m:
        delta_str, direction, anchor_str = m.group(1), m.group(2), m.group(3)
        anchor = _resolve_anchor(anchor_str, base)
        delta = _parse_relative_delta(delta_str)
        if anchor is not None and delta is not None:
            if direction == "after":
                return anchor + delta
            else:
                return anchor - delta

    # --- Pure absolute date ---
    result = _parse_absolute(raw)
    if result is not None:
        return result

    raise ValueError(f"Cannot parse date: {s!r}")
