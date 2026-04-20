"""Tests for the CSV import and utility auto-detection modules."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from tariff_audit.parsers.csv_import import parse_csv_row
from tariff_audit.parsers.detector import detect_utility, detect_utility_name
from tests.test_parsers.fixtures.fpl_sample_bill import FPL_SAMPLE_BILL_TEXT

# ---------------------------------------------------------------------------
# CSV import
# ---------------------------------------------------------------------------


def test_csv_parses_minimal_row():
    row = {
        "utility": "FPL",
        "rate_schedule": "RS-1",
        "billing_period_start": "2026-01-01",
        "billing_period_end": "2026-01-30",
        "kwh_consumed": "1000",
        "total_amount_due": "136.64",
    }
    parsed = parse_csv_row(row)
    assert parsed.utility == "FPL"
    assert parsed.rate_schedule == "RS-1"
    assert parsed.kwh_consumed == Decimal("1000")
    assert parsed.total_amount_due == Decimal("136.64")
    assert parsed.billing_period_start == date(2026, 1, 1)
    assert parsed.billing_period_end == date(2026, 1, 30)
    assert parsed.billing_days == 30


def test_csv_rejects_missing_required_columns():
    with pytest.raises(ValueError, match="missing required columns"):
        parse_csv_row({"utility": "FPL"})


def test_csv_rejects_reversed_dates():
    with pytest.raises(ValueError, match="before"):
        parse_csv_row({
            "utility": "FPL",
            "rate_schedule": "RS-1",
            "billing_period_start": "2026-02-15",
            "billing_period_end": "2026-01-15",
            "kwh_consumed": "1000",
            "total_amount_due": "100",
        })


def test_csv_strips_currency_symbols():
    row = {
        "utility": "FPL",
        "rate_schedule": "RS-1",
        "billing_period_start": "2026-01-01",
        "billing_period_end": "2026-01-30",
        "kwh_consumed": "1,000",
        "total_amount_due": "$136.64",
    }
    parsed = parse_csv_row(row)
    assert parsed.kwh_consumed == Decimal("1000")
    assert parsed.total_amount_due == Decimal("136.64")


def test_csv_accepts_us_date_format():
    row = {
        "utility": "FPL",
        "rate_schedule": "RS-1",
        "billing_period_start": "01/01/2026",
        "billing_period_end": "01/30/2026",
        "kwh_consumed": "1000",
        "total_amount_due": "136.64",
    }
    parsed = parse_csv_row(row)
    assert parsed.billing_period_start == date(2026, 1, 1)


# ---------------------------------------------------------------------------
# Detector
# ---------------------------------------------------------------------------


def test_detector_identifies_fpl_bill():
    parser = detect_utility(FPL_SAMPLE_BILL_TEXT)
    assert parser is not None
    assert parser.name == "fpl"


def test_detector_returns_none_for_unknown_bill():
    assert detect_utility("This is a Duke Energy bill.") is None


def test_detect_utility_name_shortcut():
    assert detect_utility_name(FPL_SAMPLE_BILL_TEXT) == "FPL"
    assert detect_utility_name("random text") is None
