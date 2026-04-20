"""Tests for FAC-derived billing mechanics constants and helpers."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from tariff_audit.standards.billing_mechanics import (
    ACTUAL_METER_READ_REQUIRED_EVERY_MONTHS,
    MAX_BACKBILLING_MONTHS,
    METER_ACCURACY_LOWER_BOUND,
    METER_ACCURACY_UPPER_BOUND,
    METER_TOLERANCE_PCT,
    NET_METERING_CREDIT_CARRYOVER_MONTHS,
    OVER_REGISTERING_METER_MAX_REFUND_MONTHS,
    back_billing_cutoff_date,
    is_meter_within_tolerance,
    meter_error_refund_period,
)


def test_fac_25_6_106_backbilling_is_twelve_months():
    assert MAX_BACKBILLING_MONTHS == 12


def test_fac_25_6_103_meter_error_cap_is_twelve_months():
    assert OVER_REGISTERING_METER_MAX_REFUND_MONTHS == 12


def test_fac_25_6_052_meter_tolerance_is_two_percent():
    assert Decimal("2.0") == METER_TOLERANCE_PCT
    assert Decimal("0.98") == METER_ACCURACY_LOWER_BOUND
    assert Decimal("1.02") == METER_ACCURACY_UPPER_BOUND


def test_fac_25_6_099_actual_meter_read_cadence_is_six_months():
    assert ACTUAL_METER_READ_REQUIRED_EVERY_MONTHS == 6


def test_fac_25_6_065_net_metering_carryover_is_twelve_months():
    assert NET_METERING_CREDIT_CARRYOVER_MONTHS == 12


def test_back_billing_cutoff_subtracts_twelve_months():
    assert back_billing_cutoff_date(date(2026, 4, 15)) == date(2025, 4, 15)


def test_meter_error_refund_period_is_half_since_last_test():
    """365-day gap → refund for ~182 days (half)."""
    last_test = date(2024, 1, 1)
    discovery = date(2025, 1, 1)  # 365 or 366 days later
    period = meter_error_refund_period(last_test, discovery)
    assert 180 <= period.days <= 183


def test_meter_error_refund_period_caps_at_twelve_months():
    """A 5-year-old meter with a fresh discovery must not refund 2.5 years."""
    last_test = date(2020, 1, 1)
    discovery = date(2026, 1, 1)
    period = meter_error_refund_period(last_test, discovery)
    # Must cap around 12 months (approx 365 days as the rule applies it)
    assert period.days <= 366


def test_meter_error_refund_period_rejects_reversed_dates():
    with pytest.raises(ValueError):
        meter_error_refund_period(date(2026, 1, 1), date(2024, 1, 1))


def test_is_meter_within_tolerance():
    # Exactly on bounds → within
    assert is_meter_within_tolerance(Decimal("98.0")) is True
    assert is_meter_within_tolerance(Decimal("102.0")) is True
    assert is_meter_within_tolerance(Decimal("100.0")) is True
    # Just outside → not within
    assert is_meter_within_tolerance(Decimal("97.9")) is False
    assert is_meter_within_tolerance(Decimal("102.1")) is False
