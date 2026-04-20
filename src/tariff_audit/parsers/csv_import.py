"""Manual / CSV bill entry.

For bulk analysis or when a PDF parser can't handle a particular bill
layout, users can enter billing data manually via a CSV row or direct
call to :func:`parse_csv_row`.

Expected columns:
    utility, rate_schedule, billing_period_start, billing_period_end,
    billing_days, kwh_consumed, total_amount_due

Optional columns:
    demand_kw, fuel_charge, base_charge, service_address, account_number
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from tariff_audit.parsers.base import ParsedBill


def _parse_date(value: str) -> date:
    """Parse an ISO (YYYY-MM-DD) or US-style (MM/DD/YYYY) date string."""
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%-m/%-d/%Y"):
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date format: {value!r}")


def _decimal(value: Any) -> Decimal | None:
    if value is None or value == "":
        return None
    return Decimal(str(value).replace(",", "").replace("$", "").strip())


def parse_csv_row(row: dict[str, Any]) -> ParsedBill:
    """Parse one dict (e.g. from ``csv.DictReader``) into a :class:`ParsedBill`.

    Raises ``ValueError`` with a clear message when required columns are
    missing or malformed.
    """
    required = [
        "utility", "rate_schedule",
        "billing_period_start", "billing_period_end",
        "kwh_consumed", "total_amount_due",
    ]
    missing = [c for c in required if not row.get(c)]
    if missing:
        raise ValueError(f"CSV row missing required columns: {missing}")

    start = _parse_date(row["billing_period_start"])
    end = _parse_date(row["billing_period_end"])
    if end < start:
        raise ValueError("billing_period_end is before billing_period_start")

    days = int(row.get("billing_days") or (end - start).days + 1)
    kwh = _decimal(row["kwh_consumed"])
    total = _decimal(row["total_amount_due"])
    assert kwh is not None and total is not None  # satisfied by `required` check

    return ParsedBill(
        utility=str(row["utility"]).upper(),
        rate_schedule=str(row["rate_schedule"]).upper(),
        billing_period_start=start,
        billing_period_end=end,
        billing_days=days,
        kwh_consumed=kwh,
        demand_kw=_decimal(row.get("demand_kw")),
        base_charge=_decimal(row.get("base_charge")),
        fuel_charge=_decimal(row.get("fuel_charge")),
        total_amount_due=total,
        account_number=row.get("account_number") or None,
        service_address=row.get("service_address") or None,
        parse_confidence=0.9,  # manual entry is high-confidence but not 1.0
        parse_method="csv",
        raw_text=None,
    )
