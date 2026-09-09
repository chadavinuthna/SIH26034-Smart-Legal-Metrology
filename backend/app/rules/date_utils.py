"""Date parsing, calendar arithmetic, and statutory expiry evaluation utilities.

Provides timezone-aware inspection date resolution (default Asia/Kolkata),
flexible date parsing across common Indian and international package formats,
proper calendar-month arithmetic for 'Best Before X Months' declarations,
and comparison against the inspection date.
"""
import calendar
import re
from datetime import date, datetime, timedelta
from typing import Optional, Tuple, Union
from zoneinfo import ZoneInfo
from dateutil import parser
from dateutil.relativedelta import relativedelta

DEFAULT_TIMEZONE = "Asia/Kolkata"

MONTH_NAMES = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dec": 12,
}


def get_current_inspection_date(
    timezone_name: str = DEFAULT_TIMEZONE,
    override: Optional[Union[str, date, datetime]] = None,
) -> date:
    """Return the statutory inspection date in the given timezone (or override if provided)."""
    if override:
        if isinstance(override, datetime):
            return override.date()
        if isinstance(override, date):
            return override
        if isinstance(override, str) and override.strip():
            try:
                return parser.parse(override.strip()).date()
            except Exception:
                pass

    try:
        tz = ZoneInfo(timezone_name)
        return datetime.now(tz).date()
    except Exception:
        return datetime.now().date()


def parse_flexible_date(
    raw_str: Optional[str],
    is_expiry: bool = False,
) -> Tuple[Optional[date], bool]:
    """
    Parse arbitrary date declaration text into a datetime.date object.

    Returns:
        (date_object, is_month_year_only)
        If date string specifies only month and year (e.g. '07/2026' or 'July 2026'):
          - If is_expiry=True, returns the LAST day of that month (valid through month end).
          - If is_expiry=False, returns the FIRST day of that month.
    """
    if not raw_str or not isinstance(raw_str, str):
        return None, False

    text = raw_str.strip()
    if not text:
        return None, False

    # Remove known leading prefixes
    prefix_pattern = re.compile(
        r"^(?:mfg(?:\.?\s*date)?|pkd(?:\.?\s*date)?|packing(?:\s*date)?|manufacture(?:\s*date)?|"
        r"manufactured\s*on|date\s*of\s*(?:manufacture|packing)|dom\b|mfd\b|use\s*by|use\s*before|"
        r"expiry(?:\s*date)?|exp(?:\.?\s*date)?|expires\s*on|best\s*before(?:\s*end)?|best\s*by|bbe\b|"
        r"date)\s*[:\-–]?\s*",
        re.IGNORECASE,
    )
    cleaned = prefix_pattern.sub("", text).strip()

    # Remove trailing preposition phrases e.g. "from manufacture", "from mfg", "from date of packing"
    cleaned = re.sub(r"\s+(?:from|on|at|of)\s+.*$", "", cleaned, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r"^[\[\(\{\'\"]+|[\]\)\}\'\"]+$", "", cleaned).strip()

    # 1. Direct Month/Year format: MM/YYYY, MM-YYYY, MM.YYYY
    my_match = re.match(r"^(\d{1,2})[\/\-\.](\d{4})$", cleaned)
    if my_match:
        m, y = int(my_match.group(1)), int(my_match.group(2))
        if 1 <= m <= 12 and 1990 <= y <= 2100:
            day = calendar.monthrange(y, m)[1] if is_expiry else 1
            return date(y, m, day), True

    # 2. Direct Year/Month format: YYYY/MM, YYYY-MM
    ym_match = re.match(r"^(\d{4})[\/\-\.](\d{1,2})$", cleaned)
    if ym_match:
        y, m = int(ym_match.group(1)), int(ym_match.group(2))
        if 1 <= m <= 12 and 1990 <= y <= 2100:
            day = calendar.monthrange(y, m)[1] if is_expiry else 1
            return date(y, m, day), True

    # 3. Textual Month and Year: e.g. "July 2026", "Jul 2026"
    words = cleaned.split()
    if len(words) == 2:
        w0, w1 = words[0].lower(), words[1].lower()
        if w0 in MONTH_NAMES and re.match(r"^\d{4}$", w1):
            m, y = MONTH_NAMES[w0], int(w1)
            day = calendar.monthrange(y, m)[1] if is_expiry else 1
            return date(y, m, day), True
        if w1 in MONTH_NAMES and re.match(r"^\d{4}$", w0):
            m, y = MONTH_NAMES[w1], int(w0)
            day = calendar.monthrange(y, m)[1] if is_expiry else 1
            return date(y, m, day), True

    # 4. Standard full date parsing (day-first preferred for Indian legal metrology declarations)
    try:
        dt = parser.parse(cleaned, dayfirst=True)
        if 1990 <= dt.year <= 2100:
            return dt.date(), False
    except Exception:
        pass

    # 5. Extract date substring with regex if extra tokens exist around it
    date_sub_match = re.search(
        r"\b(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}|\d{1,2}\s+[a-zA-Z]{3,9}\s+\d{2,4}|[a-zA-Z]{3,9}\s+\d{1,2},?\s+\d{2,4})\b",
        cleaned,
    )
    if date_sub_match:
        try:
            dt = parser.parse(date_sub_match.group(1), dayfirst=True)
            if 1990 <= dt.year <= 2100:
                return dt.date(), False
        except Exception:
            pass

    return None, False


def parse_best_before_duration(raw_str: Optional[str]) -> Optional[Tuple[int, str]]:
    """
    Extract duration amount and unit from declarations like:
    'Best Before 6 Months from Manufacture', '12 Months', '180 Days from Packing'.

    Returns (amount, unit) where unit is 'month', 'day', or 'year'.
    """
    if not raw_str or not isinstance(raw_str, str):
        return None

    m = re.search(r"(\d+)\s*(month|mth|mo|day|d|year|yr)s?\b", raw_str, re.IGNORECASE)
    if m:
        amount = int(m.group(1))
        u = m.group(2).lower()
        if u in ["month", "mth", "mo"]:
            return amount, "month"
        elif u in ["day", "d"]:
            return amount, "day"
        elif u in ["year", "yr"]:
            return amount, "year"

    return None


def compute_derived_best_before(
    base_date: date,
    duration_amount: int,
    duration_unit: str,
    is_base_month_year: bool = False,
) -> date:
    """
    Calculate derived expiry date from a base manufacture/packing date
    using proper calendar-month arithmetic rather than multiplying by 30 days.
    """
    if duration_unit == "month":
        derived = base_date + relativedelta(months=duration_amount)
    elif duration_unit == "day":
        derived = base_date + timedelta(days=duration_amount)
    elif duration_unit == "year":
        derived = base_date + relativedelta(years=duration_amount)
    else:
        return base_date

    if is_base_month_year:
        last_day = calendar.monthrange(derived.year, derived.month)[1]
        return date(derived.year, derived.month, last_day)

    return derived
